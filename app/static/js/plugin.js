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
  <div class="vote" style="display: inline-block !important; margin-right: 10px !important;">
      <span style='margin-top: 0px !important; padding-top: -15px !important;'>
          <div style="margin-bottom: -5px;">
              <img height="16" width="16" src="${source_image_url}" style="border-radius: 50%">
              <span style='font-size: 14px !important;'>${vote.source.toLowerCase()}</span>
          </div>
          <span style='margin-left: 20px !important; margin-top: -22px !important; font-size: 12px !important;'>${
            vote.votes
          }  points</span>
      </span>
  </div>
`;
  return create_element_from_html(html);
}

function create_plugin_div() {
  let html = `
<div
  style="border: solid; border-width: 1px; border-color: rgb(218, 213, 213); padding: 10px; padding-left: 10px; border-radius: 10px;">
</div>
`;
  return create_element_from_html(html);
}

function initialize_diffblog_plugin(plugin_holder_id, plugin_public_api_key) {
  //const post_url = window.location.href;
  const post_url = "https://feross.org/introducing-thanks/";

  const url_encoded_post_url = encodeURIComponent(post_url);
  const api_url = `http://localhost:8000/api/plugin/post_info?url=${url_encoded_post_url}&plugin_public_api_key=${plugin_public_api_key}`;
  let plugin_holder = document.getElementById(plugin_holder_id);
  let plugin_div = create_plugin_div();
  plugin_holder.appendChild(plugin_div);

  httpGetAsync(api_url, function (response) {
    var json = JSON.parse(response);
    if (!json["diffblog_url"]) {
      return;
    }
    const diffblog_entry = {
      votes: json["diffblog_aggregate_votes_count"],
      source: "diff.blog",
      url: json["diffblog_url"],
    };
    plugin_div.appendChild(create_vote_div(diffblog_entry));

    var mirror_posts = json["mirror_posts"];
    if (!mirror_posts || mirror_posts.length == 0) {
      return;
    }
    mirror_posts.sort((a, b) => b.votes - a.votes);
    for (var i = 0; i < mirror_posts.length; i++) {
      plugin_div.appendChild(create_vote_div(json["mirror_posts"][i]));
    }
  });
}
