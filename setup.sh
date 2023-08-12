#!/bin/bash

# Copy files if they don't exist
[ ! -f diffblog/secrets.py ] && cp diffblog/secrets_default.py diffblog/secrets.py
[ ! -f feed/blacklist.py ] && cp feed/blacklist_template.py feed/blacklist.py

python manage.py migrate

./manage.py loaddata all_data.json
