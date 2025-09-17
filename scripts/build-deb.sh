#!/bin/bash
set -e
git clone --recurse-submodules https://github.com/jowens25/ns.git

VERSION=${1:-1.0.0}
PACKAGE_NAME="ns"
BUILD_DIR="build"
DEB_DIR="$BUILD_DIR/debian"

echo "Building version $VERSION..."

# Clean previous builds
rm -rf $BUILD_DIR
mkdir -p $DEB_DIR

# Copy debian structure
cp -r debian/* $DEB_DIR/

# Update version in control file
sed -i "s/Version: .*/Version: $VERSION/" $DEB_DIR/DEBIAN/control

# Build Flutter web
echo "Building Flutter web..."
(
  cd ns-ui
  flutter build web --release
)

cd ns-cli

go mod download

echo "Starting go build ..."
(
  CGO_ENABLED=1 \
  GOOS=linux \
  GOARCH=arm64 \
  CC=aarch64-linux-gnu-gcc \
  go build -o "../$BUILD_DIR/ns" ./cli
)


# Copy assets to package structure
mkdir -p $DEB_DIR/usr/bin
mkdir -p $DEB_DIR/usr/share/ns/web

cp $BUILD_DIR/ns $DEB_DIR/usr/bin/
cp -r flutter-app/build/web/* $DEB_DIR/usr/share/ns/web/

# Set permissions
chmod 755 $DEB_DIR/DEBIAN/postinst
chmod 755 $DEB_DIR/DEBIAN/prerm
chmod 755 $DEB_DIR/DEBIAN/postrm
chmod 755 $DEB_DIR/usr/bin/ns

# Build the deb package
dpkg-deb --build $DEB_DIR "${PACKAGE_NAME}_${VERSION}_arm64.deb"

echo "Package built: ${PACKAGE_NAME}_${VERSION}_arm64.deb"