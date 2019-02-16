$(function () {
    var source = document.getElementById("feed-item-template").innerHTML;
    var template = Handlebars.compile(source);
    $.get("/api/posts", function (posts) {
        for (index in posts) {
            var html = template(posts[index]);
            $("#home_feed").append(html);
        }
    });
}); 