# syntax=docker/dockerfile:1
FROM python:3.9
LABEL maintainer="postgresql test"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY Pipfile.lock /code/
COPY Pipfile /code/

RUN apt-get update && \
    apt-get install ffmpeg postgresql postgresql-contrib -y


RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install pipenv && \
    /py/bin/pipenv install --deploy --system --ignore-pipfile

COPY . /code/

ENV PATH="/py/bin:$PATH"

CMD ./django_start.sh
