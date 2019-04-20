git fetch origin master
git reset --hard origin/master
sudo systemctl restart gunicorn
npm run-script build
