FROM ubuntu:22.04

RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    curl \
    python3.13 \
    python3.13-distutils \
    python3-pip \

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python

RUN pip install pytest homeassistant pytest-homeassistant-custom-component

WORKDIR /app

CMD ["python", "--version"]
