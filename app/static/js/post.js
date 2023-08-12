var dayjs = require("dayjs");
var relativeTime = require("dayjs/plugin/relativeTime");
dayjs.extend(relativeTime);

import {
  setup_ajax,
  show_login_prompt_if_required,
  update_side_feed,
} from "./helpers";
setup_ajax();

var comment_template = require("./../templates/comment.handlebars");
var follow_template = require("./../templates/small-follow.handlebars");

$(function () {
  $("#comment-content").on("click", function () {
    show_login_prompt_if_required("add_comment");
  });

  $("#submit-comment-button").on("click", function () {
    if (show_login_prompt_if_required("add_comment")) {
      return;
    }
    var content = $("#comment-content").val();
    var html = comment_template({
      content: content,
      profile: page_params.profile,
      time: "Just now",
    });
    $("#comments-holder").append(html);
    $.ajax({
      type: "POST",
      url: "/api/post/comment",
      data: {
        content: content,
        post_id: $(this).data("post-id"),
      },
    });
  });
  $.ajax({
    type: "GET",
    url: "/api/post/comments",
    data: { post_id: page_params.post_id },
    success: function (comments) {
      for (let index in comments) {
        var comment = comments[index];
        comment.time = dayjs().to(comment.posted_on);
        var html = comment_template(comment);
        $("#comments-holder").append(html);
      }
    },
  });

  $("#follow_list").html(follow_template(page_params.posted_by));

  $("#comments-holder").on("click", ".comment_vote_button", function () {
    var already_upvoted = $(this).data("vote-upvoted");
    var comment_id = $(this).data("comment-id");
    var upvotes_counter = $("#feed_upvotes_counter_" + comment_id);
    var upvotes_count = upvotes_counter.text();
    if (already_upvoted) {
      $(this).html('<i class="far fa-heart"></i>');
      $(this).data("vote-upvoted", false);
      upvotes_counter.text(parseInt(upvotes_count) - 1);
    } else {
      $(this).html('<i class="fas fa-heart"></i>');
      $(this).data("vote-upvoted", true);
      upvotes_counter.text(parseInt(upvotes_count) + 1);
    }
    $.ajax({
      type: "POST",
      url: "/api/comment/vote",
      data: { comment_id: comment_id },
      success: function () {},
    });
  });

  $.get("/api/posts/user", {
    username: page_params.posted_by.github_username,
    limit: 5,
  }).done(function (posts) {
    if (posts.length !== 0) {
      $("#recent_posts_from_author_section").removeClass("hidden");
      update_side_feed($("#recent_posts_from_author"), posts);
    }
  });
});
