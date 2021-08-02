function httpGetAsync(theUrl, callback) {
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = function () {
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
      callback(xmlHttp.responseText);
  };
  xmlHttp.open("GET", theUrl, true); // true for asynchronous
  xmlHttp.send(null);
}

function create_vote_div_legacy(vote) {
  let vote_div = document.createElement("div");
  vote_div.className = "vote";
  vote_div.style.display = "inline-block";

  let source_image = document.createElement("img");
  source_image.height = "24";
  source_image.width = "24";
  switch (vote["source"]) {
    case "diff.blog":
      source_image.src =
        "https://diff.blog/static/images/icons/favicon-32x32.png";
      break;
    case "Hacker News":
      source_image.src = "https://diff.blog/static/images/hn.png";
      break;
    default:
      source_image.src = "https://diff.blog/static/images/reddit.png";
      break;
  }
  vote_div.appendChild(source_image);

  let details_span = document.createElement("span");
  details_span.style.display = "inline";
  vote_div.appendChild(details_span);

  let source_name_span = document.createElement("span");
  source_name_span.innerHTML = vote.source;
  source_name_span.style.display = "inline-block";
  details_span.appendChild(source_name_span);

  let vote_count_span = document.createElement("span");
  vote_count_span.innerHTML = vote.votes;
  vote_count_span.style.display = "inline-block";
  details_span.appendChild(vote_count_span);

  return vote_div;
}

function create_element_from_html(html) {
  const element = document.createElement("div");
  element.innerHTML = html.trim();
  return element.firstChild;
}

function get_source_image_url(source) {
  switch (source) {
    case "diff.blog":
      return "https://diff.blog/static/images/icons/favicon-32x32.png";
    case "Hacker News":
      return "https://diff.blog/static/images/hn.png";
    default:
      return "https://diff.blog/static/images/reddit.png";
  }
}

function create_vote_div(vote) {
  const source_image_url = get_source_image_url(vote.source);
  html = `
  <div style="all: initial; display: inline-block !important; margin-right: 10px !important;">
        <a href="${vote.mirror_url}" style="all: initial; text-decoration:none !important; color: black !important; cursor: pointer !important;">
          <div style="all: initial; margin-bottom: -5px; !important; cursor: pointer !important;">
              <img src="${source_image_url}" style="all: initial; border-radius: 50% !important; height: 16px; cursor: pointer !important;">
              <span style='all: initial; font-size: 14px !important; cursor: pointer !important;'>${vote.source.toLowerCase()}</span>
          </div>
          <br style="all: initial;">
          <span style='all: initial; margin-left: 20px !important; margin-top: -22px !important; font-size: 12px !important; cursor: pointer !important;'>${
            vote.votes
          }  points</span>
        </a>
  </div>
`;
  return create_element_from_html(html);
}

function create_plugin_div() {
  let html = `
<div
  style="all: initial; border: solid !important; border-width: 1px !important; border-color: rgb(218, 213, 213) !important; padding: 20px !important; padding-left: 10px !important; padding-top: 35px !important; border-radius: 10px !important;">
  <div id="diffblog-plugin-votes-holder" style="all: initial;"></div>
</div>
`;
  return create_element_from_html(html);
}

function initialize_diffblog_plugin(plugin_holder_id, plugin_public_api_key, limit=5) {
  if (limit === 0) {
    return;
  }

  //const post_url = window.location.href;
  const post_url = "https://deepmind.com/blog/article/generally-capable-agents-emerge-from-open-ended-play";

  const url_encoded_post_url = encodeURIComponent(post_url);
  const api_url = `http://localhost:8000/api/plugin/post_info?url=${url_encoded_post_url}&plugin_public_api_key=${plugin_public_api_key}`;
  let plugin_holder = document.getElementById(plugin_holder_id);
  let plugin_div = create_plugin_div();
  plugin_holder.appendChild(plugin_div);
  let votes_holder = document.getElementById("diffblog-plugin-votes-holder");

  httpGetAsync(api_url, function (response) {
    var json = JSON.parse(response);
    if (!json["diffblog_url"]) {
      return;
    }
    const diffblog_entry = {
      votes: json["diffblog_aggregate_votes_count"],
      source: "diff.blog",
      mirror_url: json["diffblog_url"],
    };
    votes_holder.appendChild(create_vote_div(diffblog_entry));

    var mirror_posts = json["mirror_posts"];
    if (!mirror_posts || mirror_posts.length == 0) {
      return;
    }
    console.log(mirror_posts)
    mirror_posts.sort((a, b) => b.votes - a.votes);
    for (var i = 0; i < mirror_posts.length; i++) {
      console.log(i)
      if (i === limit - 1) {
        break;
      }
      votes_holder.appendChild(create_vote_div(mirror_posts[i]));
    }
  });
}
