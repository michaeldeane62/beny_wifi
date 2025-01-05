# Use a base Ubuntu image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    build-essential \
    curl \
    python3.10 \
    python3-pip \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.13 python3.13-dev

# Set Python 3.13 as the default Python version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1

# Install pip for Python 3.13
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python

RUN pip install setuptools --upgrade

# Install pytest, Home Assistant, and pytest-homeassistant-custom-component
RUN pip install pytest homeassistant pytest-homeassistant-custom-component

# Set working directory inside the container
WORKDIR /app

# Default command to verify Python installation
CMD ["python", "--version"]
