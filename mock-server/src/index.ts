import { Connection, InitializedParams, InitializeParams, InitializeResult } from "vscode-languageserver"
import { createConnection } from "vscode-languageserver/node";

import { readFileSync } from "fs";
import { exit } from "process";
import { argv } from "process";
import assert = require("assert");

type JSONValue = { [key: string]: JSONValue } | Array<JSONValue> | string | number | boolean | null;

interface TemplateParams {
    expand?: { [key: string]: string },
    replace?: { [key: string]: JSONValue }
}

interface TestMessage {
    type: "request" | "notification";
    method: string;
    params?: JSONValue;
    intermediate?: Array<TestMessage>;
    result?: JSONValue;
}

interface TestMessagesUnordered {
    type: "request-unordered";
    content: Array<TestMessage>;
}

interface TestSetup {
    name: string;
    initializeResult?: InitializeResult;
    sequence: Array<TestMessage | TestMessagesUnordered>
}

const connection = createConnection()

function loadTest(path: string): TestSetup {
    const dataRaw = readFileSync(path, { "encoding": "utf-8" })
    const data = JSON.parse(dataRaw)
    return data;
}

const test = loadTest(argv[argv.length - 1]);
let sequenceIndex = 0;
let unorderedReceived: Array<boolean> = [];
let templateParams: TemplateParams = {};
const NOT_HANDLED = Symbol("NOT_HANDLED");

connection.onInitialize((params: InitializeParams) => {
    if (test.initializeResult) {
        return test.initializeResult;
    } else {
        return {
            capabilities: {
                // TODO: fill accordingly as more tests are added
            }
        };
    }
});

connection.onInitialized((params: InitializedParams) => {})

function handleSleep(time: number) {
    // :(
    const waitUntil = new Date(new Date().getTime() + time * 1000);
    while(waitUntil > new Date());
}

function handleTerminate(exitCode: number) {
    exit(exitCode)
}

function handleSetTemplateParams(params: TemplateParams) {
    templateParams = params;
}

function assertTemplateParams(params: any): asserts params is TemplateParams {
    assert(typeof params === "object");
    assert(params !== null);
    assert(!(params instanceof Array));
    for (let key in params) {
        assert(key === "expand" || key === "replace");
    }
}

function handleCustomRequests(method: string, params: JSONValue): any {
    switch (method) {
        case "$/sleep": {
            assert(typeof params === "number")
            return handleSleep(params);
        }
        case "$/terminate": {
            assert(typeof params === "number")
            return handleTerminate(params);
        }
        case "$/setTemplateParams": {
            assertTemplateParams(params);
            return handleSetTemplateParams(params);
        }
    }
    return NOT_HANDLED;
}

/**
 * Processes a template string and returns the result.
 *
 * The template must be a string. If the string contains the pattern
 * `"${<name>}"`, then the matched substring is replaced by the property
 * `<name>` in `templateParams.expand`. If the entire string matches the pattern
 * `"#{<name>}"`, then the value of the property `<name>` in `templateParams.replace`
 * is returned, which need not be a string. If any of the property lookups fails,
 * an `Error` is thrown.
 *
 * @param template The template to be expanded
 * @returns The resulting JSONValue, which might by any type if there was a replacement
 */
function processTemplate(template: string): JSONValue {
    const replaceRegExp = /^#\{(\w+)\}$/;
    const replaceResult = template.match(replaceRegExp);
    if (replaceResult) {
        if (templateParams.replace && replaceResult[1] in templateParams.replace) {
            return templateParams.replace[replaceResult[1]];
        } else {
            throw Error("Template parameter not found");
        }
    }
    const expandRegExp = /\$\{(\w+)\}/gd;
    let expandResult = expandRegExp.exec(template);
    while (expandResult) {
        const param = expandResult[1];
        if (!(templateParams.expand && (param in templateParams.expand))) {
            throw Error("Template parameter not found");
        }
        const from = expandResult.index;
        const to = from + param.length + 3; // The 3 comes from '${' and '}'
        const replacement = templateParams.expand[param];
        template = template.substring(0, from) + templateParams.expand[param] + template.substring(to);
        expandRegExp.lastIndex += replacement.length - (to - from);
        expandResult = expandRegExp.exec(template);
    }
    return template;
}

