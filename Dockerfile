FROM tiangolo/uvicorn-gunicorn:python3.10-slim

RUN apt-get update && apt-get install -y ffmpeg libsndfile1 wget tar

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MODEL_PATH /models

RUN mkdir -p /models

WORKDIR /models

RUN wget https://github.com/deezer/spleeter/releases/download/v1.4.0/2stems.tar.gz && \
    tar -zxvf 2stems.tar.gz && \
    rm 2stems.tar.gz

RUN wget https://github.com/deezer/spleeter/releases/download/v1.4.0/4stems.tar.gz && \
    tar -zxvf 4stems.tar.gz && \
    rm 4stems.tar.gz

RUN wget https://github.com/deezer/spleeter/releases/download/v1.4.0/5stems.tar.gz && \
    tar -zxvf 5stems.tar.gz && \
    rm 5stems.tar.gz

WORKDIR /app
RUN pip install --upgrade pip
RUN pip install musdb museval spleeter

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./app /app/app
COPY ./tasks /app/tasks
COPY ./tasks.py /app/tasks.py
COPY ./pyproject.toml /app/pyproject.toml
