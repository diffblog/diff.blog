const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const TerserPlugin = require("terser-webpack-plugin");

var webpack = require('webpack');

var Handlebars = require('handlebars/runtime');

module.exports = {
    mode: 'production',
    entry: {
        components: './app/static/js/components.js',
        followers: './app/static/js/followers.js',
        following: './app/static/js/following.js',
        follow_user: './app/static/js/follow_user.js',
        feed: './app/static/js/feed.js',
        post: './app/static/js/post.js',
        like: './app/static/js/like.js',
        save: './app/static/js/save.js',
        topic: './app/static/js/topic.js',
        profile: './app/static/js/profile.js',
        signup_finish: './app/static/js/signup_finish.js',
        user_suggestions: './app/static/js/user_suggestions.js',
        companies: './app/static/js/companies.js',
        search: './app/static/js/search.js',
        blog_settings: './app/static/js/blog_settings.js',
        admin: './app/static/js/admin.js',
        base: './app/static/js/base.js',
        plugin_iframe: './app/static/js/plugin_iframe.js',
        jobs: './jobs/static/js/jobs.js',
    },
    devtool: 'inline-source-map',
    plugins: [
        new CleanWebpackPlugin(),
        new MiniCssExtractPlugin({
            filename: '[name]-min.css',
            path: path.resolve(__dirname, 'app','static', 'dist')
        }),
        new webpack.ProvidePlugin({
          $: "jquery",
          jQuery: "jquery"
        }),
    ],
    module: {
        rules: [
          {
            test: /\.m?js$/,
            exclude: /(node_modules|bower_components)/,
            use: {
              loader: 'babel-loader',
              options: {
                presets: ['@babel/preset-env']
              }
            }
          },
            {
                test: /\.handlebars$/,
                loader: "handlebars-loader",
                options: {
                    runtime: path.resolve(__dirname, 'app','static', 'js', 'handlebars') 
                }
            },
            {
                test: /.s?css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                      loader: 'css-loader'
                    },
                    {
                      loader: 'sass-loader',
                      options: {
                        sourceMap: true,
                      }
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                          postcssOptions: {
                            ident: 'postcss',
                            plugins: [
                              require('tailwindcss'),
                              require('autoprefixer'),
                            ],
                          },
                        }
                    },
                ]
            }
        ]
    },
    optimization: {
      minimize: true,
      minimizer: [
        new CssMinimizerPlugin(),
        new TerserPlugin(),
      ],
    },
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, 'app','static', 'dist')
    }
};
