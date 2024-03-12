FROM nvidia/cuda:12.3.2-runtime-ubuntu22.04

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MODEL_PATH /models

# SYSTEM
RUN apt-get update --yes --quiet && DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends \
    software-properties-common \
    build-essential apt-utils \
    wget curl vim git ca-certificates kmod \
    nvidia-driver-535 \
 && rm -rf /var/lib/apt/lists/*

# PYTHON 3.10
RUN add-apt-repository --yes ppa:deadsnakes/ppa && apt-get update --yes --quiet
RUN DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    python3.10-lib2to3 \
    python3.10-gdbm \
    python3.10-tk \
    pip

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 999 \
    && update-alternatives --config python3 && ln -s /usr/bin/python3 /usr/bin/python

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y ffmpeg libsndfile1 wget tar

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

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt


RUN pip install musdb museval
RUN pip install --default-timeout=100 spleeter

ENV LD_LIBRARY_PATH /usr/local/cuda/lib:/usr/local/cuda/lib64

COPY . /app

CMD ["python", "run.py"]