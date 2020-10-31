## Dev Environment Setup

### Install docker-compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Set up config files
* Create `diffblog/secrets.py` using the secrets_default.py template
    * The bare minimum secrets are
        * `diffblog_github_access_token`
        * `social_auth_github_key` and `social_auth_github_secret`
        * All the reddit keys for syncing upvotes
* Create `blacklist.py` file with `users = []`


### Start the development server
```bash
sudo docker-compose up

# Then attach shell to the diffblog_web docker container

./manage.py migrate
npm install
# Might want to comment out populate_user_profile_details_serial
./manage.py update_recommended_blog_list
./mange.py sync_posts
```
