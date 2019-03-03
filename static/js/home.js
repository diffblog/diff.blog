var source = document.getElementById("feed-item-template").innerHTML;
var template = Handlebars.compile(source);
    
var latest_id;
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
    latest_id = posts[posts.length -1].id;
    for (index in posts) {
        post = posts[index];
        if (!check_post_in_feed(post)) {
            add_post_to_feed(post);
        }
    }

}

function set_menu_active_section() {
    var path = window.location.pathname;
    if (path === "/") {
        $("#following-option").addClass("is-active");
    }
    if (path === "/recommended/") {
        $("#recommended-option").addClass("is-active");
    }
    if (path === "/top/") {
        $("#top-option").addClass("is-active");
    }
    if (path === "/new/") {
        $("#new-option").addClass("is-active");
    }
}

$(function () {
    set_menu_active_section();

    $.get("/api/posts/following", function (posts) {
       update_feed(posts);
    });

    $(window).scroll(function () {
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
            $.get("/api/posts/following", {latest_id: latest_id}).done(function (posts) {
               update_feed(posts);
            })
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
});
