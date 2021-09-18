#FROM python:3.9-alpine
FROM python:3.9-slim-buster
MAINTAINER Yonatan Amitzur

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
#RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
#RUN apk add --update --no-cache --virtual .tmp-build-deps \
#      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
#RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

#RUN adduser -D user
RUN adduser user
USER user