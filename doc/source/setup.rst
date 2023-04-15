Setup
=====

First, make sure you have the required runtimes installed:

* `Python 3.8 <https://www.python.org/downloads/>`_ or newer versions
* `Node.js 14.0 <https://nodejs.org/en/download>`_ or newer versions

Currently, the only way to install LSPScript is directly from the GitHub repository:

  .. code:: bash

    $ git clone https://github.com/0xJonas/LSPScript.git

Once you have the sources downloaded, the next step is to build the *token-server*,
which is used for code tokenization. It is a node.js application since
it makes use of vscode-textmate (the same library which VSCode uses) for computing the tokens.
To build the token-server, perform the following steps:

1. Navigate to the ``token-server`` directory:

  .. code:: bash

    LSPScript$ cd token-server

2. Install the dependencies:

  .. code:: bash

    LSPScript/token-server$ npm install

3. Compile the token-server in debug mode:

  .. code:: bash

    LSPScript/token-server$ npm run build

.. important::
    Once LSPScript is released on PyPI, building the token-server manually will no longer be necessary.

.. TODO: LSPScript installation using pip
