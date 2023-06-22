from pathlib import Path

import pytest

from lspscript.client import StdIOConnectionParams
from lspscript.location_list import LocationList
from lspscript.types.structures import Location, Position, Range
from lspscript.workspace import Workspace


async def test_location_list_iteration() -> None:
    async with Workspace(Path("./test/mock-ws-1")) as ws:
        doc1 = ws.open_text_document(Path("test-1.py"))
        doc2 = ws.open_text_document(Path("test-2.py"), encoding="utf-8")
        location_list = LocationList([doc1, doc2], [
            [(0, 5)],
            [(0, 3), (4, 8)]
        ])

        doc1.close()
        doc2.close()
        assert not doc1.is_closed()  # LocationList should keep the documents open
        assert not doc2.is_closed()

        with location_list:
            assert len(location_list) == 2
            items = iter(location_list.items())

            doc, locations = next(items)
            assert doc is doc1
            assert len(locations) == 1
            assert locations[0] == (0, 5)

            doc, locations = next(items)
            assert doc is doc2
            assert len(locations) == 2
            assert locations[0] == (0, 3)
            assert locations[1] == (4, 8)

            assert next(items, None) is None

        assert len(location_list) == 0
        assert doc1.is_closed()
        assert doc2.is_closed()


@pytest.mark.filterwarnings("ignore::lspscript.text_document.DroppedChangesWarning")
async def test_location_list_document_edits() -> None:
    async with Workspace(Path("./test/mock-ws-1")) as ws:
        doc1 = ws.open_text_document(Path("test-1.py"))
        doc2 = ws.open_text_document(Path("test-2.py"), encoding="utf-8")
        location_list = LocationList([doc1, doc2], [
            [(0, 5)],
            [(0, 3), (4, 8)]
        ])

        for doc in location_list:
            for start, end in location_list[doc]:
                doc.edit("test", start, end)
            doc.commit_edits()
            with pytest.raises(KeyError):
                location_list[doc]

        assert len(location_list) == 0
        assert doc1.text == 'test("Hello, World!")\n'
        assert doc2.text == """\
test test():
    print("∂ϕ")
    print("𐐀𐐐")


if __name__ == "__main__":
    main()
"""


async def test_location_list_from_lsp_locations() -> None:
    workspace_path = Path("./test/mock-ws-1").resolve()
    workspace_uri = workspace_path.as_uri()
    async with Workspace(workspace_path) as ws:
        params = StdIOConnectionParams(
            launch_command=f"node ./mock-server/out/index.js --stdio test/test_empty.json")
        client = await ws.launch_client(params)
        await client.send_request("$/setTemplateParams", {"expand": {"WORKSPACE_URI": workspace_uri}})
        doc1_uri = (workspace_path / Path("test-1.py")).as_uri()
        lsp_locations = [
            Location(uri=doc1_uri,
                     range=Range(start=Position(line=0, character=0),
                                 end=Position(line=0, character=5))),
            Location(uri=doc1_uri,
                     range=Range(start=Position(line=0, character=6),
                                 end=Position(line=0, character=8))),
        ]

        locations = LocationList.from_lsp_locations(ws, lsp_locations)

        assert len(locations) == 1

        assert len(locations[doc1_uri]) == 2
        assert locations[doc1_uri][0] == (0, 5)
        assert locations[doc1_uri][1] == (6, 8)
