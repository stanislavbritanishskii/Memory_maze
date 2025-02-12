#!/bin/bash
set -e

# Configuration variables
APP_NAME="memory_maze"
VERSION="1.0"
BUILD_DIR="build"
DIST_DIR="dist_packages"

echo "Cleaning previous build artifacts..."
rm -rf build dist ${DIST_DIR} *.spec
mkdir -p ${BUILD_DIR} ${DIST_DIR}

###############################################################################
# Step 1: Build the Linux Executable with PyInstaller
###############################################################################
echo "Building Linux executable with PyInstaller..."
# Ensure pyinstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: pyinstaller not found. Please install it (e.g., pip install pyinstaller)."
    exit 1
fi

pyinstaller --onefile --noconsole --icon=assets/maze_icon.png --name ${APP_NAME} main.py

if [ ! -f "dist/${APP_NAME}" ]; then
    echo "Error: Linux executable not found in dist/. Build failed."
    exit 1
fi

echo "Linux executable built successfully."

###############################################################################
# Step 2: Create a .deb Package with Desktop Integration
###############################################################################
if ! command -v dpkg-deb &> /dev/null; then
    echo "Error: dpkg-deb not found; please install dpkg-deb to create a .deb package."
    exit 1
fi

echo "Creating .deb package with desktop integration..."
DEB_DIR="${BUILD_DIR}/${APP_NAME}_deb"
# Create the required directory structure
mkdir -p ${DEB_DIR}/DEBIAN
mkdir -p ${DEB_DIR}/usr/local/bin
mkdir -p ${DEB_DIR}/usr/share/applications
mkdir -p ${DEB_DIR}/usr/share/pixmaps

# Create the Debian control file
cat > ${DEB_DIR}/DEBIAN/control <<EOF
Package: memory-maze
Version: ${VERSION}
Section: games
Priority: optional
Architecture: amd64
Maintainer: Your Name <youremail@example.com>
Description: ${APP_NAME} is a brain development maze game for kids and adults.
EOF

# Copy the executable to /usr/local/bin
cp dist/${APP_NAME} ${DEB_DIR}/usr/local/bin/${APP_NAME}

# Copy the icon to /usr/share/pixmaps (renaming it appropriately)
cp assets/maze_icon.png ${DEB_DIR}/usr/share/pixmaps/${APP_NAME}.png

# Create a .desktop file for menu integration using an absolute icon path
cat > ${DEB_DIR}/usr/share/applications/${APP_NAME}.desktop <<EOF
[Desktop Entry]
Version=${VERSION}
Type=Application
Name=Memory Maze
Comment=A brain development maze game for kids and adults.
Exec=/usr/local/bin/${APP_NAME}
Icon=/usr/share/pixmaps/${APP_NAME}.png
Terminal=false
Categories=Game;
EOF

# Build the .deb package
dpkg-deb --build ${DEB_DIR} ${APP_NAME}.deb
mv ${APP_NAME}.deb ${DIST_DIR}/

echo ".deb package created at: ${DIST_DIR}/${APP_NAME}.deb"
echo "Packaging process complete. You can now upload the .deb file to itch.io."

###############################################################################
# End of Script
###############################################################################
