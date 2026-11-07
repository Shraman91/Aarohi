# Dockerfile for AMERICAN WEDDING - Challenge 01 (PWN)
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    gcc-multilib \
    gdb \
    python3 \
    python3-pip \
    python3-dev \
    git \
    file \
    binutils \
    bash \
    netcat \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir pwntools

WORKDIR /challenge

COPY assets/binary/vuln.c /challenge/vuln.c
COPY assets/binary/flag.txt /challenge/flag.txt
COPY tools/build_binary.sh /challenge/build_binary.sh
COPY tools/solve_binary.py /challenge/solve_binary.py

RUN gcc -std=gnu99 -fno-stack-protector -no-pie -z execstack -Wno-deprecated-declarations -o /challenge/vuln /challenge/vuln.c

CMD ["/bin/bash"]

