import { TopicSearchResult } from "./components/TopicSearchResult";
import { add_post_to_feed } from "./helpers";
import React from "react";
import ReactDOM from "react-dom/client";
import { Component } from "react/cjs/react.production.min";

const user_template = require("./../templates/small-follow.handlebars");
const post_template = require("./../templates/feed-item.handlebars");
const topic_template = require("./../templates/topic-search-result.handlebars");

function find_get_parameter(parameter_name) {
  var result = null,
    tmp = [];
  location.search
    .substr(1)
    .split("&")
    .forEach(function (item) {
      tmp = item.split("=");
      if (tmp[0] === parameter_name) result = tmp[1];
    });
  return result;
}

$(function () {
  const search_type = find_get_parameter("type") || "posts";
  const param =
    find_get_parameter("s") || $("#search_param").attr("data-param");
  $.ajax({
    method: "GET",
    url: "/api/search",
    data: {
      param: param,
      type: search_type,
    },
    success: function (data) {
      if (search_type === "users") {
        const users = data.users;
        if (users.length === 0) {
          $("#status").text("No users found.");
        } else {
          $("#status").hide();
        }
        for (let index in users) {
          var user = users[index];
          user["custom_size"] = "is-9";
          const html = user_template(user);
          $("#results").append(html);
        }
      } else if (search_type === "posts") {
        const posts = data.posts;
        if (posts.length === 0) {
          $("#status").text("No posts found.");
        } else {
          $("#status").hide();
        }
        for (let index in posts) {
          var post = posts[index];
          post.feed_info = {};
          post.feed_info.feed = "search";
          post["custom_size"] = "is-9";
          add_post_to_feed($("#results"), post);
        }
      } else if (search_type === "topics") {
        const topics = data.topics;
        if (topics.length === 0) {
          $("#status").text("No topics found.");
        } else {
          $("#status").hide();
        }
        const results = document.querySelector("#results");
        const root = ReactDOM.createRoot(results);
        const topicElements = [];
        for (let topic of topics) {
          topicElements.push(
            <TopicSearchResult
              key={topic.id}
              topicId={topic.id}
              topicDisplayName={topic.display_name}
              topicURL={topic.url}
            />,
          );
        }
        root.render(<>{topicElements}</>);
      }
    },
  });
});
