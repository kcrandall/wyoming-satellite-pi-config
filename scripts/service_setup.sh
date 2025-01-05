#!/bin/bash
set -e

# Make sure we're root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

echo "Setting up Wyoming services..."

# Copy service files
cp services/wyoming-setup.service /etc/systemd/system/
cp services/wyoming-satellite.service /etc/systemd/system/

# Set correct permissions
chmod 644 /etc/systemd/system/wyoming-setup.service
chmod 644 /etc/systemd/system/wyoming-satellite.service

# Reload systemd and enable services
systemctl daemon-reload

echo "Enabling Wyoming services..."
systemctl enable wyoming-setup
systemctl enable wyoming-satellite

echo "Starting Wyoming services..."
# Start services
systemctl start wyoming-setup
sleep 2  # Give setup service time to complete
systemctl start wyoming-satellite

echo "Checking service status..."
systemctl status wyoming-setup --no-pager
systemctl status wyoming-satellite --no-pager

echo "Service setup complete. Check logs at /var/log/wyoming/setup.log"