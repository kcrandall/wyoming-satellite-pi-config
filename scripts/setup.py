#!/usr/bin/env python3
import subprocess
import json
import yaml
import os
import re
import sys
import shutil
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/wyoming/setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('wyoming-setup')

def run_command(command, shell=False):
    """Run a command and return output and success status"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
        else:
            result = subprocess.run(command, check=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return False, e.stderr

def load_config():
    """Load configuration from file and environment variables"""
    config_path = '/usr/local/bin/wyoming/config.yaml'
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)['satellite']
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    # Override with environment variables if set
    env_mappings = {
        'WYOMING_NAME': 'name',
        'WYOMING_AREA': 'area',
        'WYOMING_VENV': 'venv',
        'WYOMING_HA_HOST': 'host',
        'WYOMING_HA_PORT': 'ha_port',
        'WYOMING_SATELLITE_PORT': 'satellite_port',
        'WYOMING_WAKE_WORD': 'wake_word'
    }

    for env_var, config_key in env_mappings.items():
        if os.getenv(env_var):
            config[config_key] = os.getenv(env_var)

    return config

def get_audio_devices():
    """Get all audio devices"""
    try:
        mic_output = subprocess.check_output(['arecord', '-l'], universal_newlines=True)
        speaker_output = subprocess.check_output(['aplay', '-l'], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get audio devices: {e}")
        return None, None

    mic_devices = {}
    speaker_devices = {}

    # Parse microphone devices
    for line in mic_output.split('\n'):
        if 'card' in line and 'device' in line:
            match = re.search(r'card (\d+): ([^\[]+)\[(.*?)\], device (\d+): (.*)', line)
            if match:
                card_num, card_name, card_id, device_num, device_desc = match.groups()
                device_id = f"hw:{card_num},{device_num}"
                mic_devices[device_id] = f"{card_name.strip()} [{card_id.strip()}]: {device_desc.strip()}"

    # Parse speaker devices
    for line in speaker_output.split('\n'):
        if 'card' in line and 'device' in line:
            match = re.search(r'card (\d+): ([^\[]+)\[(.*?)\], device (\d+): (.*)', line)
            if match:
                card_num, card_name, card_id, device_num, device_desc = match.groups()
                device_id = f"hw:{card_num},{device_num}"
                speaker_devices[device_id] = f"{card_name.strip()} [{card_id.strip()}]: {device_desc.strip()}"

    return mic_devices, speaker_devices

def select_best_device(devices):
    """Select the best audio device"""
    if not devices:
        return None
        
    # Priority order: M-Audio > Focusrite > Other USB > Built-in
    priority_keywords = ['M-Track', 'Scarlett', 'USB']
    
    for keyword in priority_keywords:
        matching_devices = {k: v for k, v in devices.items() if keyword in v}
        if matching_devices:
            return list(matching_devices.keys())[0]
    
    return list(devices.keys())[0]

def get_user_home():
    """Get the actual user's home directory even when running as root"""
    # Get SUDO_USER or default to current user
    user = os.environ.get('SUDO_USER', os.environ.get('USER', 'admin'))
    return Path(f'/home/{user}')

def setup_virtual_environment(venv_path, requirements_files):
    """Set up a virtual environment and install dependencies"""
    logger.info(f"Setting up virtual environment at {venv_path}")
    if not venv_path.exists():
        logger.info("Creating virtual environment...")
        success, output = run_command(['python3', '-m', 'venv', str(venv_path)])
        if not success:
            logger.error(f"Failed to create virtual environment: {output}")
            return False

    pip_path = venv_path / "bin" / "pip"
    for req_file in requirements_files:
        if req_file.exists():
            logger.info(f"Installing dependencies from {req_file}")
            success, output = run_command([str(pip_path), "install", "-r", str(req_file)])
            if not success:
                logger.error(f"Failed to install dependencies: {output}")
                return False
        else:
            logger.warning(f"Requirements file not found: {req_file}")
    return True

def install_additional_packages(venv_path):
    venv_pip = venv_path / "bin" / "pip"
    # Install additional pip packages
    additional_packages = [
        "pyyaml",  # Add other required packages here if needed
    ]
    logger.info("Installing additional pip packages...")
    for package in additional_packages:
        logger.info(f"Installing {package}...")
        success, output = run_command([str(venv_pip), "install", package])
        if not success:
            logger.error(f"Failed to install {package}: {output}")
            return False
        
def setup_openwakeword():
    """Set up the OpenWakeWord environment"""
    logger.info("Setting up OpenWakeWord...")
    venv_path = Path("/home/admin/.wyoming-openwakeword")
    repository_path = Path("/home/admin/.wyoming/wyoming-openwakeword")
    requirements_file = repository_path / "requirements.txt"

    if not repository_path.exists():
        logger.info("Cloning wyoming-openwakeword repository...")
        success, output = run_command(["git", "clone", "https://github.com/rhasspy/wyoming-openwakeword.git", str(repository_path)])
        if not success:
            logger.error(f"Failed to clone OpenWakeWord repository: {output}")
            return False

    if not setup_virtual_environment(venv_path, [requirements_file]):
        logger.error("Failed to set up OpenWakeWord virtual environment")
        return False

    install_additional_packages(venv_path)
    logger.info("OpenWakeWord setup complete")
    return True

