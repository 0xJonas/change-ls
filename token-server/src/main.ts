import * as rpc from "vscode-jsonrpc/node";
import * as vsctm from "vscode-textmate";
import { IRawGrammar } from "vscode-textmate/release/rawGrammar";
import * as oniguruma from "vscode-oniguruma";
import { TextDocumentTokenizeParams, TextDocumentTokenizeResult, GrammarRequestRawParams, GrammarRequestRawResult } from "./structures";

import onigWasm from "../node_modules/vscode-oniguruma/release/onig.wasm";

import { stdin, stdout } from "process"
import { readFile } from "fs/promises";
import { StreamMessageReader, StreamMessageWriter } from "vscode-jsonrpc/node";
import { exit } from "process";

type IndexMap = { [scopeName: string]: number};

interface TokenizationState {
    indexMap: IndexMap;
    firstLine: boolean;
}

function updateScopeIndices(currentIndexMap: IndexMap, currentScopes: string[], newScopes: string[]): void {
    for (const s of newScopes) {
        if (!(s in currentIndexMap)) {
            currentIndexMap[s] = currentScopes.length;
            currentScopes.push(s)
        }
    }
}

function updateTokenizeResult(current: TextDocumentTokenizeResult, lineTokens: vsctm.IToken[], state: TokenizationState): void {
    let first = true;
    let currentCol = 0;
    for (const token of lineTokens) {
        updateScopeIndices(state.indexMap, current.scopes, token.scopes);

        const deltaLine = first && !state.firstLine ? 1 : 0;
        const deltaStart = token.startIndex - currentCol;
        const length = token.endIndex - token.startIndex;
        const indices = token.scopes.map(element => state.indexMap[element]);
        current.tokens.push([deltaLine, deltaStart, length], indices);

        currentCol = token.startIndex;
        first = false;
        state.firstLine = false;
    }
}

function findLineBreak(text: string, offset: number): [number, string] {
    const indexSubstring = text.substring(offset).search(/\r\n|\n|\r/);
    if (indexSubstring < 0) {
        return [text.length, ""];
    }

    const index = offset + indexSubstring;
    if (text[index] == '\r') {
        if (text[index + 1] == '\n') {
            return [index, "\r\n"];
        } else {
            return [index, "\r"];
        }
    } else {
        return [index, "\n"];
    }
}

class TokenLSPError extends Error {
    constructor(message: string) {
        super(message);
    }
}

const INITIALIZE_REQUEST = new rpc.RequestType0<null, void>("initialize");
const GRAMMAR_REQUEST_RAW_REQUEST = new rpc.RequestType<GrammarRequestRawParams, GrammarRequestRawResult, void>("grammar/requestRaw")
const TEXTDOCUMENT_TOKENIZE_REQUEST = new rpc.RequestType<TextDocumentTokenizeParams, TextDocumentTokenizeResult, void>("textDocument/tokenize");
const EXIT_NOTIFICATION = new rpc.NotificationType0("exit");

class TokenServer {
    private readonly connection: rpc.MessageConnection;
    private registry?: vsctm.Registry;

    constructor(input: rpc.MessageReader, output: rpc.MessageWriter) {
        this.connection = rpc.createMessageConnection(input, output);
        this.connection.onRequest(INITIALIZE_REQUEST, this.initialize.bind(this));
        this.connection.onRequest(TEXTDOCUMENT_TOKENIZE_REQUEST, this.textDocumentTokenize.bind(this))
        this.connection.onNotification(EXIT_NOTIFICATION, this.exit.bind(this));
    }

    private async loadOniguruma(): Promise<vsctm.IOnigLib> {
        const onigurumaBinary = await readFile(onigWasm);
        await oniguruma.loadWASM(onigurumaBinary);
        return {
            createOnigScanner(patterns: string[]) { return new oniguruma.OnigScanner(patterns); },
            createOnigString(s: string) { return new oniguruma.OnigString(s); }
        };
    }

    async initialize(): Promise<void> {
        this.registry = new vsctm.Registry({
            onigLib: this.loadOniguruma(),
            loadGrammar: this.loadGrammar.bind(this)
        });
    }

    private async loadGrammar(scopeName: string): Promise<IRawGrammar | undefined | null> {
        if (!this.registry) {
            throw new TokenLSPError("TokenServer is not initialized");
        }

        const result = await this.connection.sendRequest(GRAMMAR_REQUEST_RAW_REQUEST, { "scopeName": scopeName });

        if (!result) {
            // Grammar was not found
            return null;
        }

        if (result.format == "json") {
            return <IRawGrammar>JSON.parse(result.rawGrammar);
        } else if (result.format == "plist") {
            // parseRawGrammar defaults to PLIST when no filename is given.
            return vsctm.parseRawGrammar(result.rawGrammar);
        } else {
            return null;
        }
    }

    async textDocumentTokenize(params: TextDocumentTokenizeParams): Promise<TextDocumentTokenizeResult> {
        if (!this.registry) {
            throw new TokenLSPError("TokenServer is not initialized");
        }

        const state: TokenizationState = {
            indexMap: {},
            firstLine: true
        }

        const grammar = await this.registry.loadGrammar(params.scopeName);
        if (!grammar) {
            throw new TokenLSPError("Error fetching grammar");
        }

        let currentOffset = 0;
        let text = params.text;
        let ruleStack = vsctm.INITIAL;
        let result: TextDocumentTokenizeResult = {
            scopes: [],
            tokens: []
        };

        while (currentOffset < text.length) {
            const [lineBreakIndex, lineBreakString] = findLineBreak(text, currentOffset);
            const line = text.substring(currentOffset, lineBreakIndex);
            const tokenizeLineResult = grammar.tokenizeLine(line, ruleStack);

            updateTokenizeResult(result, tokenizeLineResult.tokens, state);

            ruleStack = tokenizeLineResult.ruleStack;
            currentOffset = lineBreakIndex + lineBreakString.length;
        }

        return result;
    }

    async exit(): Promise<never> {
        exit(0);
    }

    listen(): void {
        this.connection.onError(e => console.error(e));
        this.connection.listen();
    }
}

const server = new TokenServer(new StreamMessageReader(stdin), new StreamMessageWriter(stdout));
server.listen()
