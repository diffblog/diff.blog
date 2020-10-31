import { setup_ajax } from "./helpers";
setup_ajax();

var follow_button_template = require("./../templates/follow_button.handlebars");

$(function () {
  $("#follow_button").html(follow_button_template(page_params));
});
