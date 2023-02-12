import { Transform, TransformOptions, TransformCallback } from "stream";
import { Buffer } from "buffer";

class LSPError extends Error {

    constructor(message: string, context?: string) {
        let fullMessage: string;
        if (context) {
            fullMessage = `Received malformed data: "${context}". ${message}`;
        } else {
            fullMessage = `Received malformed data: ${message}`;
        }
        super(fullMessage);
    }
}

function parseKeyValue(data: string, seperator: string): [string, string] {
    const seperatorIndex = data.indexOf(seperator);
    if (seperatorIndex < 0) {
        throw new LSPError("Expected key/value pair seperated by " + seperator, data);
    }

    const key = data.substring(0, seperatorIndex).trim();
    const value = data.substring(seperatorIndex + 1).trim();
    return [key, value];
}

class ContentType {
    readonly baseType: string;
    readonly subType: string | null;
    readonly parameters: { [key: string]: string };

    constructor(baseType: string, subType: string | null, parameters: { [key: string]: string }) {
        this.baseType = baseType;
        this.subType = subType;
        this.parameters = parameters;
    }

    static from(data: string): ContentType {
        const fields = data.split(";");

        let baseType: string;
        let subType: string | null = null;
        const slashIndex = fields[0].indexOf("/");
        if (slashIndex >= 0) {
            baseType = fields[0].substring(0, slashIndex);
            subType = fields[0].substring(0, slashIndex);
        } else {
            baseType = fields[0];
        }

        let parameters: { [key: string]: string } = {};
        for (let i = 1; i < fields.length; i++) {
            const [key, value] = parseKeyValue(fields[i], "=");
            parameters[key] = value;
        }

        return new ContentType(baseType, subType, parameters);
    }

    toString(): string {
        let type: string;
        if (this.subType) {
            type = this.baseType + "/" + this.subType;
        } else {
            type = this.baseType;
        }

        let parameters: string = "";
        for (const param in this.parameters) {
            parameters += ";" + param + "=" + this.parameters[param];
        }

        return type + parameters;
    }
}

const defaultContentType = new ContentType("application", "vscode-jsonrpc", { "charset": "utf-8" });

class Header {
    readonly contentLength: number;
    readonly contentType: ContentType;

    constructor(contentLength: number, contentType: ContentType) {
        this.contentLength = contentLength;
        this.contentType = contentType;
    }

    static from(data: string): Header {
        const fields = data.split("\r\n");

        let contentLength: number | null = null;
        let contentType = defaultContentType;

        for (const field of fields) {
            const [key, value] = parseKeyValue(field, ":");

            switch (key) {
                case "Content-Length": {
                    contentLength = Number.parseInt(value);
                    break;
                }
                case "Content-Type": {
                    contentType = ContentType.from(value)
                    break;
                }
                default: {}
            }
        }

        if (contentLength === null) {
            throw new LSPError("Header must contain Content-Length field");
        }

        return new Header(contentLength, contentType);
    }

    toString(): string {
        return `Content-Length: ${this.contentLength}\r\nContent-Type: ${this.contentType.toString()}\r\n\r\n`;
    }
}

function tryReadHeader(data: Buffer): [Header, number] | null {
    const text = data.toString("latin1");
    const headerEnd = text.indexOf("\r\n\r\n");
    if (headerEnd < 0) {
        return null;
    }

    const header = Header.from(text.substring(0, headerEnd));
    return [header, headerEnd + 4];
}

function isBufferEncoding(encoding: string): encoding is BufferEncoding {
    switch (encoding) {
        case "ascii":
        case "utf8":
        case "utf-8":
        case "utf16le":
        case "ucs2":
        case "ucs-2":
        case "base64":
        case "base64url":
        case "latin1":
        case "binary":
        case "hex":
            return true;
        default:
            return false;
    }
}

class LSPToJSON extends Transform {
    pendingHeader: Header | null
    buffer: Buffer;
    bufferContentLength: number;

    constructor(options: TransformOptions) {
        options.objectMode = true;
        super(options);
        this.buffer = Buffer.allocUnsafe(1024);
        this.bufferContentLength = 0;
        this.pendingHeader = null;
    }

    private appendChunkToBuffer(chunk: Buffer) {
        const newLength = this.bufferContentLength + chunk.length;
        if (newLength > this.buffer.length) {
            const newBuffer = Buffer.allocUnsafe(newLength);
            this.buffer.copy(newBuffer);
            this.buffer = newBuffer;
        }
        chunk.copy(this.buffer, this.bufferContentLength);
        this.bufferContentLength = newLength;
    }

    private discardBytes(amount: number): void {
        if (amount < this.bufferContentLength) {
            this.buffer.copy(this.buffer, 0, amount, this.bufferContentLength);
            this.bufferContentLength -= amount;
        } else {
            this.bufferContentLength = 0;
        }
    }

    private processHeaderData(): void {
        let maybeHeader;
        try {
            maybeHeader = tryReadHeader(this.buffer);
        } catch (error) {
            if (!(error instanceof LSPError)) {
                throw error;
            }
            this.destroy(error);
            return;
        }

        if (!maybeHeader) {
            return;
        }

        const [header, bytesRead] = maybeHeader;
        this.pendingHeader = header;
        this.discardBytes(bytesRead);
    }

    private processPayloadData(): void {
        if (!this.pendingHeader) {
            throw new LSPError("internal error");
        }

        let encoding = this.pendingHeader.contentType.parameters["charset"];
        if (encoding === undefined || encoding === "utf8") {
            encoding = "utf-8";
        }
        if (!isBufferEncoding(encoding)) {
            this.destroy(new LSPError("Content encoding is not supported: " + encoding));
            return;
        }
        const jsonString = this.buffer.toString(encoding, 0, this.pendingHeader.contentLength);
        let json_object;
        try {
            json_object = JSON.parse(jsonString);
        } catch (error) {
            if (!(error instanceof SyntaxError)) {
                throw error;
            }
            this.destroy(error);
            return;
        }
        this.push(json_object);
        this.discardBytes(this.pendingHeader.contentLength);
        this.pendingHeader = null;
    }

    _transform(chunk: any, encoding: BufferEncoding, callback: TransformCallback): void {
        if (typeof chunk === "string") {
            chunk = Buffer.from(chunk, encoding);
        } else if (!(chunk instanceof Buffer)) {
            this.destroy(new LSPError("Input stream must only send strings or buffers."));
            return;
        }

        this.appendChunkToBuffer(chunk);

        if (!this.pendingHeader) {
            this.processHeaderData();
        } else if (this.bufferContentLength >= this.pendingHeader.contentLength) {
            this.processPayloadData();
        }

        callback();
    }
}

class JSONToLSP extends Transform {

    constructor(options: TransformOptions) {
        options.objectMode = true;
        super(options);
    }

    _transform(chunk: any, _encoding: BufferEncoding, callback: TransformCallback): void {
        if (typeof chunk != "object") {
            this.destroy(new LSPError("Attempted to write non-JSON data"));
        }

        const payload = Buffer.from(JSON.stringify(chunk), "utf-8");
        const header = new Header(payload.length, defaultContentType);
        const headerData = Buffer.from(header.toString(), "latin1");

        this.push(Buffer.concat([headerData, payload]))
        callback();
    }
}

export {
    LSPError,
    LSPToJSON,
    JSONToLSP
}
