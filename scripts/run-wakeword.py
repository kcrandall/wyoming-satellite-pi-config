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
     # Path to the Python interpreter in your virtual environment
    venv_python = Path("/home/admin/.wyoming/bin/python")

    # Repository path
    repo_path = Path("/home/admin/.wyoming/wyoming-openwakeword")

    # Verify the repository path exists
    if not repo_path.exists():
        print(f"Error: Repository not found at {repo_path}")
        sys.exit(1)

    # Command to run the module
    args = [
        str(venv_python),  # Python interpreter from your venv
        "-m", "wyoming_openwakeword",
        "--uri", f"tcp://0.0.0.0:{config.get('wake_word_port', 10400)}",
        "--preload-model", config.get('wakeword', 'ok_jarvis'),
    ]

    # Set working directory to the repository path
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_path)  # Add the repository to PYTHONPATH

    # Execute the module
    try:
        subprocess.check_call(args, env=env, cwd=repo_path)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to run wakeword service. {e}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()