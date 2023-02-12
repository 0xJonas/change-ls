import * as vsctm from "vscode-textmate";
import * as oniguruma from "vscode-oniguruma";
import { TokenizeParams, TokenizeResult } from "./structures";

// import relative to ./out/src/main.js
import onig_wasm from "../../node_modules/vscode-oniguruma/release/onig.wasm";

import { stdin, stdout } from "process"
import { LSPToJSON } from "./protocol";

async function initialize() {

}

async function listen() {
    const jsonIn = stdin.pipe(new LSPToJSON({}));
}
