var source = document.getElementById("follow-item-template").innerHTML;
var template = Handlebars.compile(source);

$(function () {
    $.ajax({
        type: "GET",
        url: "/api/user/following",
        data: {username: page_params.username},
        success: function (following) {
            for (index in following) {
                user = following[index];
                var html = template(user);
                $("#follow_list").append(html);
            }
        }
    });
});
