import asyncio
import json
import plistlib
from dataclasses import dataclass
from sys import argv
from typing import Any, Dict, List, Tuple, Union
from urllib.parse import quote

from aiohttp import ClientSession


@dataclass(frozen=True, eq=True)
class GitHubLocation:
    owner: str
    repo: str
    path: str
    ref: str

    @classmethod
    def from_json(cls, json: Dict[str, str]) -> "GitHubLocation":
        return cls(json["owner"], json["repo"], json["path"], json["ref"])


@dataclass
class Language:
    name: str
    language_id: str
    grammar_uri: Union[GitHubLocation, List[GitHubLocation], None]
    file_extensions: List[str]


async def generate_permalink_github(client: ClientSession, location: GitHubLocation) -> str:
    async with client.get(f"/repos/{location.owner}/{location.repo}/git/ref/{location.ref}") as response:
        res = await response.json()
    commit_sha = res['object']['sha']
    path = quote(f"{location.owner}/{location.repo}/{commit_sha}/{location.path}")
    return f"https://raw.githubusercontent.com/{path}"


async def get_grammar_scope(client: ClientSession, url: str) -> str:
    async with client.get(url) as response:
        if url.endswith(".json"):
            grammar = json.loads(await response.text())
        else:
            grammar = plistlib.loads((await response.text()).encode(), fmt=plistlib.FMT_XML)
    return grammar["scopeName"]


def list_locations(languages: Dict[str, Any]) -> List[GitHubLocation]:
    raw: List[Dict[str, Any]] = []
    for l in languages.values():
        raw.append(l["grammarLocation"])
        if embedded_grammars := l.get("embeddedGrammars"):
            raw += embedded_grammars

    out: List[GitHubLocation] = []
    for l in raw:
        if not l["type"] == "github":
            raise ValueError("Location type not supported: " + l["type"])
        out.append(GitHubLocation.from_json(l))

    return out


async def locations_to_urls(locations: List[GitHubLocation], token: str) -> List[str]:
    async with ClientSession("https://api.github.com/", headers={"Authorization": "Bearer " + token}) as client:
        requests = [generate_permalink_github(client, location) for location in locations]
        return await asyncio.gather(*requests)


async def urls_to_scopes(urls: List[str], token: str) -> List[str]:
    async with ClientSession(headers={"Authorization": "Bearer " + token}) as client:
        requests = [get_grammar_scope(client, url) for url in urls]
        return await asyncio.gather(*requests)


async def generate_scope_maps(languages: Dict[str, Any], token: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    locations = list_locations(languages)
    urls = await locations_to_urls(locations, token)
    scopes = await urls_to_scopes(urls, token)

    location_to_scope = dict(zip(locations, scopes))

    language_id_to_scope: Dict[str, str] = {}
    for id, lang in languages.items():
        location = GitHubLocation.from_json(lang["grammarLocation"])
        language_id_to_scope[id] = location_to_scope[location]

    scope_to_grammar = dict(zip(scopes, urls))

    return (language_id_to_scope, scope_to_grammar)


language_priorities: Dict[str, int] = {
    "c": 100,
    "cpp": 200,
    "coffeescript": 200,
    "csharp": 100,
    "fsharp": 200,
    "glsl": 100,
    "razor": 200,
    "sdl": 100,
    "sml": 200,
    "genie": 200,
    "glsl": 100
}


def update_extension_map(mapping: Dict[str, str], language_id: str, extension: str) -> None:
    current_id = mapping.get(extension)
    if current_id:
        priority_current = language_priorities.get(current_id)
        priority_new = language_priorities.get(language_id)
        if priority_current is None or priority_new is None:
            raise ValueError(
                f"Priorities for language ids {current_id} and {language_id} required, because of extension '{extension}'")
        if priority_current >= priority_new:
            return
    mapping[extension] = language_id


def generate_extension_map(languages: Dict[str, Any]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for id, val in languages.items():
        for e in val["extensions"]:
            update_extension_map(mapping, id, e)
    return mapping


def generate_languages_py(extension_to_language_id: Dict[str, str], language_id_to_scope: Dict[str, str], scope_to_grammar: Dict[str, str]) -> str:
    extension_to_language_id_str = "\n".join(f'    "{key}": "{val}",' for key, val in extension_to_language_id.items())
    language_id_to_scope_str = "\n".join(f'    "{key}": "{val}",' for key, val in language_id_to_scope.items())
    scope_to_grammar_str = "\n".join(
        f'    "{key}": BuiltInGrammar("{key}", "{val}"),' for key, val in scope_to_grammar.items())

    return f"""\
from typing import Dict
from .tokens.grammar import Grammar, BuiltInGrammar


extension_to_language_id = {{
{extension_to_language_id_str}
}}


language_id_to_scope = {{
{language_id_to_scope_str}
}}


scope_to_grammar: Dict[str, Grammar] = {{
{scope_to_grammar_str}
}}
"""


async def main() -> None:
    with open("../res/languages.json") as file:
        languages = json.load(file)

    with open("github-token") as file:
        token = file.read().strip()

    language_id_to_scope, scope_to_grammar = await generate_scope_maps(languages, token)

    extension_to_language_id = generate_extension_map(languages)

    out_str = generate_languages_py(extension_to_language_id, language_id_to_scope, scope_to_grammar)
    with open(argv[1], "w") as file:
        file.write(out_str)

    await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
