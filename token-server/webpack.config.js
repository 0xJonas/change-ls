const path = require("path");

module.exports = {
    target: "node",
    entry: {
        main: "./out/src/main.js",
    },
    devtool: "inline-source-map",
    module: {
        rules: [
            {
                "test": /\.wasm/,
                "use": "file-loader"
            }
        ]
    },
    output: {
        filename: "[name].js",
        path: path.resolve(__dirname, '../lspscript/token_server')
    }
}
