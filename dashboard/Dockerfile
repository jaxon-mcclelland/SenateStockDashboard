FROM python:3.9.5-slim-buster

RUN apt-get update 
RUN apt-get install -y -qq default-libmysqlclient-dev g++ 
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT ["./run.sh"]

