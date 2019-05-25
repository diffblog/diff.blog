const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');

module.exports = {
    mode: 'development',
    entry: {
        followers: './static/js/followers.js',
        following: './static/js/following.js',
        follow: './static/js/follow.js',
        feed: './static/js/feed.js',
        post: './static/js/post.js',
        like: './static/js/like.js',
        save: './static/js/save.js',
        profile: './static/js/profile.js',
        signup_finish: './static/js/signup_finish.js',
        user_suggestions: './static/js/user_suggestions.js',
        search: './static/js/search.js',
        blog_settings: './static/js/blog_settings.js',
        admin: './static/js/admin.js',
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
        path: path.resolve(__dirname, 'static', 'dist')
    }
};
