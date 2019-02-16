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

function shuffle(array) {
    var currentIndex = array.length, temporaryValue, randomIndex;
  
    // While there remain elements to shuffle...
    while (0 !== currentIndex) {
  
      // Pick a remaining element...
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex -= 1;
  
      // And swap it with the current element.
      temporaryValue = array[currentIndex];
      array[currentIndex] = array[randomIndex];
      array[randomIndex] = temporaryValue;
    }
  
    return array;
  }

$(function () {
    $.get("/api/posts", function (posts) {
        latest_id = posts[posts.length -1].id;
        posts = shuffle(posts);
        for (index in posts) {
            var html = template(posts[index]);
            $("#home_feed").append(html);
        }
    });

    $(window).scroll(function () { 
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 10) {
            $.get("/api/posts", {latest_id: latest_id}).done(function (posts) {
                latest_id = posts[posts.length -1].id;
                posts = shuffle(posts);
                for (index in posts) {
                    post = posts[index];
                    if (!check_post_in_feed(post)) {
                        add_post_to_feed(post);
                    }
                }
            })
        }
     });
});
