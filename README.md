## Dev Environment Setup

### Install docker-compose

https://docs.docker.com/compose/install/linux/

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

### Populate users
```
./manage.py update_recommended_blog_list
```

### Populate blogs
```
./mange.py sync_posts
```
