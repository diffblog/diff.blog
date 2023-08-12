var feed_item_template = require("./../templates/feed-item.handlebars");
var side_feed_item_template = require("./../templates/side-feed-item.handlebars");
var dayjs = require("dayjs");
var relativeTime = require("dayjs/plugin/relativeTime");
dayjs.extend(relativeTime);

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
}

export function setup_ajax() {
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader(
          "X-CSRFToken",
          document.getElementsByName("csrfmiddlewaretoken")[0].value,
        );
      }
    },
  });
}

export function show_login_prompt_if_required(action) {
  if (!logged_in) {
    const action_to_message = {
      boost: "Join to boost this post",
      following_feed: "Join to access following feed",
      follow: "Join to follow users",
      follow_topic: "Join to follow topics",
      upvote: "Join to like posts",
      add_comment: "Join to comment",
      save_to_pocket: "Join to save to Pocket",
    };
    document.getElementById("join-message").innerText =
      action_to_message[action];
    $("#signup-prompt-modal").addClass("is-active");
  }
  return !logged_in;
}

export function get_feed_info() {
  const pathname = window.location.pathname;

  if (pathname.match(/^\/$/)) {
    return { feed: "main", sort_by: "top", topic: "" };
  }

  if (pathname.match(/^\/new\/$/)) {
    return { feed: "main", sort_by: "new", topic: "" };
  }

  if (pathname.match(/^\/following\/$/)) {
    return {
      feed: "user",
      subcategory: "following",
      sort_by: "new",
      topic: "",
    };
  }

  let matches = pathname.match(/^\/tag\/(?<token>[^ $]*)\/top\/$/);
  if (matches) {
    return { feed: "main", sort_by: "top", topic: matches.groups.token };
  }

  matches = pathname.match(/^\/tag\/(?<token>[^ $]*)\/new\/$/);
  if (matches) {
    return { feed: "main", sort_by: "new", topic: matches.groups.token };
  }

  matches = pathname.match(/^\/tag\/(?<token>[^ $]*)\/following\/$/);
  if (matches) {
    return {
      feed: "user",
      subcategory: "following",
      sort_by: "new",
      topic: matches.groups.token,
    };
  }

  matches = pathname.match(/^\/tag\/(?<token>[^ $]*)\/users\/$/);
  if (matches) {
    return { feed: "user_recommendations", topic: matches.groups.token };
  }

  if (pathname.match(/^\/users\/recommended\/$/)) {
    return {
      feed: "user_recommendations",
      topic: "",
    };
  }

  if ("page_params" in window && page_params.profile_username) {
    let expression = new RegExp("^/" + page_params.profile_username + "/$");
    matches = expression.exec(pathname);
    if (matches) {
      return {
        feed: "user",
        subcategory: "published",
        sort_by: "new",
        username: page_params.profile_username,
      };
    }

    expression = new RegExp("^/" + page_params.profile_username + "/liked/$");
    matches = expression.exec(pathname);
    if (matches) {
      return {
        feed: "user",
        subcategory: "liked",
        sort_by: "new",
        username: page_params.profile_username,
      };
    }
  }
  return {};
}

export function add_post_to_feed(feed, post) {
  post.time = dayjs().to(post.updated_on);
  post.is_admin = is_admin;
  post.show_pocket = pocket_show_button || !logged_in;
  if (post.cover_photo_url) {
    post.cover_photo_url =
      "http://localhost:8888/unsafe/200x133/" +
      window.encodeURIComponent(post.cover_photo_url);
  }
  var html = feed_item_template(post);
  feed.append(html);
}

export function add_post_to_side_feed(feed, post) {
  var html = side_feed_item_template(post);
  feed.append(html);
}

export function update_side_feed(feed, posts) {
  for (let index in posts) {
    let post = posts[index];
    add_post_to_side_feed(feed, post);
  }
}

export function shuffle(array) {
  // From https://stackoverflow.com/a/2450976/2791111

  var currentIndex = array.length,
    temporaryValue,
    randomIndex;

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
