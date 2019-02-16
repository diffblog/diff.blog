$(function () {
    var source = document.getElementById("feed-item-template").innerHTML;
    var template = Handlebars.compile(source);
    $.get("/api/posts", function (posts) {
        for (index in posts) {
            var html = template(posts[index]);
            $("#home_feed").append(html);
        }
    });

    $(window).scroll(function () { 
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
            $.get("/api/posts", function (posts) {
                for (index in posts) {
                    var html = template(posts[index]);
                    $("#home_feed").append(html);
                }
            });
        }
     });
});
