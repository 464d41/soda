FROM python:3.7.3-alpine3.9

ENV WORKDIR=/app

WORKDIR $WORKDIR

RUN echo "http://nl.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories && \
    apk update && \
    apk add hping3 && \
    rm -rf /var/cache/apk/*

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD . .

CMD ["python", "soda-docker.py"]
