#!/bin/bash
set -e

REPO_DIR="docs"
DIST="stable"
COMPONENT="main"
ARCH="amd64"

cd "$REPO_DIR"

# Create directory structure
mkdir -p pool/main
mkdir -p dists/$DIST/$COMPONENT/binary-$ARCH

# Generate Packages file
cd dists/$DIST/$COMPONENT/binary-$ARCH
dpkg-scanpackages -m ../../../../pool/main /dev/null > Packages
gzip -kf Packages

# Generate Release file
cd ../../..
cat > Release <<EOF
Origin: YourCompany
Label: YourCompany NS Tools
Suite: $DIST
Codename: $DIST
Architectures: $ARCH all
Components: $COMPONENT
Description: NS Serial Tools Repository
EOF

echo "Repository updated successfully"