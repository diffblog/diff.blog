import { setup_ajax, show_login_prompt_if_required } from "./helpers";
setup_ajax();

$(function () {
  $("#home_feed").on("click", ".boost_button", function (event) {
    if (show_login_prompt_if_required()) {
      return;
    }
    var post_id = $(this).data("post-id");
    var upvotes_counter = $("#feed_upvotes_counter_" + post_id);
    var upvotes_count = upvotes_counter.text();
    upvotes_counter.text(parseInt(upvotes_count) + 1);

    $.ajax({
      type: "POST",
      url: "/api/admin/boost",
      data: { post_id: post_id },
      success: function () {},
    });
  });
});
