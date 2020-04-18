const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');

module.exports = {
    mode: 'production',
    entry: {
        followers: './app/static/js/followers.js',
        following: './app/static/js/following.js',
        follow: './app/static/js/follow.js',
        feed: './app/static/js/feed.js',
        post: './app/static/js/post.js',
        like: './app/static/js/like.js',
        save: './app/static/js/save.js',
        profile: './app/static/js/profile.js',
        signup_finish: './app/static/js/signup_finish.js',
        user_suggestions: './app/static/js/user_suggestions.js',
        search: './app/static/js/search.js',
        blog_settings: './app/static/js/blog_settings.js',
        admin: './app/static/js/admin.js',
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
        path: path.resolve(__dirname, 'app','static', 'dist')
    }
};
