FROM python:3.10-slim-bullseye AS base
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "calheinz/cli.py", "poll", "/data"]
