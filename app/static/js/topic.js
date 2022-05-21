import { setup_ajax } from "./helpers";
setup_ajax();
var topic_item_sidebar_template = require("./../templates/topic-item-home-sidebar.handlebars");
var topic_follow_template = require("./../templates/topic-follow-button.handlebars");

export function is_subscribed_to_topic(my_topics, topic_id) {
  for (let my_topic of my_topics) {
    if (my_topic.id === parseInt(topic_id)) {
      return true;
    }
  }
  return false;
}

export function load_my_topics_left_sidebar_if_required() {
  if (!$("#my-topics").length) {
    return;
  }

  $.ajax({
    type: "GET",
    url: "/api/user/topics",
    success: function (my_topics) {
      $("#my-topics").empty();
      for (let topic of my_topics) {
        const html = topic_item_sidebar_template(topic);
        $("#my-topics").append(html);
      }
    },
  });
}

$(function () {
  load_my_topics_left_sidebar_if_required();

  if ($("#popular-topics").length) {
    $.ajax({
      type: "GET",
      url: "/api/topics/popular",
      success: function (popular_topics) {
        let count = 0;
        for (let topic of popular_topics) {
          const html = topic_item_sidebar_template(topic);
          $("#popular-topics").append(html);
          count += 1;
          if (count === 30) {
            break;
          }
        }

        if ($("#topic-follow-button-holder").length) {
          const page_topic_id = $("#topic-follow-button-holder").data(
            "topic-id"
          );
          const html = topic_follow_template({
            following: false,
            id: page_topic_id,
          });
          $("#topic-follow-button-holder").html(html);
        }
      },
    });
  }
});
