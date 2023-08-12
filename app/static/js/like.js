import { setup_ajax, show_login_prompt_if_required } from "./helpers";
setup_ajax();

$(function () {
  $("body").on("click", ".vote_button", function (event) {
    if (show_login_prompt_if_required("upvote")) {
      return;
    }
    var already_upvoted = $(this).data("vote-upvoted");
    var post_id = $(this).data("post-id");
    var upvotes_counter = $("#feed_upvotes_counter_" + post_id);
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
      url: "/api/post/vote",
      data: { post_id: post_id },
      success: function () {},
    });
  });
});
