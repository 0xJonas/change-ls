from typing import Dict
from .tokens.grammar import Grammar, BuiltInGrammar


extension_to_language_id = {
    ".as": "actionscript",
    ".bat": "bat",
    ".cmd": "bat",
    ".bib": "bibtex",
    ".clj": "clojure",
    ".boot": "clojure",
    ".cl2": "clojure",
    ".cljc": "clojure",
    ".cljs": "clojure",
    ".cljs.hl": "clojure",
    ".cljscm": "clojure",
    ".cljx": "clojure",
    ".hic": "clojure",
    ".coffee": "coffeescript",
    "._coffee": "coffeescript",
    ".cake": "coffeescript",
    ".cjsx": "coffeescript",
    ".cson": "coffeescript",
    ".iced": "coffeescript",
    ".c": "c",
    ".cats": "c",
    ".h": "cpp",
    ".idc": "c",
    ".w": "c",
    ".cpp": "cpp",
    ".c++": "cpp",
    ".cc": "cpp",
    ".cp": "cpp",
    ".cxx": "cpp",
    ".h++": "cpp",
    ".hh": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".inc": "cpp",
    ".inl": "cpp",
    ".ipp": "cpp",
    ".tcc": "cpp",
    ".tpp": "cpp",
    ".cr": "crystal",
    ".ecr": "ecr",
    ".slang": "slang",
    ".cs": "csharp",
    ".cshtml": "razor",
    ".csx": "csharp",
    ".css": "css",
    ".d": "d",
    ".di": "d",
    ".dpp": "dpp",
    ".d++": "dpp",
    ".dscript": "dscript",
    ".ds": "dscript",
    ".dml": "dml",
    ".sml": "sml",
    ".dt": "diet",
    ".dart": "dart",
    ".diff": "diff",
    ".patch": "diff",
    "dockerfile": "dockerfile",
    ".ex": "elixir",
    ".exs": "elixir",
    ".eex": "eex",
    ".leex": "eex",
    ".heex": "eex",
    ".html.eex": "html-eex",
    ".html.leex": "html-eex",
    ".html.heex": "html-eex",
    ".elm": "elm",
    ".erl": "erlang",
    ".es": "erlang",
    ".escript": "erlang",
    ".hrl": "erlang",
    ".xrl": "erlang",
    ".yrl": "erlang",
    ".fs": "fsharp",
    ".fsi": "fsharp",
    ".fsx": "fsharp",
    ".f90": "FortranFreeForm",
    ".F90": "FortranFreeForm",
    ".f95": "FortranFreeForm",
    ".F95": "FortranFreeForm",
    ".f03": "FortranFreeForm",
    ".F03": "FortranFreeForm",
    ".f08": "FortranFreeForm",
    ".F08": "FortranFreeForm",
    ".f18": "FortranFreeForm",
    ".F18": "FortranFreeForm",
    ".fpp": "FortranFreeForm",
    ".FPP": "FortranFreeForm",
    ".pf": "FortranFreeForm",
    ".PF": "FortranFreeForm",
    ".fypp": "FortranFreeForm",
    ".FYPP": "FortranFreeForm",
    ".f": "FortranFixedForm",
    ".F": "FortranFixedForm",
    ".f77": "FortranFixedForm",
    ".F77": "FortranFixedForm",
    ".for": "FortranFixedForm",
    ".FOR": "FortranFixedForm",
    ".gs": "genie",
    ".gleam": "gleam",
    ".vs": "glsl",
    ".vsf": "glsl",
    ".fsh": "glsl",
    ".gsh": "glsl",
    ".vshader": "glsl",
    ".fshader": "glsl",
    ".gshader": "glsl",
    ".comp": "glsl",
    ".vert": "glsl",
    ".tesc": "glsl",
    ".tese": "glsl",
    ".frag": "glsl",
    ".geom": "glsl",
    ".glsl": "glsl",
    ".glslv": "glsl",
    ".glslf": "glsl",
    ".glslg": "glsl",
    ".go": "go",
    ".gql": "graphql",
    ".graphql": "graphql",
    ".graphqls": "graphql",
    ".gr": "grain",
    ".groovy": "groovy",
    ".gvy": "groovy",
    ".gradle": "groovy",
    ".jenkinsfile": "groovy",
    ".nf": "groovy",
    ".handlebars": "handlebars",
    ".hbs": "handlebars",
    ".hjs": "handlebars",
    ".hx": "haxe",
    ".hlsl": "hlsl",
    ".hlsli": "hlsl",
    ".fx": "hlsl",
    ".fxh": "hlsl",
    ".vsh": "hlsl",
    ".psh": "hlsl",
    ".cginc": "hlsl",
    ".compute": "hlsl",
    ".html": "html",
    ".htm": "html",
    ".shtml": "html",
    ".xhtml": "html",
    ".xht": "html",
    ".mdoc": "html",
    ".jsp": "html",
    ".asp": "html",
    ".aspx": "html",
    ".jshtm": "html",
    ".volt": "html",
    ".ejs": "html",
    ".rhtml": "html",
    ".hxml": "hxml",
    ".ini": "ini",
    ".pug": "jade",
    ".jade": "jade",
    ".java": "java",
    ".jav": "java",
    ".js": "javascript",
    ".es6": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".pac": "javascript",
    ".jsx": "javascriptreact",
    ".json": "json",
    ".bowerrc": "json",
    ".jscsrc": "json",
    ".webmanifest": "json",
    ".js.map": "json",
    ".css.map": "json",
    ".ts.map": "json",
    ".har": "json",
    ".jslintrc": "json",
    ".jsonld": "json",
    ".geojson": "json",
    ".ipynb": "json",
    ".jsonc": "jsonc",
    ".eslintrc": "jsonc",
    ".eslintrc.json": "jsonc",
    ".jsfmtrc": "jsonc",
    ".jshintrc": "jsonc",
    ".swcrc": "jsonc",
    ".hintrc": "jsonc",
    ".babelrc": "jsonc",
    ".jl": "julia",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".tex": "latex",
    ".ltx": "latex",
    ".ctx": "latex",
    ".less": "less",
    ".log": "log",
    ".lua": "lua",
    ".mk": "makefile",
    ".mak": "makefile",
    "Makefile": "makefile",
    "makefile": "makefile",
    "GNUMakefile": "makefile",
    "OCamlMakefile": "makefile",
    ".md": "markdown",
    ".mkd": "markdown",
    ".mdwn": "markdown",
    ".mdown": "markdown",
    ".markdown": "markdown",
    ".markdn": "markdown",
    ".mdtxt": "markdown",
    ".mdtext": "markdown",
    ".workbook": "markdown",
    ".nim": "nim",
    ".nims": "nim",
    "nim.cfg": "nim",
    ".nim.cfg": "nim",
    ".nimble": "nimble",
    ".ml": "ocaml",
    ".eliom": "ocaml",
    ".ocamlinit": "ocaml",
    ".mll": "ocaml.ocamllex",
    ".m": "objective-c",
    ".mm": "objective-cpp",
    ".pl": "perl",
    ".pm": "perl",
    ".pod": "perl",
    ".t": "perl",
    ".PL": "perl",
    ".psgi": "perl",
    ".p6": "perl6",
    ".pl6": "perl6",
    ".pm6": "perl6",
    ".nqp": "perl6",
    ".php": "php",
    ".php4": "php",
    ".php5": "php",
    ".phtml": "php",
    ".ctp": "php",
    ".ps1": "powershell",
    ".psm1": "powershell",
    ".psd1": "powershell",
    ".pssc": "powershell",
    ".psrc": "powershell",
    ".purs": "purescript",
    ".py": "python",
    ".rpy": "python",
    ".pyw": "python",
    ".cpy": "python",
    ".gyp": "python",
    ".gypi": "python",
    ".pyi": "python",
    ".ipy": "python",
    ".pyt": "python",
    ".r": "r",
    ".rhistory": "r",
    ".rprofile": "r",
    ".rt": "r",
    ".rkt": "racket",
    ".raml": "raml",
    ".razor": "razor",
    ".re": "reason",
    ".rei": "reason",
    ".res": "rescript",
    ".resi": "rescript",
    ".rst": "restructuredtext",
    ".rb": "ruby",
    ".rbx": "ruby",
    ".rjs": "ruby",
    ".gemspec": "ruby",
    ".rake": "ruby",
    ".ru": "ruby",
    ".erb": "ruby",
    ".podspec": "ruby",
    ".rbi": "ruby",
    ".rs": "rust",
    ".scala": "scala",
    ".sbt": "scala",
    ".sc": "scala",
    ".scss": "scss",
    ".shader": "shaderlab",
    ".sh": "shellscript",
    ".bash": "shellscript",
    ".bats": "shellscript",
    ".cgi": "shellscript",
    ".command": "shellscript",
    ".fcgi": "shellscript",
    ".ksh": "shellscript",
    ".sh.in": "shellscript",
    ".tmux": "shellscript",
    ".tool": "shellscript",
    ".zsh": "shellscript",
    ".slint": "slint",
    ".60": "slint",
    ".sig": "sml",
    ".fun": "sml",
    ".sql": "sql",
    ".dsql": "sql",
    ".st.css": "stylable",
    ".swift": "swift",
    ".sysl": "sysl",
    ".sv": "systemverilog",
    ".svh": "systemverilog",
    ".tf": "terraform",
    ".tfvars": "terraform-vars",
    ".sty": "tex",
    ".cls": "tex",
    ".bbx": "tex",
    ".cbx": "tex",
    ".ts": "typescript",
    ".cts": "typescript",
    ".mts": "typescript",
    ".tsx": "typescriptreact",
    ".vala": "vala",
    ".vapi": "vala",
    ".vb": "vb",
    ".brs": "vb",
    ".vbs": "vb",
    ".bas": "vb",
    ".vba": "vb",
    ".vdmpp": "vdmpp",
    ".vdmrt": "vdmrt",
    ".vdmsl": "vdmsl",
    ".vhd": "vhdl",
    ".vhdl": "vhdl",
    ".vho": "vhdl",
    ".vim": "viml",
    ".vimrc": "viml",
    ".gvim": "viml",
    ".ideavim": "viml",
    ".exrc": "viml",
    ".page": "visualforce",
    ".component": "visualforce",
    ".xml": "xml",
    ".xsd": "xml",
    ".ascx": "xml",
    ".atom": "xml",
    ".axml": "xml",
    ".axaml": "xml",
    ".bpmn": "xml",
    ".cpt": "xml",
    ".csl": "xml",
    ".csproj": "xml",
    ".csproj.user": "xml",
    ".dita": "xml",
    ".ditamap": "xml",
    ".dtd": "xml",
    ".ent": "xml",
    ".mod": "xml",
    ".dtml": "xml",
    ".fsproj": "xml",
    ".fxml": "xml",
    ".iml": "xml",
    ".isml": "xml",
    ".jmx": "xml",
    ".launch": "xml",
    ".menu": "xml",
    ".mxml": "xml",
    ".nuspec": "xml",
    ".opml": "xml",
    ".owl": "xml",
    ".proj": "xml",
    ".props": "xml",
    ".pt": "xml",
    ".publishsettings": "xml",
    ".pubxml": "xml",
    ".pubxml.user": "xml",
    ".rbxlx": "xml",
    ".rbxmx": "xml",
    ".rdf": "xml",
    ".rng": "xml",
    ".rss": "xml",
    ".shproj": "xml",
    ".storyboard": "xml",
    ".svg": "xml",
    ".targets": "xml",
    ".tld": "xml",
    ".tmx": "xml",
    ".vbproj": "xml",
    ".vbproj.user": "xml",
    ".vcxproj": "xml",
    ".vcxproj.filters": "xml",
    ".wsdl": "xml",
    ".wxi": "xml",
    ".wxl": "xml",
    ".wxs": "xml",
    ".xaml": "xml",
    ".xbl": "xml",
    ".xib": "xml",
    ".xlf": "xml",
    ".xliff": "xml",
    ".xpdl": "xml",
    ".xul": "xml",
    ".xoml": "xml",
    ".xsl": "xsl",
    ".xslt": "xsl",
    ".yml": "yaml",
    ".eyaml": "yaml",
    ".eyml": "yaml",
    ".yaml": "yaml",
    ".cff": "yaml",
    ".zig": "zig",
    ".zon": "zig",
}


