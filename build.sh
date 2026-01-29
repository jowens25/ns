fpm -s python -t deb \
    --name ns \
    --version 0.1.0 \
    --architecture all \
    --description "Network/System configuration tool" \
    --maintainer "Jacob <your.email@example.com>" \
    --url "https://github.com/yourusername/ns" \
    --license MIT \
    --depends python3 \
    --depends firewalld \
    --depends network-manager \
    --depends "python3 (>= 3.12)" \
    --python-package-name-prefix python3 \
    --python-bin python3 \
    --python-pip pip3 \
    --deb-priority optional \
    --category admin \
    pyproject.toml