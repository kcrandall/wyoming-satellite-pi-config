# Wyoming Pi Setup

Automated setup for Wyoming Satellite on Raspberry Pi with audio detection and configuration.

## Quick Start
```bash
git clone https://github.com/githubusername/repo-name.git
cd repo-name
sudo ./install.sh
```

## Full Setup

Here's how the system works and how to set it up on a new Pi:

1. First Time Pi Setup:
```bash
# Start with fresh Raspberry Pi OS Lite
# Using Raspberry Pi Imager:
- Choose Raspberry Pi OS Lite (64-bit)
- In settings (⚙️):
  - Set hostname (e.g., wyoming-living)
  - Enable SSH with password auth
  - Set username to "admin"
  - Set a password
  - Configure WiFi if needed

# After first boot, SSH in:
ssh admin@wyoming-living.local
```

2. Clone and Install:
```bash
# Install git
sudo apt update
sudo apt install git

# Clone the repo
git clone https://github.com/githubusername/repo-name.git
cd repo-name

chmod +x install.sh

# Run installer
sudo ./install.sh
```

How the system works:

1. The `install.sh` script:
- Creates necessary directories
- Copies files to correct locations
- Makes scripts executable
- Triggers service setup

2. `config/config.yaml` controls:
- Satellite name
- Room/area
- Home Assistant connection
- Wake word settings
- VAD settings

3. `scripts/setup.py`:
- Installs dependencies
- Creates Python virtual environment
- Detects audio devices
- Configures Wyoming satellite

4. `scripts/service_setup.sh`:
- Sets up systemd services
- Enables automatic startup
- Starts the services

5. Services:
- `wyoming-setup.service`: Runs setup script on boot
- `wyoming-satellite.service`: Runs the actual Wyoming satellite

To customize for your setup:

1. Edit `config/config.yaml` before installing:
```yaml
satellite:
  name: "living_room"        # Change this
  area: "living_room"        # Change this
  host: "192.168.1.100"      # Your HA IP
  ha_port: 10600
```

2. Or use environment variables:
```bash
export WYOMING_NAME="living_room"
export WYOMING_HA_HOST="192.168.1.50"
sudo -E ./install.sh
```

To check if everything is working:
```bash
# Check services
sudo systemctl status wyoming-setup
sudo systemctl status wyoming-satellite

# Check logs
sudo journalctl -u wyoming-satellite -f

# Check audio
arecord -l
```

Would you like me to explain:
1. How to troubleshoot common issues?
2. How to test the audio setup?
3. How to modify the configuration after installation?


## Repository Structure
```
root/
├── install.sh              # Main installation script that sets up the entire system
├── README.md               # This documentation file
├── config/
│   └── config.yaml         # Default configuration for Wyoming satellite
├── scripts/
│   ├── setup.py            # Python script that runs at boot to configure audio and Wyoming
│   ├── configure.py        # Interactive script to modify config.yaml settings
│   └── service_setup.sh    # Sets up systemd services
└── services/
├── wyoming-setup.service       # Systemd service that runs setup.py at boot
└── wyoming-satellite.service   # Systemd service that runs the Wyoming satellite
```

### File Descriptions

#### Root Directory
- `install.sh`: Main installation script that:
  - Installs Python and dependencies
  - Creates virtual environment
  - Installs Wyoming packages
  - Sets up all services

#### Config Directory
- `config.yaml`: Default configuration file containing:
  - Satellite name and area
  - Home Assistant connection details
  - Wake word settings
  - Virtual environment settings

#### Scripts Directory
- `setup.py`: Core setup script that:
  - Detects audio devices
  - Updates Wyoming configuration
  - Runs at system boot
  
- `configure.py`: Interactive configuration tool that:
  - Allows easy config.yaml modifications
  - Provides default values
  - Can restart services
  
- `service_setup.sh`: Service configuration script that:
  - Sets up systemd services
  - Configures auto-start
  - Sets proper permissions

#### Services Directory
- `wyoming-setup.service`: Systemd service that:
  - Runs setup.py at boot
  - Must complete before satellite starts
  
- `wyoming-satellite.service`: Systemd service that:
  - Runs the Wyoming satellite
  - Depends on setup service
  - Manages the satellite process


#### Debugging 
```
sudo systemctl status wyoming-satellite.service --no-pager
sudo journalctl -u wyoming-satellite.service
```