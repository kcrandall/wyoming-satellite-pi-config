#!/bin/bash
set -e

# Make sure we're root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

echo "Setting up Wyoming services..."

# Ensure all service files are present
if [ ! -f services/wyoming-setup.service ] || \
   [ ! -f services/wyoming-satellite.service ] || \
   [ ! -f services/wyoming-wakeword.service ]; then
    echo "Error: One or more service files are missing in the 'services' directory."
    exit 1
fi

# Copy service files
cp services/wyoming-setup.service /etc/systemd/system/
cp services/wyoming-satellite.service /etc/systemd/system/
cp services/wyoming-wakeword.service /etc/systemd/system/

# Set correct permissions
chmod 644 /etc/systemd/system/wyoming-setup.service
chmod 644 /etc/systemd/system/wyoming-satellite.service
chmod 644 /etc/systemd/system/wyoming-wakeword.service

# Stop any old services 
systemctl stop wyoming-setup
systemctl stop wyoming-wakeword
systemctl stop wyoming-satellite

# Reload systemd and enable services
systemctl daemon-reload

echo "Enabling Wyoming services..."
systemctl enable wyoming-setup
systemctl enable wyoming-wakeword
systemctl enable wyoming-satellite

echo "Starting Wyoming services..."
# Start services
systemctl start wyoming-setup
systemctl start wyoming-wakeword
sleep 2  # Give setup service time to complete
systemctl start wyoming-satellite

echo "Checking service status..."
systemctl status wyoming-setup --no-pager
systemctl status wyoming-wakeword --no-pager
systemctl status wyoming-satellite --no-pager

echo "Service setup complete. Check logs at /var/log/wyoming/setup.log"