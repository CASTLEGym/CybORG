# Set Ubuntu and Python versions from pre-built images
FROM ubuntu:22.10
FROM python:3.10.12

# Set working directory to /cage
WORKDIR /cage

# Copy local package requirements and init script into container's /cage folder
COPY . /cage

# Install system dependencies
# Mininet installation instructions recommend python-is-python3 on Ubuntu to link python to python3
# Packages that will be used to run actions shall be installed at this step as well
RUN apt-get update && apt-get install -y \
    git \
    openjdk-17-jdk \
    python3-pip \
    python3-dev \
    python-is-python3 \
    iproute2 \
    nmap \ 
    bind9 \
    bind9utils \
    bind9-doc \
    dnsutils \
    openvswitch-switch \
    xterm \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Mininet
RUN git clone git://github.com/mininet/mininet && \
    mininet/util/install.sh -nfv

# Install packages
RUN pip install -e .

# Example of adding additional instructions
# RUN pip install stable_baselines3

# Run evaluation script
ENTRYPOINT ["python", "/cage/CybORG/Evaluation/validation.py"]

