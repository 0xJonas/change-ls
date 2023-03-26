const path = require("path");

module.exports = {
    target: "node",
    entry: {
        main: "./src/main.ts",
    },
    devtool: "inline-source-map",
    module: {
        rules: [
            {
                "test": /\.wasm/,
                "use": "file-loader"
            },
            {
                "test": /\.ts/,
                "use": "ts-loader"
            }
        ]
    },
    resolve: {
        extensions: [".ts", ".js"]
    },
    output: {
        filename: "[name].js",
        path: path.resolve(__dirname, '../lspscript/token_server')
    }
}
