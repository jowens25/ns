#!/bin/bash
set -e

VERSION=${1:-1.0.2}
PACKAGE_NAME="ns"
BUILD_DIR="build"
DEB_DIR="$BUILD_DIR/debian"

echo "Building version $VERSION..."

# Clean previous builds
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Build Flutter web
(
    echo "Building Flutter web..."
    cd ns-ui
    flutter build web --release
)

# Go build
(
    echo "Starting go build..."
    cd ns-cli
    go mod download
    CGO_ENABLED=1 \
    GOOS=linux \
    GOARCH=arm64 \
    CC=aarch64-linux-gnu-gcc \
    go build -o ../build/ns ./cli
)

# Verify binary was created
if [ ! -f "$BUILD_DIR/ns" ]; then
    echo "Error: Go binary not found at $BUILD_DIR/ns"
    exit 1
fi

# Verify Flutter web build exists
if [ ! -d "ns-ui/build/web" ]; then
    echo "Error: Flutter web build not found at ns-ui/build/web"
    exit 1
fi

# Create debian package structure
mkdir -p $DEB_DIR

# Copy debian structure
if [ ! -d "debian" ]; then
    echo "Error: debian/ directory not found"
    exit 1
fi
cp -r debian/* $DEB_DIR/

# Update version in control file
sed -i "s/Version: .*/Version: $VERSION/" $DEB_DIR/DEBIAN/control

# Create package directory structure
mkdir -p $DEB_DIR/usr/bin
mkdir -p $DEB_DIR/usr/share/ns/web
mkdir -p $DEB_DIR/etc/nginx
mkdir -p $DEB_DIR/etc/snmp
mkdir -p $DEB_DIR/etc/nginx/ssl
mkdir -p $DEB_DIR/etc/systemd/system

# Copy binary to package structure
cp $BUILD_DIR/ns $DEB_DIR/usr/bin/ns

# Copy Flutter web assets to package structure
cp -r ns-ui/build/web/* $DEB_DIR/usr/share/ns/web/

# Copy configuration files to package structure
if [ -f "configs/nginx.conf" ]; then
    cp configs/nginx.conf $DEB_DIR/etc/nginx/nginx.conf
    echo "Included nginx.conf"
fi


# Copy configuration files to package structure
if [ -f "configs/snmpd.conf" ]; then
    cp configs/snmpd.conf $DEB_DIR/etc/snmp/snmpd.conf
    echo "Included snmpd.conf"
fi

# Set permissions
chmod 755 $DEB_DIR/usr/bin/ns

# Set config file permissions
find $DEB_DIR/etc -type f -name "*.conf" -exec chmod 644 {} \;
find $DEB_DIR/etc -type f -name "*.cfg" -exec chmod 644 {} \;
find $DEB_DIR/etc -type f -name "*.json" -exec chmod 644 {} \;
[ -f "$DEB_DIR/etc/systemd/system/ns.service" ] && chmod 644 $DEB_DIR/etc/systemd/system/ns.service

# Set permissions for control scripts (only if they exist)
[ -f "$DEB_DIR/DEBIAN/postinst" ] && chmod 755 $DEB_DIR/DEBIAN/postinst
[ -f "$DEB_DIR/DEBIAN/prerm" ] && chmod 755 $DEB_DIR/DEBIAN/prerm
[ -f "$DEB_DIR/DEBIAN/postrm" ] && chmod 755 $DEB_DIR/DEBIAN/postrm

# Update architecture in control file to match build
sed -i "s/Architecture: .*/Architecture: arm64/" $DEB_DIR/DEBIAN/control

# Build the deb package
dpkg-deb --build $DEB_DIR "${PACKAGE_NAME}_${VERSION}_arm64.deb"

echo "Package built successfully: ${PACKAGE_NAME}_${VERSION}_arm64.deb"

# Optional: Show package info
echo "Package info:"
dpkg-deb --info "${PACKAGE_NAME}_${VERSION}_arm64.deb"
echo "Package contents:"
dpkg-deb --contents "${PACKAGE_NAME}_${VERSION}_arm64.deb"