import * as assert from "assert";
import { JSONToLSP, LSPToJSON } from "../src/protocol";

async function eventToPromise(emitter: any, event: string, timeout: number = 1000): Promise<void> {
    return new Promise((resolve, reject) => {
        emitter.on(event, resolve);
        setTimeout(reject, timeout);
    })
}

describe("LSPToJSON", function () {
    it("correctly parses valid LSP packets", function () {
        const payload = Buffer.from(`{"test1": 5, "test2": [1, 2]}`, "utf-8");
        const header = Buffer.from(`Content-Length: ${payload.length}\r\n\r\n`, "latin1");

        const converter = new LSPToJSON({});
        converter.write(header);
        assert.strictEqual(converter.read(), null);
        converter.write(payload);
        assert.deepStrictEqual(converter.read(), { "test1": 5, "test2": [1, 2] });
    });
    it("rejects non-json packets", function () {
        const payload = Buffer.from(`<test>Not JSON</test>`, "utf-8");
        const header = Buffer.from(`Content-Length: ${payload.length}\r\n\r\n`, "latin1");

        const converter = new LSPToJSON({});
        converter.write(header);
        assert.strictEqual(converter.read(), null);
        converter.write(payload);
        return eventToPromise(converter, "error");
    });
    it("rejects invalid headers", function () {
        const header = Buffer.from(`Content-Thing: hi\r\n\r\n`, "latin1");

        const converter = new LSPToJSON({});
        converter.write(header);
        return eventToPromise(converter, "error");
    });
});

describe("JSONToLSP", function () {
    it("correctly serializes a JSON-packet", function () {
        const expected = Buffer.from('Content-Length: 25\r\nContent-Type: application/vscode-jsonrpc;charset=utf-8\r\n\r\n{"test1":5,"test2":[1,2]}');
        const obj = {"test1": 5, "test2": [1, 2]};

        const converter = new JSONToLSP({});
        converter.write(obj);

        const actual = converter.read();
        assert(actual instanceof Buffer);
        assert.equal(Buffer.compare(actual, expected), 0);
    })
});
