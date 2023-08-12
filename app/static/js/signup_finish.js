import { setup_ajax } from "./helpers";
setup_ajax();

$(function () {
  function reload_if_profile_setup_complete() {
    $.ajax({
      type: "GET",
      url: "/api/user/profile_setup_status",
      success: function (data) {
        if (data.fetched_following_users) {
          window.location = "/";
        } else {
          setTimeout(function () {
            reload_if_profile_setup_complete();
          }, 4000);
        }
      },
    });
  }

  $(".topic-option").on("click", function () {
    $(this).toggleClass("is-dark");
  });

  $("#submit-button").on("click", function () {
    var topic_ids = [];
    $("#topics-selection-box .is-dark").each(function () {
      topic_ids.push($(this).data("id"));
    });

    $.ajax({
      type: "POST",
      url: "/api/user/topics",
      data: {
        topic_ids: JSON.stringify(topic_ids),
      },
      success: function () {
        // Reload directly to home page. Not sure whether its worth
        // making users wait
        window.location = "/";
        $("#topics-selection-box").hide();
        $("#profile-scanning-box").show();
        setTimeout(function () {
          reload_if_profile_setup_complete();
        }, 4000);
      },
    });
  });
});
