 <h1 class="text-3xl">Show votes from diff.blog, Hacker News and Reddit in your blog post!</h1>

<br>
<h1 class="text-2xl underline">
    Demo
</h1>
<hr >
<br>
<br>

<div id="diffblog-votes"></div>
<script id="diffblogscript" async src="/static/js/plugin.js"></script>
<script>
    document.getElementById("diffblogscript").addEventListener("load", function () {
        initialize_diffblog_plugin(
            plugin_holder_id = "diffblog-votes",
            plugin_public_api_key = "***REMOVED***",
            limit=7
        );
    });
</script>


<br>
<br>
<h2 class="text-2xl underline">
    Installation
</h2>

<br>
<h3 class="text-xl">
    1. Copy the code
</h3>
<br>

<pre class="rounded-lg bg-white">
    <code class="language-html">
        {{ code_snippet }}
    </code>
</pre>

<h3 class="text-xl">
    2. Paste it in the HTML template file of your blog post. That's it!
</h3>
<br>

<h2 class="text-2xl underline">
    Optional configuration
</h2>

<br>

<p>
    You can customize the plugin by passing the following optional parameters to <b class="font-medium">initialize_diffblog_plugin</b>.
</p>

<br>

<p>
    <h4 class="font-medium">limit (optional)</h4>
    Limit the number of sources to show the vote from. Sources are shown in descending order of votes. The default value of limit is 5.
</p>

<br>

<h4 class="font-medium">sources (optional)</h4>
You can also customize the plugin for each source.

This parameter takes an array of dicts. Each dict can have the following keys:
<div class="pl-5">
    <br>
    <ul>
        <li>
            <h5>name  (required)</h5>
            The name of the source.
            <br>
            
            The value can be one of "*", "diff.blog", "hacker news", "reddit", or the name of a subreddit.
        </li>
        <br>
        <li>
            <h5>url  (required)</h5>
            The url of the source.
        </li>
    </ul>
</div> 