def setup_satellite():
    """Set up the Satellite environment"""
    logger.info("Setting up Satellite...")
    venv_path = Path("/home/admin/.wyoming-satellite")
    repository_path = Path("/home/admin/.wyoming/wyoming-satellite")
    requirements_files = [
        repository_path / "requirements.txt",
        repository_path / "requirements_audio_enhancement.txt",
        repository_path / "requirements_vad.txt"
    ]

    if not repository_path.exists():
        logger.info("Cloning wyoming-satellite repository...")
        success, output = run_command(["git", "clone", "https://github.com/rhasspy/wyoming-satellite.git", str(repository_path)])
        if not success:
            logger.error(f"Failed to clone Satellite repository: {output}")
            return False

    if not setup_virtual_environment(venv_path, requirements_files):
        logger.error("Failed to set up Satellite virtual environment")
        return False

    logger.info("Satellite setup complete")
    return True

def check_dependencies(config):
    """Check and install dependencies"""
    logger.info("Checking dependencies...")
    

    # Install system packages
    packages = [
        "python3-pip",
        "python3-venv",
        "libatlas-base-dev",
        "portaudio19-dev",
        "pulseaudio",
        "alsa-utils",
        "python3-yaml"
    ]
    logger.info("Checking system packages...")
    for package in packages:
        # Check if package is installed
        success, output = run_command(f"dpkg -l | grep -q '^ii.*{package}'", shell=True)
        if success:
            logger.info(f"Package {package} is already installed")
        else:
            logger.info(f"Installing package {package}...")
            success, output = run_command(f"apt-get install -y {package}", shell=True)
            if not success:
                logger.error(f"Failed to install {package}: {output}")
                return False

    if not setup_openwakeword():
        logger.error("OpenWakeWord setup failed")
        return

    # Set up Satellite
    if not setup_satellite():
        logger.error("Satellite setup failed")
        return
   
    

    logger.info("check_dependencies() complete.")
    return True

def update_wyoming_config(config, mic_device, speaker_device=None):
    """Update Wyoming configuration file"""
    config_path = '/etc/wyoming/satellite.yaml'
    logger.info(f"Updating Wyoming configuration at {config_path}")
    
    wyoming_config = {
        'satellite': {
            'name': config['name'],
            'area': config['area'],
            'host': config['host'],
            'port': config['ha_port'],
            'mic': {
                'command': [
                    'arecord',
                    '-D', mic_device,
                    '-r', '16000',
                    '-f', 'S16_LE',
                    '-c', '1'
                ]
            },
            'wake': {
                'command': [
                    'wyoming-openwakeword',
                    '--model', config['wake_word']
                ]
            },
            'vad': {
                'threshold': 2,           # VAD sensitivity
                'trigger_level': 3,       # How many positives before triggering
                'chunk_size': 960         # Audio chunk size for processing
            }
        }
    }

    if speaker_device:
        wyoming_config['satellite']['speaker'] = {
            'command': [
                'aplay',
                '-D', f"plug{speaker_device}",  # Use plughw for flexible resampling
                # '-r', '22050',
                # '-c', '1',
                # '-f', 'S16_LE',
                # '-t', 'raw'
            ]
        }

    try:
        with open('/tmp/satellite.yaml', 'w') as f:
            yaml.dump(wyoming_config, f, default_flow_style=False)
        
        run_command(f'mv /tmp/satellite.yaml {config_path}', shell=True)
        run_command(f'chown root:root {config_path}', shell=True)
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        return False

    return True

def main():
    logger.info("Starting Wyoming Satellite setup...")
    
    # Load configuration
    config = load_config()
    logger.info(f"Loaded configuration: {config}")
    
    # Check dependencies
    if not check_dependencies(config):
        logger.error("Failed to install dependencies")
        sys.exit(1)

    # Detect audio devices
    mic_devices, speaker_devices = get_audio_devices()
    if not mic_devices:
        logger.error("No microphone devices found!")
        sys.exit(1)

    # Select best devices
    best_mic = select_best_device(mic_devices)
    best_speaker = select_best_device(speaker_devices) if speaker_devices else None
    
    logger.info(f"Selected microphone: {best_mic}")
    if best_speaker:
        logger.info(f"Selected speaker: {best_speaker}")

    # Update configuration
    if not update_wyoming_config(config, best_mic, best_speaker):
        logger.error("Failed to update Wyoming configuration")
        sys.exit(1)

    logger.info("Setup completed successfully")

if __name__ == "__main__":
    main()