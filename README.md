## Dev Environment Setup

### Install docker-compose

https://docs.docker.com/compose/install/

### Set up config files
* Create `diffblog/secrets.py` using the secrets_default.py template
    * The bare minimum secrets are
        * `diffblog_github_access_token`
        * `social_auth_github_key` and `social_auth_github_secret`
        * All the reddit keys for syncing upvotes
* Create `blacklist.py` file with `users = []`


### Start the development server
```bash
docker-compose up
```

### Populate users with RSS feed URLs
Run inside the docker container

```bash
./manage.py update_recommended_blog_list
```

### Populate blog posts from RSS feeds
Run inside the docker container.

Note: You can stop this command in between since this might take a while to fully complete.

```bash
./mange.py sync_posts
```

### Generate popular topics
Run inside the docker container.

```bash
./manage.py generate_popular_topics
```
