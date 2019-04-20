var template = require("./../templates/follow.handlebars")

$(function () {
    $.ajax({
        method: "GET",
        url: "/api/users/suggestions",
        success: function(data) {
            for (index in data) {
                var user = data[index];
                user["custom_size"] = "is-9"
                const html = template(user);
                $("#follow_list").append(html)
            }
        }
    })
});
