import { setup_ajax } from "./helpers";
setup_ajax();

function reload_if_feed_fetch_complete() {
  $.ajax({
    type: "GET",
    url: "/api/user/feed_status",
    success: function (data) {
      if (data.feed_status !== 1) {
        location.reload();
      } else {
        setTimeout(function () {
          reload_if_feed_fetch_complete();
        }, 4000);
      }
    },
  });
}

$(function () {
  $("#blog_setting_submit_button").on("click", function (e) {
    e.preventDefault();
    const blog_url = $("[name='blog_url']").val();
    $.ajax({
      url: "/api/user/update_blog_url",
      type: "POST",
      data: {
        blog_url: blog_url,
      },
      success: function () {
        $("#blog_settings_form").hide();
        $("#blog_settings_loading").show();

        setTimeout(function () {
          reload_if_feed_fetch_complete();
        });
      },
    });
  });
});
