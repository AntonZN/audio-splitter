FROM python:3.10

RUN apt-get update && apt-get install -y ffmpeg libsndfile1 wget tar espeak

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt


RUN pip install --upgrade pip

COPY . /app

CMD ["python", "run.py"]