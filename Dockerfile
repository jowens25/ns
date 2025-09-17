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
    debhelper

RUN apt-get install -y \
    libpam0g-dev \
    libpam-modules-bin \
    libpam0g-dev:arm64 \
    libpam0g:arm64 \
    libpam-modules:arm64 \
    libc6:arm64 \
    libc6-dev:arm64 \
    && rm -rf /var/lib/apt/lists/*

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
ARG CACHEBUST=1
RUN echo "Cache bust: $CACHEBUST" && git clone --recurse-submodules https://github.com/jowens25/ns.git
WORKDIR /root/Projects/ns

# Build arguments and environment
ARG VERSION=1.0.0
ENV PACKAGE_NAME="ns"
ENV BUILD_DIR="build"
ENV DEB_DIR="$BUILD_DIR/debian"

# Clean and prepare build directory
RUN rm -rf $BUILD_DIR && mkdir -p $DEB_DIR

# Copy debian structure and update version
RUN cp -r debian/* $DEB_DIR/ && \
    sed -i "s/Version: .*/Version: $VERSION/" $DEB_DIR/DEBIAN/control

# Download Go dependencies (cacheable)
RUN cd ns-cli && go mod download

# Build Flutter web
RUN cd ns-ui && flutter build web --release

# Build Go CLI
RUN cd ns-cli && \
    CGO_ENABLED=1 \
    GOOS=linux \
    GOARCH=arm64 \
    CC=aarch64-linux-gnu-gcc \
    go build -o "../$BUILD_DIR/ns" ./cli

# Create package directories
RUN mkdir -p $DEB_DIR/usr/bin && \
    mkdir -p $DEB_DIR/usr/share/ns/web

# Copy binaries and assets
RUN cp $BUILD_DIR/ns $DEB_DIR/usr/bin/
RUN cp -r ns-ui/build/web/* $DEB_DIR/usr/share/ns/web/

# Set permissions
RUN chmod 755 $DEB_DIR/DEBIAN/postinst && \
    chmod 755 $DEB_DIR/DEBIAN/prerm && \
    chmod 755 $DEB_DIR/DEBIAN/postrm && \
    chmod 755 $DEB_DIR/usr/bin/ns

# Build the deb package
RUN dpkg-deb --build $DEB_DIR "${PACKAGE_NAME}_${VERSION}_arm64.deb" && \
    echo "Package built: ${PACKAGE_NAME}_${VERSION}_arm64.deb"

# Set default command
CMD ["/bin/bash"]