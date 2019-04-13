#!/usr/bin/env bash
source bin/activate
./manage.py migrate
sudo /etc/init.d/nginx start    # start nginx
