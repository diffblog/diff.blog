import {
  setup_ajax,
  show_login_prompt_if_required,
  send_event,
} from "./helpers";
setup_ajax();

function toggle_button_classes(elem) {
  elem.toggleClass("follow");
  elem.toggleClass("following");

  elem.toggleClass("text-white");
  elem.toggleClass("bg-gray-900");
  elem.toggleClass("hover:bg-gray-800");

  elem.toggleClass("border-gray-400");
  elem.toggleClass("hover:border-gray-500");
}

$(function () {
  $("body").on("click", ".following", function () {
    if (show_login_prompt_if_required()) {
      return;
    }
    send_event("unfollow");

    $(this).text("Follow");
    toggle_button_classes($(this));

    $.ajax({
      type: "DELETE",
      url: "/api/user/following",
      data: { user_id: $(this).data("user-id") },
      success: function (response) {},
    });
  });
  $("body").on("click", ".follow", function () {
    if (show_login_prompt_if_required()) {
      return;
    }
    send_event("follow");

    $(this).text("Following");
    toggle_button_classes($(this));

    $.ajax({
      type: "POST",
      url: "/api/user/following",
      data: { user_id: $(this).data("user-id") },
      success: function (response) {},
    });
  });
});
