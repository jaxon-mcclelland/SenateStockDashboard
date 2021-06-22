FROM python:3.9.5-slim-buster

ENV dbUser root
ENV dbPwd root
ENV dbHost db
ENV dbName transactions

RUN apt-get update 
RUN apt-get install -y -qq default-libmysqlclient-dev g++ 
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD python3 getSenatorData.py