language_id_to_scope = {
    "actionscript": "source.as2",
    "bat": "source.batchfile",
    "bibtex": "text.bibtex",
    "clojure": "source.clojure",
    "coffeescript": "source.coffee",
    "c": "source.c",
    "cpp": "source.cpp",
    "crystal": "source.crystal",
    "ecr": "text.ecr",
    "slang": "text.slang",
    "csharp": "source.cs",
    "css": "source.css",
    "d": "source.d",
    "dpp": "source.d",
    "dscript": "source.d",
    "dml": "source.dml",
    "sdl": "source.sdl",
    "diet": "source.diet",
    "dart": "source.dart",
    "diff": "source.diff",
    "dockerfile": "source.dockerfile",
    "elixir": "source.elixir",
    "eex": "text.elixir",
    "html-eex": "text.html.elixir",
    "elm": "source.elm",
    "erlang": "source.erlang",
    "fsharp": "source.fsharp",
    "FortranFreeForm": "source.fortran.free",
    "FortranFixedForm": "source.fortran.fixed",
    "genie": "source.genie",
    "gleam": "source.gleam",
    "glsl": "source.glsl",
    "go": "source.go",
    "graphql": "source.graphql",
    "grain": "source.grain",
    "groovy": "source.groovy",
    "handlebars": "text.html.handlebars",
    "haxe": "source.hx",
    "hlsl": "source.hlsl",
    "html": "text.html.basic",
    "hxml": "source.hxml",
    "ini": "source.ini",
    "jade": "text.pug",
    "java": "source.java",
    "javascript": "source.ts",
    "javascriptreact": "source.tsx",
    "json": "source.json",
    "jsonc": "source.json",
    "julia": "source.julia",
    "kotlin": "source.kotlin",
    "latex": "text.tex.latex",
    "less": "source.css.less",
    "log": "text.log",
    "lua": "source.lua",
    "makefile": "source.makefile",
    "markdown": "text.html.markdown",
    "nim": "source.nim",
    "nimble": "source.nimble",
    "ocaml": "source.ocaml",
    "ocaml.ocamllex": "source.ocaml.ocamllex",
    "objective-c": "source.objc",
    "objective-cpp": "source.objcpp",
    "perl": "source.perl",
    "perl6": "source.perl.6",
    "php": "source.php",
    "powershell": "source.powershell",
    "purescript": "source.purescript",
    "python": "source.python",
    "r": "source.r",
    "racket": "source.racket",
    "raml": "source.raml",
    "razor": "text.aspnetcorerazor",
    "reason": "source.reason",
    "rescript": "source.rescript",
    "restructuredtext": "source.rst",
    "ruby": "source.ruby",
    "rust": "source.rust",
    "scala": "source.scala",
    "scss": "source.css.scss",
    "shaderlab": "source.shaderlab",
    "shellscript": "source.shell",
    "slint": "source.slint",
    "sml": "source.sml",
    "sql": "source.sql",
    "stylable": "source.stylable",
    "swift": "source.swift",
    "sysl": "source.sysl",
    "systemverilog": "source.systemverilog",
    "terraform": "source.hcl.terraform",
    "terraform-vars": "source.hcl.terraform",
    "tex": "text.tex",
    "typescript": "source.ts",
    "typescriptreact": "source.tsx",
    "vala": "source.vala",
    "vb": "source.asp.vb.net",
    "vdmpp": "source.vdmpp",
    "vdmrt": "source.vdmsl",
    "vdmsl": "source.vdmsl",
    "vhdl": "source.vhdl",
    "viml": "source.viml",
    "visualforce": "text.visualforce.markup",
    "xml": "text.xml",
    "xsl": "text.xml.xsl",
    "yaml": "source.yaml",
    "zig": "source.zig",
}


