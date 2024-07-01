FROM alpine:latest

RUN apk add --no-cache \
    g++ \
    python3 \
    openjdk11-jre

RUN ln -sf python3 /usr/bin/python

RUN python --version && \
    g++ --version && \
    java -version

WORKDIR /workspace