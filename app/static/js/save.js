import { setup_ajax, show_login_prompt_if_required } from "./helpers";
setup_ajax();

$(function () {
  $("body").on("click", ".pocket_save_button", function (event) {
    if (show_login_prompt_if_required("save_to_pocket")) {
      return;
    }
    const button_elem = $(this);
    var post_id = button_elem.data("post-id");
    $.ajax({
      type: "POST",
      url: "/api/integrations/pocket/add",
      data: { post_id: post_id },
      success: function () {
        button_elem.html('<i class="fas fa-check-circle"></i>');
      },
      error: function (response) {
        if (response.responseJSON.message === "authorize pocket") {
          window.location = "/account/settings/integrations/";
        }
      },
    });
  });
});
