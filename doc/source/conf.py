project = "LSPScript"
author = "Jonas Rinke"
copyright = "2023, Jonas Rinke"
html_theme = "piccolo_theme"

extensions = [
    "sphinx.ext.autodoc",
    "autodoc2",
    "sphinx_autodoc_typehints",
    "myst_parser"
]

autodoc2_packages = [
    {
        "path": "../../lspscript/types/",
        "module": "lspsript.types",
        "exclude_files": ["capabilities.py", "client_requests.py", "lsp_enum.py", "util.py"]
    }
]

autodoc2_docstring_parser_regexes = [
    (r"lspscript\.types\..*", "myst")
]

autodoc2_hidden_objects = ["private"]
autodoc2_hidden_regexes = [
    r".*\.from_json",
    r".*\.to_json"
]

simplify_optional_unions = False
typehints_document_rtype = False
typehints_use_signature_return = True

myst_enable_extensions = [
    "fieldlist"
]
