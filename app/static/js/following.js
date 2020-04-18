var template = require("./../templates/follow.handlebars");

$(function () {
    $.ajax({
        type: "GET",
        url: "/api/user/following",
        data: {username: page_params.profile_username},
        success: function (following) {
            for (index in following) {
                user = following[index];
                var html = template(user);
                var column = "<div class='column is-6'>" + html + "</div>";
                $("#follow_list").append(column);
            }
        }
    });
});
