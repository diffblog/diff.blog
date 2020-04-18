git fetch origin master
git reset --hard origin/master
sudo systemctl restart gunicorn
npm install
pip install -r requirements.txt
npm run-script build
./manage.py collectstatic
