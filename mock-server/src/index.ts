import { Connection, InitializedParams, InitializeParams } from "vscode-languageserver"
import { createConnection } from "vscode-languageserver/node";

import { readFileSync } from "fs";
import { argv } from "process";
import assert = require("assert");

interface TestMessage {
    type: "request" | "notification";
    method: string;
    params?: any;
    intermediate?: Array<TestMessage>;
    result?: any;
}

interface TestMessagesUnordered {
    type: "request-unordered";
    content: Array<TestMessage>;
}

interface TestSetup {
    name: string;
    defaultInitialize: boolean;
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
let unorderedReceived: Array<boolean> = []

connection.onInitialize((params: InitializeParams) => {
    return {
        capabilities: {
            // TODO: fill accordingly as more tests are added
        }
    };
});

connection.onInitialized((params: InitializedParams) => {})

function matchMessage(msg: TestMessage, method: string, params: any): boolean {
    if (msg.method !== method) {
        return false;
    }
    try {
        assert.deepEqual(msg.params, params);
        return true;
    } catch {
        return false;
    }
}

function processRequest(connection: Connection, msg: TestMessage): any {
    if (msg.intermediate !== undefined) {
        for (let i of msg.intermediate) {
            assert(i.type == "notification");

            // Assume the notifications are sent in order and before the response.
            connection.sendNotification(i.method, i.params);
        }
    }

    return msg.result;
}

connection.onRequest((method: string, params: any) => {
    console.error(method);
    const msg = test.sequence[sequenceIndex];
    if (msg.type == "request") {
        assert(matchMessage(msg, method, params), `${msg} does not match ${params}`);
        sequenceIndex++;
        return processRequest(connection, msg);
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
                return processRequest(connection, option);
            }
        }
        assert(false) // Nothing matched
    }
});

connection.onNotification((method: string, params: any) => {
    const msg = test.sequence[sequenceIndex];
    assert(msg.type == "notification");
    assert(matchMessage(msg, method, params));

    if (msg.intermediate) {
        for (let option of msg.intermediate) {
            if (option.type == "notification") {
                connection.sendNotification(option.method, option.params);
            } else {
                connection.sendRequest(option.method, option.params).then(result => {
                    assert(result == option.result);
                })
            }
        }
    }
});

connection.listen()
