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
                console.log(user)
                var html = template(user);
                $("#following_list").append(html);
            }
        }
    })
});