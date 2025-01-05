FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    curl \
    python3.13 \
    python3.13-distutils \
    python3-pip \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python

RUN pip install pytest homeassistant pytest-homeassistant-custom-component

WORKDIR /app
# test

CMD ["python", "--version"]