scope_to_grammar: Dict[str, Grammar] = {
    "source.as2": BuiltInGrammar("source.as2", "https://raw.githubusercontent.com/admvx/as2-language-support/691be995fc1deaea0aff530b41e85d538e877583/syntaxes/ActionScript.plist"),
    "source.batchfile": BuiltInGrammar("source.batchfile", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/bat/syntaxes/batchfile.tmLanguage.json"),
    "text.bibtex": BuiltInGrammar("text.bibtex", "https://raw.githubusercontent.com/jlelong/vscode-latex-basics/82b28a3ab01e50918e38c47369f4a02b450362d5/syntaxes/Bibtex.tmLanguage.json"),
    "source.clojure": BuiltInGrammar("source.clojure", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/clojure/syntaxes/clojure.tmLanguage.json"),
    "source.coffee": BuiltInGrammar("source.coffee", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/coffeescript/syntaxes/coffeescript.tmLanguage.json"),
    "source.c": BuiltInGrammar("source.c", "https://raw.githubusercontent.com/jeff-hykin/better-c-syntax/ff81a5813673a7be5944e544b2ab83ff8c165a2b/autogenerated/c.tmLanguage.json"),
    "source.cpp": BuiltInGrammar("source.cpp", "https://raw.githubusercontent.com/jeff-hykin/better-cpp-syntax/9276ef69b245b4abec38091aeaa3fd56ed8d36f1/autogenerated/cpp.tmLanguage.json"),
    "source.cpp.embedded.macro": BuiltInGrammar("source.cpp.embedded.macro", "https://raw.githubusercontent.com/jeff-hykin/better-cpp-syntax/9276ef69b245b4abec38091aeaa3fd56ed8d36f1/autogenerated/cpp.embedded.macro.tmLanguage.json"),
    "source.crystal": BuiltInGrammar("source.crystal", "https://raw.githubusercontent.com/crystal-lang-tools/vscode-crystal-lang/c990acde25a020e910ca1092991e62289ceaa6c9/syntaxes/crystal.json"),
    "text.ecr": BuiltInGrammar("text.ecr", "https://raw.githubusercontent.com/crystal-lang-tools/vscode-crystal-lang/c990acde25a020e910ca1092991e62289ceaa6c9/syntaxes/ecr.json"),
    "text.slang": BuiltInGrammar("text.slang", "https://raw.githubusercontent.com/crystal-lang-tools/vscode-crystal-lang/c990acde25a020e910ca1092991e62289ceaa6c9/syntaxes/slang.json"),
    "source.cs": BuiltInGrammar("source.cs", "https://raw.githubusercontent.com/dotnet/csharp-tmLanguage/e9d9a525e56a2ac988155a411ce1e7280c92cd17/grammars/csharp.tmLanguage"),
    "source.css": BuiltInGrammar("source.css", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/css/syntaxes/css.tmLanguage.json"),
    "source.d": BuiltInGrammar("source.d", "https://raw.githubusercontent.com/Pure-D/code-d/bee4f0336d31fd81976bfb829fd6d5982a593977/./syntaxes/d.json"),
    "source.dml": BuiltInGrammar("source.dml", "https://raw.githubusercontent.com/Pure-D/code-d/bee4f0336d31fd81976bfb829fd6d5982a593977/./syntaxes/dml.json"),
    "source.sdl": BuiltInGrammar("source.sdl", "https://raw.githubusercontent.com/Pure-D/code-d/bee4f0336d31fd81976bfb829fd6d5982a593977/./syntaxes/sdl.json"),
    "source.diet": BuiltInGrammar("source.diet", "https://raw.githubusercontent.com/Pure-D/code-d/bee4f0336d31fd81976bfb829fd6d5982a593977/./syntaxes/diet.json"),
    "source.dart": BuiltInGrammar("source.dart", "https://raw.githubusercontent.com/dart-lang/dart-syntax-highlight/cbad4cb3e814a3975b3002b1d8dcd31bf71bc9d6/grammars/dart.json"),
    "source.diff": BuiltInGrammar("source.diff", "https://raw.githubusercontent.com/textmate/diff.tmbundle/0593bb775eab1824af97ef2172fd38822abd97d7/Syntaxes/Diff.plist"),
    "source.dockerfile": BuiltInGrammar("source.dockerfile", "https://raw.githubusercontent.com/moby/moby/7489b51f610104ab5acc43f4e77142927e7b522e/contrib/syntax/textmate/Docker.tmbundle/Syntaxes/Dockerfile.tmLanguage"),
    "source.elixir": BuiltInGrammar("source.elixir", "https://raw.githubusercontent.com/elixir-lsp/vscode-elixir-ls/0101a7a44fc14423e1a47ce022c72a55e1983b8a/syntaxes/elixir.json"),
    "text.elixir": BuiltInGrammar("text.elixir", "https://raw.githubusercontent.com/elixir-lsp/vscode-elixir-ls/0101a7a44fc14423e1a47ce022c72a55e1983b8a/syntaxes/eex.json"),
    "text.html.elixir": BuiltInGrammar("text.html.elixir", "https://raw.githubusercontent.com/elixir-lsp/vscode-elixir-ls/0101a7a44fc14423e1a47ce022c72a55e1983b8a/syntaxes/html-eex.json"),
    "source.elm": BuiltInGrammar("source.elm", "https://raw.githubusercontent.com/elm-tooling/elm-language-client-vscode/23bf1ae459f7053cc100aa129e2c4d8faca0dabf/syntaxes/elm-syntax.json"),
    "source.erlang": BuiltInGrammar("source.erlang", "https://raw.githubusercontent.com/erlang-ls/grammar/5d043682ec677e72ea33f29d2281c9e857ed1101/Erlang.plist"),
    "source.fsharp": BuiltInGrammar("source.fsharp", "https://raw.githubusercontent.com/ionide/ionide-fsgrammar/713cd4a34e7729e444cf85ae287dd94c19e34337/grammars/fsharp.json"),
    "source.fortran.free": BuiltInGrammar("source.fortran.free", "https://raw.githubusercontent.com/fortran-lang/vscode-fortran-support/8a65bde94e658cf1c01d99b86b8045f26264ccaf/syntaxes/fortran_free-form.tmLanguage.json"),
    "source.fortran.fixed": BuiltInGrammar("source.fortran.fixed", "https://raw.githubusercontent.com/fortran-lang/vscode-fortran-support/8a65bde94e658cf1c01d99b86b8045f26264ccaf/syntaxes/fortran_fixed-form.tmLanguage.json"),
    "source.genie": BuiltInGrammar("source.genie", "https://raw.githubusercontent.com/vala-lang/vala-vscode/c7736251219d5ceaf3b74c879f4fb0488195eeba/syntaxes/genie.tmLanguage"),
    "source.gleam": BuiltInGrammar("source.gleam", "https://raw.githubusercontent.com/gleam-lang/vscode-gleam/3dbe499cbd94f01adc9319a987e49b6e9d290843/syntaxes/gleam.tmLanguage.json"),
    "source.glsl": BuiltInGrammar("source.glsl", "https://raw.githubusercontent.com/stef-levesque/vscode-shader/f1c804839f9f58a6749c9a840187c5527b76b053/syntaxes/glsl.tmLanguage"),
    "source.go": BuiltInGrammar("source.go", "https://raw.githubusercontent.com/jeff-hykin/better-go-syntax/29007738160ff2918757b29562f84e5508d7adbc/autogenerated/go.tmLanguage.json"),
    "source.graphql": BuiltInGrammar("source.graphql", "https://raw.githubusercontent.com/graphql/graphiql/832867c5d7cbcc5282738965285ae3ffc9730845/packages/vscode-graphql-syntax/grammars/graphql.json"),
    "source.grain": BuiltInGrammar("source.grain", "https://raw.githubusercontent.com/grain-lang/grain-language-server/091a49bce5f288413505b13a52f72ae7d1b11e06/editor-extensions/vscode/syntaxes/grain.json"),
    "source.groovy": BuiltInGrammar("source.groovy", "https://raw.githubusercontent.com/textmate/groovy.tmbundle/6f903cacfb2d5397a350eeb73bc36b2c40f3da70/Syntaxes/Groovy.tmLanguage"),
    "text.html.handlebars": BuiltInGrammar("text.html.handlebars", "https://raw.githubusercontent.com/daaain/Handlebars/c2c09947b6b83d740e9ee94a6e3a0199476f2e15/grammars/Handlebars.json"),
    "source.hx": BuiltInGrammar("source.hx", "https://raw.githubusercontent.com/vshaxe/haxe-TmLanguage/b3cb0d3a6835938603d006fce402205fa16c11dd/haxe.tmLanguage"),
    "source.hlsl": BuiltInGrammar("source.hlsl", "https://raw.githubusercontent.com/tgjones/shaders-tmLanguage/87c0dca3a39170dbd7ee7e277db4f915fb2de14a/grammars/hlsl.json"),
    "text.html.basic": BuiltInGrammar("text.html.basic", "https://raw.githubusercontent.com/textmate/html.tmbundle/56a5f29746f1b5573488adfaa258326d4087d7ee/Syntaxes/HTML.plist"),
    "source.hxml": BuiltInGrammar("source.hxml", "https://raw.githubusercontent.com/vshaxe/haxe-TmLanguage/b3cb0d3a6835938603d006fce402205fa16c11dd/hxml.tmLanguage"),
    "source.ini": BuiltInGrammar("source.ini", "https://raw.githubusercontent.com/textmate/ini.tmbundle/7d8c7b5544c48069a246fd2f43e965f06d03d3da/Syntaxes/Ini.plist"),
    "text.pug": BuiltInGrammar("text.pug", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/pug/syntaxes/pug.tmLanguage.json"),
    "source.java": BuiltInGrammar("source.java", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/java/syntaxes/java.tmLanguage.json"),
    "source.ts": BuiltInGrammar("source.ts", "https://raw.githubusercontent.com/microsoft/TypeScript-TmLanguage/b51ef309756bea99f4ee9f6862febe62d7c12df5/TypeScript.tmLanguage"),
    "source.tsx": BuiltInGrammar("source.tsx", "https://raw.githubusercontent.com/microsoft/TypeScript-TmLanguage/b51ef309756bea99f4ee9f6862febe62d7c12df5/TypeScriptReact.tmLanguage"),
    "source.json": BuiltInGrammar("source.json", "https://raw.githubusercontent.com/microsoft/vscode-JSON.tmLanguage/d113e90937ed3ecc31ac54750aac2e8efa08d784/JSON.tmLanguage"),
    "source.julia": BuiltInGrammar("source.julia", "https://raw.githubusercontent.com/JuliaEditorSupport/atom-language-julia/95bcb952a4b617152ae7298fcc4ca0a6ea29b06f/grammars/julia_vscode.json"),
    "source.kotlin": BuiltInGrammar("source.kotlin", "https://raw.githubusercontent.com/fwcd/kotlin-language-server/4bdd672a32e421e78af153704f43f92eac4a4980/grammars/Kotlin.tmLanguage.json"),
    "text.tex.latex": BuiltInGrammar("text.tex.latex", "https://raw.githubusercontent.com/jlelong/vscode-latex-basics/82b28a3ab01e50918e38c47369f4a02b450362d5/syntaxes/LaTeX.tmLanguage.json"),
    "source.css.less": BuiltInGrammar("source.css.less", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/less/syntaxes/less.tmLanguage.json"),
    "text.log": BuiltInGrammar("text.log", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/log/syntaxes/log.tmLanguage.json"),
    "source.lua": BuiltInGrammar("source.lua", "https://raw.githubusercontent.com/LuaLs/lua.tmbundle/70b8f85df5f4d914600575aceef96391e6e8e939/Syntaxes/Lua.plist"),
    "source.makefile": BuiltInGrammar("source.makefile", "https://raw.githubusercontent.com/fadeevab/make.tmbundle/1d4c0b541959995db098df751ffc129da39a294b/Syntaxes/Makefile.plist"),
    "text.html.markdown": BuiltInGrammar("text.html.markdown", "https://raw.githubusercontent.com/microsoft/vscode-markdown-tm-grammar/eed230887a39da1ecf5bfc914e00a1e1813c0fdb/syntaxes/markdown.tmLanguage"),
    "source.nim": BuiltInGrammar("source.nim", "https://raw.githubusercontent.com/pragmagic/vscode-nim/0272a0544ddf147fde98f8a8f2b624b7dcb19eb3/syntaxes/nim.json"),
    "source.nimble": BuiltInGrammar("source.nimble", "https://raw.githubusercontent.com/pragmagic/vscode-nim/0272a0544ddf147fde98f8a8f2b624b7dcb19eb3/syntaxes/nimble.json"),
    "source.ocaml": BuiltInGrammar("source.ocaml", "https://raw.githubusercontent.com/ocamllabs/vscode-ocaml-platform/d6f8463ca88315e4e5b097e7c87c2e4d6303b4d0/syntaxes/ocaml.json"),
    "source.ocaml.ocamllex": BuiltInGrammar("source.ocaml.ocamllex", "https://raw.githubusercontent.com/ocamllabs/vscode-ocaml-platform/d6f8463ca88315e4e5b097e7c87c2e4d6303b4d0/syntaxes/ocamllex.json"),
    "source.objc": BuiltInGrammar("source.objc", "https://raw.githubusercontent.com/jeff-hykin/better-objc-syntax/119b75fb1f4d3e8726fa62588e3b935e0b719294/autogenerated/objc.tmLanguage.json"),
    "source.objcpp": BuiltInGrammar("source.objcpp", "https://raw.githubusercontent.com/jeff-hykin/better-objcpp-syntax/f5a804b75062cf98e1f8c50535e507b4ad3b8582/autogenerated/objcpp.tmLanguage.json"),
    "source.perl": BuiltInGrammar("source.perl", "https://raw.githubusercontent.com/textmate/perl.tmbundle/a85927a902d6e5d7805f56a653f324d34dfad53a/Syntaxes/Perl.plist"),
    "source.perl.6": BuiltInGrammar("source.perl.6", "https://raw.githubusercontent.com/textmate/perl.tmbundle/a85927a902d6e5d7805f56a653f324d34dfad53a/Syntaxes/Perl 6.tmLanguage"),
    "source.php": BuiltInGrammar("source.php", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/php/syntaxes/php.tmLanguage.json"),
    "source.powershell": BuiltInGrammar("source.powershell", "https://raw.githubusercontent.com/PowerShell/EditorSyntax/c0372a1d2df136ca6b3d1a9f7b85031dedf117f9/PowerShellSyntax.tmLanguage"),
    "source.purescript": BuiltInGrammar("source.purescript", "https://raw.githubusercontent.com/nwolverson/vscode-language-purescript/5364aa25ecc1ecf3e3ee67a1d7307f44894e106a/syntaxes/purescript.json"),
    "source.python": BuiltInGrammar("source.python", "https://raw.githubusercontent.com/MagicStack/MagicPython/7d0f2b22a5ad8fccbd7341bc7b7a715169283044/grammars/MagicPython.tmLanguage"),
    "source.r": BuiltInGrammar("source.r", "https://raw.githubusercontent.com/REditorSupport/vscode-R/d99a1f1761c0d746d252bc53bca95da04c8d6adb/syntax/r.json"),
    "source.racket": BuiltInGrammar("source.racket", "https://raw.githubusercontent.com/Eugleo/magic-racket/cd95319339634197444312e6812c9ef10b8ffc9b/syntaxes/racket.tmLanguage.json"),
    "source.raml": BuiltInGrammar("source.raml", "https://raw.githubusercontent.com/aml-org/als/7c75494b3e58287094a0fcd26dc9393957346a27/documentation/vscode-client-example/syntaxes/raml.tmLanguage.json"),
    "text.aspnetcorerazor": BuiltInGrammar("text.aspnetcorerazor", "https://raw.githubusercontent.com/dotnet/razor/addf903ee977e6d55e8903222f8e1c23af49cf3a/src/Razor/src/Microsoft.AspNetCore.Razor.VSCode.Extension/syntaxes/aspnetcorerazor.tmLanguage.json"),
    "source.reason": BuiltInGrammar("source.reason", "https://raw.githubusercontent.com/ocamllabs/vscode-ocaml-platform/d6f8463ca88315e4e5b097e7c87c2e4d6303b4d0/syntaxes/reason.json"),
    "source.rescript": BuiltInGrammar("source.rescript", "https://raw.githubusercontent.com/rescript-lang/rescript-vscode/9833a38911d85425ebe163446ea3e478b60ee8a2/grammars/rescript.tmLanguage.json"),
    "source.rst": BuiltInGrammar("source.rst", "https://raw.githubusercontent.com/trond-snekvik/vscode-rst/66bbd8fe1fb7e22202c6022ed7d45247660c129f/syntaxes/rst.tmLanguage.json"),
    "source.ruby": BuiltInGrammar("source.ruby", "https://raw.githubusercontent.com/textmate/ruby.tmbundle/efcb8941c701343f1b2e9fb105c678152fea6892/Syntaxes/Ruby.plist"),
    "source.rust": BuiltInGrammar("source.rust", "https://raw.githubusercontent.com/dustypomerleau/rust-syntax/a1f5e777379a28c9798b4db0df8e99c67e4b2056/syntaxes/rust.tmLanguage.json"),
    "source.scala": BuiltInGrammar("source.scala", "https://raw.githubusercontent.com/scala/vscode-scala-syntax/78750edc8babd117616290e507697a46cbadc85a/syntaxes/Scala.tmLanguage.json"),
    "source.css.scss": BuiltInGrammar("source.css.scss", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/scss/syntaxes/scss.tmLanguage.json"),
    "source.shaderlab": BuiltInGrammar("source.shaderlab", "https://raw.githubusercontent.com/tgjones/shaders-tmLanguage/87c0dca3a39170dbd7ee7e277db4f915fb2de14a/grammars/shaderlab.json"),
    "source.shell": BuiltInGrammar("source.shell", "https://raw.githubusercontent.com/jeff-hykin/better-shell-syntax/9b6fc5f28c57bcef7ec7ae3a27fed82cbd835f71/autogenerated/shell.tmLanguage.json"),
    "source.slint": BuiltInGrammar("source.slint", "https://raw.githubusercontent.com/slint-ui/slint/4cf44ea69d31bb953f83aa3778294ba05b849e96/editors/vscode/slint.tmLanguage.json"),
    "source.sml": BuiltInGrammar("source.sml", "https://raw.githubusercontent.com/azdavis/millet/67e20a13f0e216b87a3599906692c3acd4650bd9/editors/vscode/languages/sml/syntax.json"),
    "source.sql": BuiltInGrammar("source.sql", "https://raw.githubusercontent.com/microsoft/vscode-mssql/241673c18177e1792cc69150507539c55abd0ae7/syntaxes/SQL.plist"),
    "source.stylable": BuiltInGrammar("source.stylable", "https://raw.githubusercontent.com/wix/stylable-intelligence/941bf9d0a51ec3af0b0ac17b166a30357c0ae0ef/syntaxes/stylable.tmLanguage.json"),
    "source.swift": BuiltInGrammar("source.swift", "https://raw.githubusercontent.com/textmate/swift.tmbundle/aa73c3410d26dea8d39c834fd8e9bec4319dad2c/Syntaxes/Swift.tmLanguage"),
    "source.sysl": BuiltInGrammar("source.sysl", "https://raw.githubusercontent.com/anz-bank/vscode-sysl/6280476cde7bb0dbd9bf0065eb83aeaf5f503955/packages/extension/src/syntax/sysl.tmLanguage.json"),
    "source.systemverilog": BuiltInGrammar("source.systemverilog", "https://raw.githubusercontent.com/dalance/svls-vscode/657044f5cdea1ad97ade6a91a2f7aa958d1b6fa2/syntaxes/systemverilog.tmLanguage.json"),
    "source.hcl.terraform": BuiltInGrammar("source.hcl.terraform", "https://raw.githubusercontent.com/hashicorp/syntax/f5540c69ebe7b395caf3399c4b77ada38071978a/syntaxes/terraform.tmGrammar.json"),
    "text.tex": BuiltInGrammar("text.tex", "https://raw.githubusercontent.com/jlelong/vscode-latex-basics/82b28a3ab01e50918e38c47369f4a02b450362d5/syntaxes/TeX.tmLanguage.json"),
    "source.vala": BuiltInGrammar("source.vala", "https://raw.githubusercontent.com/vala-lang/vala-vscode/c7736251219d5ceaf3b74c879f4fb0488195eeba/syntaxes/vala.tmLanguage"),
    "source.asp.vb.net": BuiltInGrammar("source.asp.vb.net", "https://raw.githubusercontent.com/textmate/asp.vb.net.tmbundle/0cc4e1dcdb401703e373f32d7f0c8e9220b990dd/Syntaxes/ASP VB.net.plist"),
    "source.vdmpp": BuiltInGrammar("source.vdmpp", "https://raw.githubusercontent.com/overturetool/vdm-vscode/4af6be4c66dd3a5b46128978e194b737783c8e49/syntaxes/vdmpp.tmLanguage.json"),
    "source.vdm": BuiltInGrammar("source.vdm", "https://raw.githubusercontent.com/overturetool/vdm-vscode/4af6be4c66dd3a5b46128978e194b737783c8e49/syntaxes/vdm.tmLanguage.json"),
    "source.vdm.statements": BuiltInGrammar("source.vdm.statements", "https://raw.githubusercontent.com/overturetool/vdm-vscode/4af6be4c66dd3a5b46128978e194b737783c8e49/syntaxes/vdm.statements.tmLanguage.json"),
    "source.vdm.operators": BuiltInGrammar("source.vdm.operators", "https://raw.githubusercontent.com/overturetool/vdm-vscode/4af6be4c66dd3a5b46128978e194b737783c8e49/syntaxes/vdm.operators.tmLanguage.json"),
    "source.vdm.number": BuiltInGrammar("source.vdm.number", "https://raw.githubusercontent.com/overturetool/vdm-vscode/4af6be4c66dd3a5b46128978e194b737783c8e49/syntaxes/vdm.number.tmLanguage.json"),
    "source.vdmsl": BuiltInGrammar("source.vdmsl", "https://raw.githubusercontent.com/overturetool/vdm-vscode/4af6be4c66dd3a5b46128978e194b737783c8e49/syntaxes/vdmsl.tmLanguage.json"),
    "source.vhdl": BuiltInGrammar("source.vhdl", "https://raw.githubusercontent.com/VHDL-LS/rust_hdl_vscode/cc60f010dd1bb73eeb53a72807ec23809ce25181/syntaxes/vhdl.tmLanguage"),
    "source.viml": BuiltInGrammar("source.viml", "https://raw.githubusercontent.com/XadillaX/vscode-language-viml/03abc9f198dc6e1f8198cf95f9f71afc4b61e929/syntaxes/viml.tmLanguage.json"),
    "text.visualforce.markup": BuiltInGrammar("text.visualforce.markup", "https://raw.githubusercontent.com/forcedotcom/salesforcedx-vscode/96b713b5de8f34a30918efc46f3d030af531a1d5/packages/salesforcedx-vscode-visualforce/syntaxes/visualforce.json"),
    "text.xml": BuiltInGrammar("text.xml", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/xml/syntaxes/xml.tmLanguage.json"),
    "text.xml.xsl": BuiltInGrammar("text.xml.xsl", "https://raw.githubusercontent.com/microsoft/vscode/2f0f935056c5b26f93740920f59ff9985dd5ad6d/extensions/xml/syntaxes/xsl.tmLanguage.json"),
    "source.yaml": BuiltInGrammar("source.yaml", "https://raw.githubusercontent.com/textmate/yaml.tmbundle/e54ceae3b719506dba7e481a77cea4a8b576ae46/Syntaxes/YAML.tmLanguage"),
    "source.zig": BuiltInGrammar("source.zig", "https://raw.githubusercontent.com/ziglang/vscode-zig/d0bdaba503a5a85edeb4feb6d6f337ea513cec89/syntaxes/zig.tmLanguage.json"),
}
