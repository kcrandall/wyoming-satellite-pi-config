#!/usr/bin/env python3
import yaml
import os
import sys
from pathlib import Path

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
    venv_path = Path('/home/admin') / config['venv']
    repo_path = venv_path / 'wyoming-openwakeword'
    
    # Build command line arguments from config
    args = [
        f"--uri 'tcp://0.0.0.0:{config.get('wake_word_port', 10400)}'",
        f"--preload-model '{config.get('wakeword', 'ok_jarvis')}'"
    ]

    # Join all arguments
    args_str = ' '.join(args)
    
    # Execute the script/run command
    cmd = f"cd {repo_path} && script/run {args_str}"
    os.execvp("bash", ["bash", "-c", cmd])

if __name__ == "__main__":
    main()