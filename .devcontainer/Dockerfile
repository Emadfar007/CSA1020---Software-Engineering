FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04
USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3 openssh-server ca-certificates curl git \
    && rm -rf /var/lib/apt/lists/*
USER vscode
