FROM python:3.7.7-alpine3.11

ENV FLASK_APP sponsormatch.py
ENV FLASK_CONFIG docker

RUN adduser -D sponsormatch


WORKDIR /home/sponsormatch

COPY requirements.txt requirements.txt
RUN python3 -m venv venv

#Installing client libraries and any other package you need
RUN apk update && apk add libpq

#Install build dependencies
RUN apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev
RUN venv/bin/pip install -r requirements.txt

#Delete build dependencies
RUN apk del .build-deps

COPY app app
COPY migrations migrations
COPY tests tests
COPY sponsormatch.py config.py boot.sh ./
RUN chmod +x boot.sh

#switch users
USER sponsormatch

#runtime configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
