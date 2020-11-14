var template = require("./../templates/user-suggestion.handlebars");

$(function () {
  $.ajax({
    type: "GET",
    url: "/api/user/followers",
    data: { username: page_params.profile_username },
    success: function (following) {
      for (index in following) {
        user = following[index];
        var html = template(user);
        $("#follow_list").append(html);
      }
    },
  });
});
