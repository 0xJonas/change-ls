export interface TextDocumentTokenizeParams {
    /**
     * The initial scope to use. This specifies the grammar.
     */
    scopeName: string;

    /**
     * The raw text to tokenize.
     */
    text: string;
}

export interface TextDocumentTokenizeResult {
    /**
     * The scopes used by this `TokenizeResult`.
     */
    scopes: string[];

    /**
     * The tokens in the following format:
     *
     * The list alternates between two different sublists:
     * - sublists at even indices always contain three numbers, one for each of `[deltaLine, deltaStart, length]`
     * - sublists at odd indices contain any number of scopes for the previous token, as indices into `scopes`.
     */
    tokens: number[][];
}

export interface GrammarRequestRawParams {

    /**
     * The initial scope for which the raw grammar is requested.
     */
    scopeName: string;
}

export interface GrammarRequestRawResult {

    /**
     * The raw grammar in a format compatible with vscode-textmate.
     */
    rawGrammar: string;
}
