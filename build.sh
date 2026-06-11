#!/bin/bash
rm -rf dist/*

uv sync
# grab the version from the deb change log so the python and deb are the same...
ver="$(sed -n '1{s/^[^(]*(\([^)]*\)).*/\1/p;}' debian/changelog)"
sed -i "s/^version = \".*\"$/version = \"$ver\"/" pyproject.toml

sed -i "s/^var version string = \".*\"$/var version string = \"$ver\"/" src/ns2/backend/ns/cmd/version.go 
dpkg-buildpackage -us -uc -b

mv ../*.ddeb ../*.deb ../*.buildinfo ../*.changes dist/



#debsign -k ABF8C9E8DF6D4AFD02BA58DCBA050865951ED7DD
