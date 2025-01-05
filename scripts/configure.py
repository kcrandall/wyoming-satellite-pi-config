#!/usr/bin/env python3
import yaml
import os
import sys
from pathlib import Path

def load_current_config():
    """Load existing config or return defaults"""
    defaults = {
        'satellite': {
            'name': 'default_satellite',
            'area': 'default_area',
            'venv': '.wyoming',
            'host': '192.168.1.100',
            'ha_port': 10600,
            'satellite_port': 10300,
            'wake_word': 'hey_jarvis'
        }
    }
    
    config_path = Path('/usr/local/bin/wyoming/config.yaml')
    if not config_path.exists():
        return defaults
        
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except:
        return defaults

def get_input(prompt, default):
    """Get user input with default value"""
    response = input(f"{prompt} (default: {default}): ").strip()
    return response if response else default

def configure():
    """Interactive configuration"""
    print("\nWyoming Satellite Configuration")
    print("Press Enter to keep default values\n")
    
    # Load current config
    current = load_current_config()
    config = current['satellite']
    
    # Get user input for each setting
    new_config = {
        'satellite': {
            'name': get_input("Satellite Name", config['name']),
            'area': get_input("Area/Room Name", config['area']),
            'venv': get_input("Virtual Environment Name (Don't change this in most cases.)", config['venv']),
            'host': get_input("Home Assistant IP", config['host']),
            'ha_port': int(get_input("Home Assistant Port", config['ha_port'])),
            'satellite_port': int(get_input("Satellite Port", config['satellite_port'])),
            'wake_word': get_input("Wake Word", config['wake_word'])
        }
    }

     # Add VAD configuration
    vad_enabled = get_input("Enable VAD (Voice Activity Detection)", str(config.get('vad', {}).get('enabled', True))).lower() in ['true', 'yes', 'y', '1']

    if vad_enabled:
        vad_threshold = int(get_input("VAD Sensitivity (0-3)", config.get('vad', {}).get('threshold', 2)))
        vad_trigger = int(get_input("VAD Trigger Level", config.get('vad', {}).get('trigger_level', 3)))
    else:
        vad_threshold = 2
        vad_trigger = 3


    new_config['satellite']['vad'] = {
        'enabled': vad_enabled,
        'threshold': vad_threshold,
        'trigger_level': vad_trigger,
        'chunk_size': 960
    }
    
    # Show the new configuration
    print("\nNew Configuration:")
    for key, value in new_config['satellite'].items():
        print(f"{key}: {value}")
        
    # Confirm save
    if input("\nSave this configuration? (Y/N): ").lower() != 'y':
        print("Configuration cancelled")
        sys.exit(0)
        
    # Save configuration
    try:
        os.makedirs('/usr/local/bin/wyoming', exist_ok=True)
        with open('/usr/local/bin/wyoming/config.yaml', 'w') as f:
            yaml.dump(new_config, f, default_flow_style=False)
        print("Configuration saved successfully")
        
        # Ask about restarting services
        if input("\nRestart Wyoming services now? (y/N): ").lower() == 'y':
            os.system('sudo systemctl restart wyoming-setup')
            os.system('sudo systemctl restart wyoming-satellite')
            print("Services restarted")
            
    except Exception as e:
        print(f"Error saving configuration: {e}")
        sys.exit(1)

def check_sudo():
    """Check if script is running with sudo privileges"""
    if os.geteuid() != 0:
        print("\nError: This script requires sudo privileges.")
        print("Please run: sudo python scripts/configure.py")
        sys.exit(1)

if __name__ == "__main__":
    check_sudo()
    configure()