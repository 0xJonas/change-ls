export interface TokenizeParams {
    /**
     * The index grammar to use, as returned by grammar/load.
     */
    grammarIndex: number;

    /**
     * The raw text to tokenize.
     */
    text: string;
}

export interface TokenizeResult {
    /**
     * The scopes used by this `TokenizeResult`.
     */
    scopes: number[];

    /**
     * The tokens in the following format:
     *
     * The list alternates between two different sublists:
     * - sublists at even indices always contain three numbers, one for each of `[deltaLine, deltaStart, length]`
     * - sublists at odd indices contain any number of scopes for the previous token, as indices into `scopes`.
     */
    tokens: number[][];
}