function matchArrays(ref: Array<JSONValue>, test: Array<JSONValue>): boolean {
    if (ref.length !== test.length) {
        return false;
    }
    for (let i = 0; i < ref.length; i++) {
        if (!matchDeepEqual(ref[i], test[i])) {
            return false;
        }
    }
    return true;
}

function matchObjects(ref: { [key: string]: JSONValue }, test: { [key: string]: JSONValue }): boolean {
    for (let keyTemplate in ref) {
        const key = processTemplate(keyTemplate);
        if (!(typeof key === "string")) {
            throw Error("Replacement templates in object keys must expand to a string value");
        }
        if (!(key in test)) {
            return false;
        }
        if (!matchDeepEqual(ref[keyTemplate], test[key])) {
            return false;
        }
    }
    return true;
}

function matchDeepEqual(ref: JSONValue, test: JSONValue): boolean {
    if (typeof ref === "string") {
        ref = processTemplate(ref);
    }

    const refType = typeof ref;
    const testType = typeof test;
    if (refType !== testType) {
        return false;
    }

    if (ref === null && test === null) {
        return true;
    } else if (["string", "number", "boolean"].indexOf(refType) >= 0) {
        return ref === test;
    } else if (ref instanceof Array && test instanceof Array) {
        return matchArrays(ref, test);
    } else if (ref !== null && test !== null && !(ref instanceof Array) && !(test instanceof Array)) {
        assert(typeof ref === "object");
        assert(typeof test === "object");
        return matchObjects(ref, test);
    } else {
        return false;
    }
}

function matchMessage(msg: TestMessage, method: string, params?: JSONValue): boolean {
    if (msg.method !== method) {
        return false;
    }
    if (msg.params !== undefined) {
        if (params === undefined) {
            return false;
        }
        return matchDeepEqual(msg.params, params);
    } else {
        return params === undefined;
    }
}

async function processIntermediate(intermediate: TestMessage[]) {
    try {
        for (let option of intermediate) {
            if (option.type == "notification") {
                await connection.sendNotification(option.method, option.params);
            } else {
                const result = await connection.sendRequest<JSONValue>(option.method, option.params);
                processRequestResult(result, option.result);
            }
        }
    } catch (e) {
        // We need seperate error handling here,
        // since the function async.
        console.error(e);
        exit(1);
    }
}

connection.onRequest(async (method: string, params: any) => {
    try {
        const maybeResult = handleCustomRequests(method, params);
        if (maybeResult !== NOT_HANDLED) {
            return maybeResult;
        }

        const msg = test.sequence[sequenceIndex];
        if (msg.type == "request") {
            assert(matchMessage(msg, method, params));
            sequenceIndex++;
            if (msg.intermediate) {
                await processIntermediate(msg.intermediate);
            }
            return msg.result;
        } else if (msg.type == "request-unordered") {
            if (unorderedReceived.length == 0) {
                unorderedReceived = Array(msg.content.length)
                unorderedReceived.fill(false)
            }

            for (let i = 0; i < msg.content.length; i++) {
                let option = msg.content[i];
                if (unorderedReceived[i]) {
                    continue;
                } else if (!matchMessage(option, method, params)) {
                    continue;
                } else {
                    unorderedReceived[i] = true;
                    if (unorderedReceived.every(e => e)) {
                        // All messages received
                        sequenceIndex++;
                    }
                    if (option.intermediate) {
                        processIntermediate(option.intermediate);
                    }
                    return option.result;
                }
            }
            assert(false) // Nothing matched
        } else {
            // Request was sent, but something else was expected.
            assert(false);
        }
    } catch (e) {
        console.error(e);
        exit(1);
    }
});

function processRequestResult(result?: JSONValue, expectedResult?: JSONValue) {
    if (result === undefined) {
        assert(expectedResult === undefined)
    } else {
        assert(expectedResult !== undefined);
        assert(matchDeepEqual(expectedResult, result));
    }
}

connection.onNotification((method: string, params: any) => {
    try {
        const msg = test.sequence[sequenceIndex];
        assert(msg.type == "notification");
        assert(matchMessage(msg, method, params));
        sequenceIndex++;
        if (msg.intermediate) {
            processIntermediate(msg.intermediate);
        }
    } catch (e) {
        console.error(e);
        exit(1);
    }
});

connection.listen()
