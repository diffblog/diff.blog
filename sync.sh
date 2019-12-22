git fetch origin master
git reset --hard origin/master
sudo systemctl restart gunicorn
npm install
pip install -r requirments.txt
npm run-script build
