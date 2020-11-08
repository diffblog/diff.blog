import { get_feed_info } from "./helpers";

var template = require("./../templates/user-suggestion.handlebars");

$(function () {
  const feed_info = get_feed_info();
  $.ajax({
    method: "GET",
    url: "/api/users/suggestions",
    data: { limit: 30, topic: feed_info.topic },
    success: function (data) {
      for (let index in data) {
        var user = data[index];
        user["custom_size"] = "is-9";
        user["show_topics"] = true;
        const html = template(user);
        $("#user_list").append(html);
      }
    },
  });
});
