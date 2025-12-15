FROM tiangolo/uvicorn-gunicorn:python3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential pkg-config  libsndfile1-dev libsamplerate0-dev ffmpeg

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN apt-get install -y  portaudio19-dev

RUN pip install madmom
RUN pip install BeatNet

COPY . /app