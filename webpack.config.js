const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');

module.exports = {
    mode: 'development',
    entry: {
        followers: './static/js/followers.js',
        following: './static/js/following.js',
        follow: './static/js/follow.js',
        home: './static/js/home.js',
        post: './static/js/post.js',
    },
    devtool: 'inline-source-map',
    plugins: [
        new CleanWebpackPlugin(),
    ],
    module: {
        rules: [
            { test: /\.handlebars$/, loader: "handlebars-loader" }
        ]
    },
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'dist')
    }
};