function create_iframe(plugin_public_api_key, blog_post_url) {
  const plugin_script = document.getElementById("diffblog-plugin-script");
  if (blog_post_url === undefined) {
    blog_post_url = window.location.href;
  }
  const url_encoded_blog_post_url = encodeURIComponent(blog_post_url);

  var iframe = document.createElement("iframe");
  var iframe_url =
    "https://diff.blog/plugin/iframe?plugin_public_api_key=" +
    plugin_public_api_key +
    "&url_encoded_blog_post_url=" +
    url_encoded_blog_post_url;
  iframe.setAttribute("src", iframe_url);
  iframe.setAttribute(
    "style",
    "width: 1px; min-width: 100%; border: none; user-select: none; visibility: visible;"
  );
  const iframe_holder = document.createElement("div");
  plugin_script.parentNode.insertBefore(
    iframe_holder,
    plugin_script.nextSibling
  );
  iframe_holder.appendChild(iframe);
}

function DiffBlog(plugin_public_api_key, blog_post_url) {
  create_iframe(plugin_public_api_key, blog_post_url);
}
