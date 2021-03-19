FROM python:3.7.7-alpine3.11
WORKDIR /home/sponsormatch


RUN adduser -D sponsormatch


COPY requirements.txt requirements.txt
COPY app app
COPY sponsormatch.py config.py boot.sh ./


RUN apk update && apk add --virtual build-dependencies libpq gcc \
    && apk add python3-dev musl-dev postgresql-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apk del build-dependencies


COPY migrations migrations
RUN chmod +x boot.sh

#switch users
USER sponsormatch

#runtime configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
