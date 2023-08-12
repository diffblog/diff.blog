import {
  setup_ajax,
  show_login_prompt_if_required,
  add_post_to_feed,
  shuffle,
  update_side_feed,
  get_feed_info,
} from "./helpers";
setup_ajax();

var follow_template = require("./../templates/small-follow.handlebars");

var latest_id;
var last_post_updated_on;
var last_post_score;
var post_ids = {};
var feed_fetch_in_progress = false;

function check_post_in_feed(post) {
  return post_ids.hasOwnProperty(post.id);
}

function update_feed(feed_info, posts) {
  feed_fetch_in_progress = false;
  for (let index in posts) {
    let post = posts[index];
    if (!check_post_in_feed(post)) {
      post.feed_info = feed_info;
      add_post_to_feed($("#home_feed"), post);
      post_ids[post.id] = true;
    }
  }
}

function set_menu_active_section(feed_info) {
  if (feed_info.feed === "main" && feed_info.sort_by === "top") {
    $('#feed-menu [name="top"]').addClass("is-active");
  } else if (feed_info.feed === "main" && feed_info.sort_by === "new") {
    $('#feed-menu [name="new"]').addClass("is-active");
  } else if (
    feed_info.feed === "user" &&
    feed_info.subcategory === "following" &&
    feed_info.sort_by === "new"
  ) {
    $('#feed-menu [name="following"]').addClass("is-active");
  }
}

function initialize_feed(feed_info) {
  post_ids = {};
  if (feed_info.feed === "user" && feed_info.subcategory === "following") {
    if (show_login_prompt_if_required("following_feed")) {
      return;
    }
    $.get("/api/posts/following", { topic: feed_info.topic }).done(
      function (posts) {
        $("#home_feed").html("");
        last_post_updated_on = posts[posts.length - 1].updated_on;
        update_feed(feed_info, posts);
      },
    );
  }

  if (feed_info.feed === "main" && feed_info.sort_by === "new") {
    $.get("/api/posts/new", { topic: feed_info.topic }).done(function (posts) {
      $("#home_feed").html("");
      last_post_updated_on = posts[posts.length - 1].updated_on;
      update_feed(feed_info, posts);
    });
  }

  if (feed_info.feed === "main" && feed_info.sort_by === "top") {
    $.get("/api/posts/top", { topic: feed_info.topic }).done(function (posts) {
      $("#home_feed").html("");
      last_post_score = posts[posts.length - 1].score;
      update_feed(feed_info, posts);
    });
  }

  if (feed_info.feed === "user" && feed_info.subcategory === "published") {
    $.get("/api/posts/user", { username: feed_info.username }).done(
      function (posts) {
        $("#home_feed").html("");
        if (posts.length !== 0) {
          last_post_score = posts[posts.length - 1].score;
          update_feed(feed_info, posts);
        }
      },
    );
  }

  if (feed_info.feed === "user" && feed_info.subcategory === "liked") {
    $.get("/api/posts/liked", { username: feed_info.username }).done(
      function (posts) {
        $("#home_feed").html("");
        if (posts.length !== 0) {
          last_post_score = posts[posts.length - 1].score;
          update_feed(feed_info, posts);
        }
      },
    );
  }
}

function initialize_menu_feed(feed_info) {
  post_ids = {};

  const is_new_feed = feed_info.feed === "main" && feed_info.sort_by === "new";
  const is_top_feed = feed_info.feed === "main" && feed_info.sort_by === "top";
  const is_following_feed =
    feed_info.feed === "user" && feed_info.subcategory === "following";

  if (is_top_feed || is_following_feed) {
    $.get("/api/posts/new", { topic: feed_info.topic, limit: 5 }).done(
      function (posts) {
        if (posts.length === 0) {
          return;
        }
        $("#recent_posts_section").removeClass("hidden");
        update_side_feed($("#recent_posts"), posts);
      },
    );
  }

  if (is_new_feed || is_following_feed) {
    $.get("/api/posts/top", { topic: feed_info.topic, limit: 5 }).done(
      function (posts) {
        if (posts.length === 0) {
          return;
        }
        $("#top_posts_section").removeClass("hidden");
        update_side_feed($("#top_posts"), posts);
      },
    );
  }

  if (is_new_feed || is_top_feed) {
    $.get("/api/posts/following", { topic: feed_info.topic, limit: 5 }).done(
      function (posts) {
        if (posts.length === 0) {
          return;
        }
        $("#following_posts_section").removeClass("hidden");
        update_side_feed($("#following_posts"), posts);
      },
    );
  }

  if (is_top_feed || is_new_feed) {
    $.ajax({
      method: "GET",
      url: "/api/users/suggestions",
      data: { limit: 2, topic: feed_info.topic },
      success: function (data) {
        if (data.length === 0) {
          return;
        }
        shuffle(data);
        var count = 0;
        for (let index in data) {
          var user = data[index];
          user["custom_size"] = "is-20";
          const html = follow_template(user);
          $("#right_sidebar_recommended_developers_follow_list").append(html);
          count++;
          if (count == 2) {
            break;
          }
        }
        $("#user_recommendations_section").removeClass("hidden");
      },
    });
  }
}

$(function () {
  const feed_info = get_feed_info();

  set_menu_active_section(feed_info);
  initialize_feed(feed_info);

  initialize_menu_feed(feed_info);

  $(window).scroll(function () {
    if (
      $(window).scrollTop() >=
        $(document).height() - $(window).height() - 2000 &&
      !feed_fetch_in_progress
    ) {
      feed_fetch_in_progress = true;
      if (feed_info.feed === "user" && feed_info.subcategory === "following") {
        $.get("/api/posts/following", {
          last_post_updated_on: last_post_updated_on,
          topic: feed_info.topic,
        }).done(function (posts) {
          last_post_updated_on = posts[posts.length - 1].updated_on;
          update_feed(feed_info, posts);
        });
      }
      if (feed_info.feed === "main" && feed_info.sort_by === "new") {
        $.get("/api/posts/new", {
          last_post_updated_on: last_post_updated_on,
          topic: feed_info.topic,
        }).done(function (posts) {
          last_post_updated_on = posts[posts.length - 1].updated_on;
          update_feed(feed_info, posts);
        });
      }
      if (feed_info.feed === "main" && feed_info.sort_by === "top") {
        $.get("/api/posts/top", {
          last_post_score: last_post_score,
          topic: feed_info.topic,
        }).done(function (posts) {
          last_post_score = posts[posts.length - 1].score;
          update_feed(feed_info, posts);
        });
      }
    }
  });

  $("#feed-menu .menu-item").on("click", function (e) {
    e.preventDefault();

    var new_feed_type = $(this).attr("name");
    if (
      new_feed_type === "following" &&
      show_login_prompt_if_required("following_feed")
    ) {
      return;
    }
    $('#feed-menu [name="new"').removeClass("is-active");
    $('#feed-menu [name="following"').removeClass("is-active");
    $('#feed-menu [name="top"').removeClass("is-active");

    $("#topic-info-header").css("display", "none");

    $("#feed-menu [name=" + new_feed_type + "]").addClass("is-active");
    if (new_feed_type !== "top") {
      history.pushState(
        new_feed_type,
        "diff.blog()",
        "/" + new_feed_type + "/",
      );
    } else {
      history.pushState(new_feed_type, "diff.blog()", "/");
    }
    initialize_feed(get_feed_info());
  });
});
