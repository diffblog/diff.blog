var template = require("./../templates/follow-legacy.handlebars")

$(function () {
    $.ajax({
        method: "GET",
        url: "/api/users/suggestions",
        success: function(data) {
            for (index in data) {
                var user = data[index];
                user["custom_size"] = "is-9"
                user["show_topics"] = true
                const html = template(user);
                $("#user_list").append(html)
            }
        }
    })
});
