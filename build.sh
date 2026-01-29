#!/bin/bash

# Clean previous builds
rm -rf dist/ build/ *.egg-info ns_*.deb

# Build Python wheel (platform independent)
python -m build --wheel

# Use fpm to convert wheel to deb WITHOUT python dependencies
fpm -s python -t deb \
    --name ns \
    --version 0.1.0 \
    --architecture all \
    --description "Network/System configuration tool" \
    --maintainer "Jacob <your.email@example.com>" \
    --url "https://github.com/jowens25/ns" \
    --license MIT \
    --depends "python3 (>= 3.11)" \
    --depends python3-pip \
    --depends firewalld \
    --depends network-manager \
    --python-package-name-prefix python3 \
    --python-bin python3 \
    --python-pip pip3 \
    --no-python-dependencies \
    --deb-priority optional \
    --category admin \
    dist/ns-0.1.0-py3-none-any.whl

echo "Package built: ns_0.1.0_all.deb"