import { setup_ajax } from "./helpers";
setup_ajax();

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
  let html = `
  <div style="display: inline-block; margin-right: 10px; border-radius: 20px;
  box-shadow: 0px 2px 5px 0px rgb(0 52 102 / 11%); border: 0px solid #aaaaaa; padding: 10px;">
    <a href="${
      vote.mirror_url
    }" style="text-decoration:none; color: black; cursor: pointer;">
          <div style="margin-bottom: 3px; cursor: pointer;">
              <img src="${source_image_url}" style="border-radius: 50%; height: 16px; cursor: pointer;">
              <span style='font-size: 14px; cursor: pointer;'>${vote.source.toLowerCase()}</span>
          </div>
          <span style='margin-left: 20px; font-size: 12px; cursor: pointer;'>${
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
  style="">
  <div id="diffblog-plugin-votes-holder"></div>
</div>
`;
  return create_element_from_html(html);
}

function show_mirror_votes(
  plugin_public_api_key,
  encoded_blog_post_url,
  limit
) {
  if (limit === 0) {
    return;
  }
  if (!limit) {
    limit = 5;
  }

  const api_url = `/api/plugin/post_info`;
  let plugin_holder = document.getElementById("diffblog-votes");
  let plugin_div = create_plugin_div();
  plugin_holder.appendChild(plugin_div);
  let votes_holder = document.getElementById("diffblog-plugin-votes-holder");

  let data = {
    plugin_public_api_key: plugin_public_api_key,
    encoded_blog_post_url: encoded_blog_post_url,
  };

  $.ajax({
    type: "POST",
    url: api_url,
    data: data,
    success: function (json) {
      // console.log(response)
      // var json = JSON.parse(response);
      if (!json["diffblog_url"]) {
        return;
      }
      var discussed_on_text_holder = document.getElementById(
        "discussed-on-text-holder"
      );
      discussed_on_text_holder.style.display = "";
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
      mirror_posts.sort((a, b) => b.votes - a.votes);
      for (var i = 0; i < mirror_posts.length; i++) {
        if (i === limit - 1) {
          break;
        }
        votes_holder.appendChild(create_vote_div(mirror_posts[i]));
      }
    },
  });
}

document.getElementById("diffblogscript").addEventListener("load", function () {
  show_mirror_votes(
    document
      .getElementById("diffblogscript")
      .getAttribute("data-plugin-public-api-key"),
    document
      .getElementById("diffblogscript")
      .getAttribute("data-blog-post-url"),
    7
  );
});
