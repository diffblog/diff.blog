FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY package.json /code/
RUN apt-get update && apt-get install -y nodejs && apt-get -y install npm && npm install -g npm && npm install -g n
RUN npm install
RUN apt-get install -y redis-server
RUN apt-get install -y sqlite3
RUN ./manage.py migrate
ENV DEVELOPMENT 1
COPY . /code/
