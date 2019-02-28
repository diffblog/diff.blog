var source = document.getElementById("follow-item-template").innerHTML;
var template = Handlebars.compile(source);

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(function () {
    $.ajax({
        type: "GET",
        url: "/api/user/followers",
        data: {username: page_params.username},
        success: function (following) {
            for (index in following) {
                user = following[index];
                var html = template(user);
                $("#followers_list").append(html);
            }
        }
    })
});
