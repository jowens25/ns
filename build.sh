#!/bin/bash
deactivate
# Clean previous builds
rm -rf dist/ build/ *.egg-info ns_*.deb

# Deactivate venv if active
deactivate 2>/dev/null || true

# Build Python wheel (platform independent) 
# Use system Python, not venv
/usr/bin/python3 -m build --wheel

# Use fpm to convert wheel to deb
fpm -s python -t deb \
    --name ns \
    --version 0.1.0 \
    --architecture all \
    --description "Network/System configuration tool" \
    --maintainer "Jacob" \
    --url "https://github.com/jowens25/ns" \
    --license MIT \
    --depends "python3 (>= 3.11)" \
    --depends python3-pip \
    --depends firewalld \
    --depends network-manager \
    --python-package-name-prefix python3 \
    --python-bin /usr/bin/python3 \
    --python-pip /usr/bin/pip3 \
    --python-install-lib /usr/lib/python3/dist-packages \
    --python-install-bin /usr/local/bin \
    --no-python-dependencies \
    --deb-priority optional \
    --category admin \
    dist/ns-0.1.0-py3-none-any.whl

echo "Package built: ns_0.1.0_all.deb"