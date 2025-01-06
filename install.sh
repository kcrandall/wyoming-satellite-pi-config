#!/bin/bash
set -e

# Install Python and dependencies
echo "Installing Python and required packages..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-yaml \
    git wget curl build-essential \
    alsa-utils pulseaudio portaudio19-dev

# Create required directories
echo "Creating directories..."
sudo mkdir -p /etc/wyoming
sudo mkdir -p /usr/local/bin/wyoming
sudo mkdir -p /var/log/wyoming

# Copy files to system locations
echo "Copying files..."
sudo cp config/config.yaml /usr/local/bin/wyoming/
sudo cp scripts/setup.py /usr/local/bin/wyoming/
sudo cp scripts/configure.py /usr/local/bin/wyoming/
sudo cp scripts/service_setup.sh /usr/local/bin/wyoming/
sudo cp scripts/run-wakword.sh /usr/local/bin/wyoming/
sudo cp scripts/run-satellite.sh /usr/local/bin/wyoming/

# Make scripts executable
echo "Making scripts executable..."
sudo chmod +x /usr/local/bin/wyoming/setup.py
sudo chmod +x /usr/local/bin/wyoming/service_setup.sh
sudo chmod +x /usr/local/bin/wyoming/run-wakword.sh
sudo chmod +x /usr/local/bin/wyoming/run-satellite.sh

# Run service setup
echo "Runing service_setup.sh..."
sudo /usr/local/bin/wyoming/service_setup.sh