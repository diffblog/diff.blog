import pdb
from django.core.management.base import BaseCommand, CommandError
from app.models import Topic, UserProfile, UserList, Post

from diffblog.secrets import diffblog_github_access_token

import requests as r
import json

headers = {"Authorization": "token {}".format(diffblog_github_access_token)}


import requests
import base64
import json
import datetime


def push_to_repo_branch(content, gitHubFileName, repo_slug, branch, user, token):
    """
    Push file update to GitHub repo

    :param gitHubFileName: the name of the file in the repo
    :param fileName: the name of the file on the local branch
    :param repo_slug: the github repo slug, i.e. username/repo
    :param branch: the name of the branch to push the file to
    :param user: github username
    :param token: github user token
    :return None
    :raises Exception: if file with the specified name cannot be found in the repo
    """

    message = "Automated update " + str(datetime.datetime.now())
    path = "https://api.github.com/repos/%s/branches/%s" % (repo_slug, branch)

    r = requests.get(path, auth=(user, token))
    if not r.ok:
        print("Error when retrieving branch info from %s" % path)
        print("Reason: %s [%d]" % (r.text, r.status_code))
        raise
    rjson = r.json()
    treeurl = rjson["commit"]["commit"]["tree"]["url"]
    r2 = requests.get(treeurl, auth=(user, token))
    if not r2.ok:
        print("Error when retrieving commit tree from %s" % treeurl)
        print("Reason: %s [%d]" % (r2.text, r2.status_code))
        raise
    r2json = r2.json()
    sha = None

    for file in r2json["tree"]:
        # Found file, get the sha code
        if file["path"] == gitHubFileName:
            sha = file["sha"]

    # if sha is None after the for loop, we did not find the file name!
    if sha is None:
        print("Could not find " + gitHubFileName + " in repos 'tree' ")
        raise Exception

    # gathered all the data, now let's push
    inputdata = {}
    inputdata["path"] = gitHubFileName
    inputdata["branch"] = branch
    inputdata["message"] = message
    inputdata["content"] = base64.b64encode(content.encode("ascii")).decode("ascii")
    if sha:
        inputdata["sha"] = str(sha)

    updateURL = (
        "https://api.github.com/repos/diffblogbot/diffblogbot/contents/"
        + gitHubFileName
    )
    try:
        rPut = requests.put(updateURL, auth=(user, token), data=json.dumps(inputdata))
        if not rPut.ok:
            print("Error when pushing to %s" % updateURL)
            print("Reason: %s [%d]" % (rPut.text, rPut.status_code))
            raise Exception
    except requests.exceptions.RequestException as e:
        print(rPut)
        print(e)


class Command(BaseCommand):
    help = "Update slugs of all existing posts"

    def handle(self, *args, **options):
        blog_count = (
            UserProfile.objects.exclude(blog_url__isnull=True)
            .exclude(blog_url__exact="")
            .count()
        )

        gist_md = """
Hello :wave: :wave:

Over the past decade, we have seen the rise of centralized publishing platforms like Medium.  A lot of self hosted blogs were migrated to these platforms in hope of a bigger audience. Sadly, most of these blogs lost their unique identity and became just another page on them.

Our mission is to fight back against monopolies like Medium and promote independent self hosted blogs like yours. We think the best way to make this happen is by improving the visibility and reach of self hosted blogs. And that's why we built [diff.blog](https://diff.blog).

diff.blog is an aggregator of developer blogs. It was started in 2019 to improve the visibility of self hosted blogs. Whenever you publish a new blog post on your blog, it would automatically appear in the diff.blog news feed. The title and summary of the post would be visible to the users of diff.blog and they can click on the post to read the full post on your blog.

We also have a weekly email digest, which would email the most popular blog posts in our index to all diff.blog users.

diff.blog index over **{blog_count}** blogs at the moment. And our network is growing steadily every day. And we would like to invite you to include your blog in diff.blog as well.

Adding your blog to diff.blog is super easy and takes less than a minute.
* Go to https://diff.blog
* Sign up with your GitHub account.
* Go to blog settings https://diff.blog/account/settings/blog/
* Add the URL of your blog

We are looking forward to have your blog in diff.blog. Let us know if you have any questions. Happy to answer.
    """.format(
            blog_count=blog_count
        )

        push_to_repo_branch(
            gist_md,
            "README.md",
            "diffblogbot/diffblogbot",
            "main",
            "diffblogbot",
            diffblog_github_access_token,
        )
