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

    $(".vote_button").unbind("click");
    $(".vote_button").on("click", function(event) {
        $.ajax({
            type: "POST",
            url: "/api/post/vote",
            data: {"post_id": $(this).data("post-id")},
            success: function() {
                console.log("done")
            }
        })
    });
}

$(function () {
    $.get("/api/posts", function (posts) {
       update_feed(posts);
    });

    $(window).scroll(function () { 
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
            $.get("/api/posts", {latest_id: latest_id}).done(function (posts) {
               update_feed(posts);
            })
        }
     });

});
