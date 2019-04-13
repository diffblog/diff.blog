#!/usr/bin/env bash
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install build-essential libssl-dev

# Install python3.6
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.6

# Install PIP
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.6 get-pip.py

# Install NVM, Node and NPM
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash
source ~/.profile
nvm install 10.15.3
nvm use 10.15.3

# Install node packages
npm install

# Setup virtualenv and install python packages
pip install virtualenv
virtualenv -p python3.6 .
source bin/activate
pip install -r requirements.txt

# Generate secrets.py
cp -n diffblog/secrets.py.template diffblog/secrets.py
