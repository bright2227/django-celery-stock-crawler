FROM python:3.7.2

ENV PYTHONUNBUFFERED 1

RUN mkdir /crawl
WORKDIR /crawl
COPY . /crawl
RUN pip install -r requirements.txt
