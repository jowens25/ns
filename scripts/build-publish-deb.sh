#!/bin/bash
set -e

git config --global user.email "jowens@novuspower.com"
git config --global user.name "jowens25"

git clone --recurse-submodules git@github.com:jowens25/ns.git

#git submodule update --init --recursive

cd ns

git checkout main
git pull origin main


MAJOR="1"
MINOR=$(git rev-list --count HEAD --merges)
PATCH=$(git rev-list --count HEAD)

VERSION="${MAJOR}.${MINOR}.${PATCH}"

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

    MINOR=$(git rev-list --count HEAD --merges)
    PATCH=$(git rev-list --count HEAD)
    UI_VERSION="${MAJOR}.${MINOR}.${PATCH}"
    cd lib
    sed -i -E "s#(final String frontendVersion = \")[^\"]*(\";)#\1${UI_VERSION}\2#" main.dart
    cd ..

    flutter build web --release

    cd ..

)





# Go build
(
    echo "Starting go build..."

    cd ns-cli

    MINOR=$(git rev-list --count HEAD --merges)
    PATCH=$(git rev-list --count HEAD)
    CLI_VERSION="${MAJOR}.${MINOR}.${PATCH}"
    cd cli/cmd
    sed -i "s#\(Version: *\"\)[^\"]*\(\".*\)#\1${CLI_VERSION}\2#" root.go
    cd ..
    cd ..
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
mkdir -p $DEB_DIR/usr/share/ns/configs
mkdir -p $DEB_DIR/etc/ns
mkdir -p $DEB_DIR/etc/nginx
mkdir -p $DEB_DIR/etc/snmp
mkdir -p $DEB_DIR/etc/xinetd.d
mkdir -p $DEB_DIR/etc/security
mkdir -p $DEB_DIR/etc/nginx/ssl
mkdir -p $DEB_DIR/etc/systemd/system
mkdir -p $DEB_DIR/etc/bash_completion.d/ns.bash

# Copy binary to package structure
cp $BUILD_DIR/ns $DEB_DIR/usr/bin/ns

# Copy Flutter web assets to package structure
cp -r ns-ui/build/web/* $DEB_DIR/usr/share/ns/web/

# Copy all the configs for reset
cp -r configs/* $DEB_DIR/usr/share/ns/configs/

# Copy configuration files to package structure
if [ -f "configs/nginx.conf" ]; then
    cp configs/nginx.conf $DEB_DIR/etc/nginx/nginx.conf
    echo "Included nginx.conf"
fi

if [ -f "configs/snmpd.conf" ]; then
    cp configs/snmpd.conf $DEB_DIR/etc/snmp/snmpd.conf
    echo "Included snmpd.conf"
fi

if [ -f "configs/ftp" ]; then
    cp configs/ftp $DEB_DIR/etc/xinetd.d/ftp
    echo "Included ftp"
fi

if [ -f "configs/ssh" ]; then
    cp configs/ssh $DEB_DIR/etc/xinetd.d/ssh
    echo "Included ssh"
fi

if [ -f "configs/telnet" ]; then
    cp configs/telnet $DEB_DIR/etc/xinetd.d/telnet
    echo "Included telnet"
fi

if [ -f "configs/pwquality.conf" ]; then
    cp configs/pwquality.conf $DEB_DIR/etc/security/pwquality.conf
    echo "Included pwquality.conf"
fi

if [ -f "configs/login.defs" ]; then
    cp configs/login.defs $DEB_DIR/etc/login.defs
    echo "Included login.defs"
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



cp "${PACKAGE_NAME}_${VERSION}_arm64.deb" ns-package/pool/main/n/ns/

cd ns-package

ls 

# Generate Packages file
apt-ftparchive packages pool/ > dists/bullseye/main/binary-arm64/Packages

# Generate compressed Packages file
gzip -k dists/bullseye/main/binary-arm64/Packages

# Generate Release file
apt-ftparchive -c=apt-ftparchive.conf release dists/bullseye/ > dists/bullseye/Release

echo "Repository metadata updated"
echo "=== Packages file ===" 
head -30 dists/bullseye/main/binary-arm64/Packages


git status
git add .
git commit -m "Add ns package ${PACKAGE_NAME}_${VERSION}_arm64.deb"
git push origin HEAD:main