#FROM python:3.9-alpine
FROM python:3.9-slim-buster
MAINTAINER Yonatan Amitzur

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "/py-packages:$PYTHONPATH"

COPY ./requirements.txt /requirements.txt


#RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
#RUN apk add --update --no-cache --virtual .tmp-build-deps \
#      gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
#RUN apk del .tmp-build-deps

RUN mkdir /poco_grabber_api
WORKDIR /poco_grabber_api
COPY ./poco_grabber_api /poco_grabber_api

#RUN adduser -D user
RUN adduser user
USER user