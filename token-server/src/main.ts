import * as rpc from "vscode-jsonrpc/node";
import * as vsctm from "vscode-textmate";
import { IRawGrammar } from "vscode-textmate/release/rawGrammar";
import * as oniguruma from "vscode-oniguruma";
import { TextDocumentTokenizeParams, TextDocumentTokenizeResult, GrammarRequestRawParams, GrammarRequestRawResult } from "./structures";

// import relative to ./out/src/main.js
import onigWasm from "../../node_modules/vscode-oniguruma/release/onig.wasm";

import { stdin, stdout } from "process"
import { readFile } from "fs/promises";
import { StreamMessageReader, StreamMessageWriter } from "vscode-jsonrpc/node";
import { exit } from "process";

type IndexMap = { [scopeName: string]: number};

interface TokenizationState {
    indexMap: IndexMap;
    currentLine: number;
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

        let deltaLine = first ? 1 : 0;
        let deltaStart = token.startIndex - currentCol;
        let length = token.endIndex - token.startIndex;
        let indices = token.scopes.map(element => state.indexMap[element]);
        current.tokens.push([deltaLine, deltaStart, length], indices);

        currentCol = token.startIndex;
        first = false;
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
        this.connection.onRequest(INITIALIZE_REQUEST, this.initialize);
        this.connection.onRequest(TEXTDOCUMENT_TOKENIZE_REQUEST, this.textDocumentTokenize)
        this.connection.onNotification(EXIT_NOTIFICATION, this.exit);
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
            loadGrammar: this.loadGrammar
        });
    }

    private async loadGrammar(scopeName: string): Promise<IRawGrammar | undefined | null> {
        if (!this.registry) {
            throw new TokenLSPError("TokenServer is not initialized");
        }

        const result = await this.connection.sendRequest(GRAMMAR_REQUEST_RAW_REQUEST, { "scopeName": scopeName });
        return vsctm.parseRawGrammar(result.rawGrammar);
    }

    async textDocumentTokenize(params: TextDocumentTokenizeParams): Promise<TextDocumentTokenizeResult> {
        if (!this.registry) {
            throw new TokenLSPError("TokenServer is not initialized");
        }

        const state: TokenizationState = {
            indexMap: {},
            currentLine: 0
        }

        const grammar = await this.registry.loadGrammar(params.scopeName);
        if (!grammar) {
            throw new TokenLSPError("Error fetching grammar");
        }

        let currentOffset = 0;
        let text = params.text;
        let ruleStack: vsctm.StateStack | null = null;
        let result: TextDocumentTokenizeResult = {
            scopes: [],
            tokens: []
        };

        while (currentOffset < text.length) {
            let lineEnd = text.indexOf("\n", currentOffset);
            if (lineEnd < 0) {
                lineEnd = text.length;
            }
            const line = text.substring(currentOffset, lineEnd + 1);
            const tokenizeLineResult = grammar.tokenizeLine(line, ruleStack);

            updateTokenizeResult(result, tokenizeLineResult.tokens, state);

            ruleStack = tokenizeLineResult.ruleStack;
            currentOffset = lineEnd + 1;
        }

        return result;
    }

    async exit(): Promise<never> {
        exit(0);
    }

    listen(): void {
        this.connection.listen()
    }
}

const server = new TokenServer(new StreamMessageReader(stdin), new StreamMessageWriter(stdout));
server.listen()
