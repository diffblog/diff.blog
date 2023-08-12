FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y nodejs && apt-get -y install npm && npm install -g npm && npm install -g n
RUN n 14.17.0

# Ñeeded for node-gyp NPM package
RUN apt-get install -y python2

COPY package.json package-lock.json* /code/
RUN npm install

RUN apt-get install -y redis-server
RUN apt-get install -y sqlite3

ENV DEVELOPMENT 1
