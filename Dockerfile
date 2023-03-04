FROM python:3.10-slim-bullseye AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

