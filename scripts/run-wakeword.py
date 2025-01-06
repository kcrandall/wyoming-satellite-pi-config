#!/usr/bin/env python3
import yaml
import os
import sys
from pathlib import Path
import subprocess

def load_config():
    config_path = '/etc/wyoming/satellite.yaml'
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)['satellite']
            # Set default port if not present
            if 'wake_word_port' not in config:
                config['wake_word_port'] = 10400
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def main():
    config = load_config()
    # venv_path = Path('/home/admin') / config.get('venv', '.wyoming')
    # repo_path = venv_path / 'wyoming-openwakeword'
    
    # Path to the Python interpreter in the virtual environment
    venv_python = Path("/home/admin/.wyoming/bin/python")

    # Ensure the interpreter exists
    if not venv_python.exists():
        print(f"Error: Python interpreter not found at {venv_python}")
        sys.exit(1)

    # Build command line arguments
    args = [
        str(venv_python), "-m", "wyoming_openwakeword",
        f"--uri=tcp://0.0.0.0:{config.get('wake_word_port', 10400)}",
        f"--preload-model={config.get('wakeword', 'ok_jarvis')}"
    ]

    # Execute the wyoming_openwakeword module
    try:
        subprocess.check_call(args)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to run wyoming_openwakeword. {e}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()