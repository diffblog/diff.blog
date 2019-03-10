var template = require("./../templates/feed-item.handlebars");

var latest_id;
var last_post_updated_on;
var last_post_score;
var post_ids = [];

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

function get_feed_type() {
    var pathname = window.location.pathname;
    if (pathname === "/") {
        return "following";
    }
    if (pathname[0] === "/") {
        pathname = pathname.substr(1);
    }

    if (pathname[pathname.length - 1] === "/") {
        pathname = pathname.substring(0, pathname.length - 1);
    }
    return pathname;
}

function add_post_to_feed(post) {
    post.time = moment(post.updated_on).fromNow();
    var html = template(post);
    $("#home_feed").append(html);
    post_ids.push(post.id);
}

function check_post_in_feed(post) {
    return _.contains(post_ids, post.id);
}

function update_feed(posts) {
    for (index in posts) {
        post = posts[index];
        if (!check_post_in_feed(post)) {
            add_post_to_feed(post);
        }
    }

}

function set_menu_active_section() {
    var feed_type = get_feed_type();
    $("#feed-menu [name=" + feed_type + "]").addClass("is-active");
}

function initialize_feed() {
    var feed_type = get_feed_type();
    post_ids = [];
    if (feed_type === "following") {
        $.get("/api/posts/following", function (posts) {
            $("#home_feed").html("");
            last_post_updated_on = posts[posts.length -1].updated_on;
            update_feed(posts);
         });
    }

    if (feed_type === "new") {
        $.get("/api/posts/new", function (posts) {
            $("#home_feed").html("");
            last_post_updated_on = posts[posts.length -1].updated_on;
            update_feed(posts);
         });
    }

    if (feed_type === "top") {
        $.get("/api/posts/top", function (posts) {
            $("#home_feed").html("");
            last_post_score = posts[posts.length -1].score;
            update_feed(posts);
         });
    }
}

$(function () {
    set_menu_active_section();
    initialize_feed();

    $(window).scroll(function () {
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
            var feed_type = get_feed_type();
            if (feed_type === "following") {
                $.get("/api/posts/following", {last_post_updated_on: last_post_updated_on}).done(function (posts) {
                    last_post_updated_on = posts[posts.length -1].updated_on;
                    update_feed(posts);
                 })
            } else if (feed_type === "new") {
                $.get("/api/posts/new", {last_post_updated_on: last_post_updated_on}).done(function (posts) {
                    last_post_updated_on = posts[posts.length -1].updated_on;
                    update_feed(posts);
                 })
            } else if (feed_type === "top") {
            $.get("/api/posts/top", {last_post_score: last_post_score}).done(function (posts) {
                last_post_score = posts[posts.length -1].score;
                update_feed(posts);
             })
        }
        }
     });

    $("#home_feed").on("click", ".vote_button", function(event) {
        var already_upvoted = $(this).data("vote-upvoted");
        var post_id = $(this).data("post-id");
        var upvotes_counter = $("#feed_upvotes_counter_" + post_id);
        var upvotes_count = upvotes_counter.text()
        if (already_upvoted) {
            $(this).html('<i class="far fa-heart"></i>');
            $(this).data("vote-upvoted", false);
            upvotes_counter.text(parseInt(upvotes_count) - 1);

        } else {
            $(this).html('<i class="fas fa-heart"></i>');
            $(this).data("vote-upvoted", true);
            upvotes_counter.text(parseInt(upvotes_count) + 1);
        }
        $.ajax({
            type: "POST",
            url: "/api/post/vote",
            data: {"post_id": post_id},
            success: function() {
            }
        })
    });

    $("#feed-menu .menu-item").on("click", function() {
        var current_feed_type = get_feed_type();
        var new_feed_type = $(this).attr("name");
        $("#feed-menu [name=" + current_feed_type + "]").removeClass("is-active");
        $("#feed-menu [name=" + new_feed_type + "]").addClass("is-active");
        if (new_feed_type !== "following") {
            history.pushState(new_feed_type, "Diff.Blog()", "/" + new_feed_type + "/");
        } else {
            history.pushState(new_feed_type, "Diff.Blog()", "/");
        }
        initialize_feed();
    });

});
