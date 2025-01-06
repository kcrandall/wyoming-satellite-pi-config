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
    # Paths
    venv_python = Path("/home/admin/.wyoming/bin/python")
    repo_path = Path("/home/admin/.wyoming/wyoming-openwakeword")
    main_script = repo_path / "wyoming_openwakeword" / "__main__.py"

    # Ensure the main script exists
    if not main_script.exists():
        print(f"Error: Main script not found at {main_script}")
        sys.exit(1)

    # Build command line arguments
    args = [
        str(venv_python),  # Python interpreter from your venv
        str(main_script),  # Path to the main script
        "--uri", f"tcp://0.0.0.0:{config.get('wake_word_port', 10400)}",
        "--preload-model", config.get('wakeword', 'ok_jarvis'),
    ]

    # Execute the main script directly
    try:
        subprocess.check_call(args)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to run wakeword service. {e}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()