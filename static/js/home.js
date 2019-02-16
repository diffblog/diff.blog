var source = document.getElementById("feed-item-template").innerHTML;
var template = Handlebars.compile(source);
    
var latest_id;
var post_ids = [];

function is_in_array(value, array) {
    return array.indexOf(value) > -1;
}

function add_post_to_feed(post) {
    var html = template(post);
    $("#home_feed").append(html);
    post_ids.push(post.id);
}

function check_post_in_feed(post) {
    return is_in_array(post.id, post_ids);
}

$(function () {
    $.get("/api/posts", function (posts) {
        for (index in posts) {
            var html = template(posts[index]);
            $("#home_feed").append(html);
        }
        latest_id = posts[posts.length -1].id;
    });

    $(window).scroll(function () { 
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
            $.get("/api/posts", {latest_id: latest_id}).done(function (posts) {
                for (index in posts) {
                    post = posts[index];
                    if (!check_post_in_feed(post)) {
                        add_post_to_feed(post);
                    }
                }
                latest_id = posts[posts.length -1].id;
            })
        }
     });
});
