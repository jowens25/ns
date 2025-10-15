FROM debian:bullseye

# Add arm64 architecture and install dependencies
RUN dpkg --add-architecture arm64 && apt-get update

RUN apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    unzip \
    gcc-aarch64-linux-gnu \
    g++-aarch64-linux-gnu \
    libc6-dev-arm64-cross \
    crossbuild-essential-arm64 \
    pkg-config \
    dpkg-dev \
    debhelper \
    apt-utils

RUN apt-get install -y \
    libpam0g-dev \
    libpam-modules-bin \
    libpam0g-dev:arm64 \
    libpam0g:arm64 \
    libpam-modules:arm64 \
    libc6:arm64 \
    libc6-dev:arm64 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update
RUN apt-get install nano

# Install Go
ENV GO_VERSION=1.24.4
RUN wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin

# Install Flutter
ENV FLUTTER_VERSION=3.35.2
ENV FLUTTER_HOME=/opt/flutter
RUN git clone --depth 1 --branch ${FLUTTER_VERSION} https://github.com/flutter/flutter.git ${FLUTTER_HOME}
RUN ${FLUTTER_HOME}/bin/flutter precache
ENV PATH=$PATH:${FLUTTER_HOME}/bin

# Clone the project
WORKDIR /root/Projects

COPY scripts/build-publish-deb.sh .

# Set default command
CMD ["/bin/bash"]