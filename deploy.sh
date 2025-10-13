#!/bin/bash
set -e

git config --global user.email "jowens@novuspower.com"
git config --global user.name "jowens25"

git submodule update --init --recursive

./scripts/build-deb.sh

# Find the most recent ns_*.deb file
LATEST_DEB=$(ls -t ns_*_arm64.deb 2>/dev/null | head -n1)

if [ -z "$LATEST_DEB" ]; then
    echo "Error: No .deb package found!"
    exit 1
fi

echo "Deploying package: $LATEST_DEB"

git clone git@github.com:jowens25/ns-package.git

cp $LATEST_DEB ../ns-package/$LATEST_DEB

cd ../ns-package

git add $LATEST_DEB
git commit -m "$LATEST_DEB"
git push