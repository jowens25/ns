#!/bin/bash
# build-deb.sh

set -e  # Exit on error

# Clean previous builds
rm -rf dist/ ns_*.deb

echo "Building wheel with Poetry..."
poetry build

echo "Converting wheel to .deb with fpm..."
fpm -s python -t deb \
    --name ns \
    --version 0.2.3 \
    --architecture all \
    --description "Novus power products server configuration tool" \
    --maintainer "Jacob Owens <jaowens14@protonmail.com>" \
    --url "https://github.com/jowens25/ns" \
    --license MIT \
    --depends "python3 (>= 3.11)" \
    --depends python3-pip \
    --depends firewalld \
    --depends network-manager \
    --python-bin /usr/bin/python3 \
    --python-install-lib /usr/lib/python3/dist-packages \
    --python-install-bin /usr/local/bin \
    dist/ns-0.2.3-py3-none-any.whl

echo "✅ Package built: ns_0.2.3_all.deb"
ls -lh ns_0.2.3_all.deb