#!/usr/bin/env python3
import yaml
import os
import sys
from pathlib import Path
import logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log only to the console
    ]
)
logger = logging.getLogger("wyoming-satellite")

def load_config():
    config_path = '/etc/wyoming/satellite.yaml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)['satellite']
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def main():
    config_path = '/etc/wyoming/satellite.yaml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)['satellite']
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        sys.exit(1)    
    
    venv_path = Path('/home/admin') / config['venv']
    repo_path = venv_path / 'wyoming-satellite'
    
    mic_command = ' '.join(config.get('mic', {}).get('command', []))
    speaker_command = ' '.join(config.get('speaker', {}).get('command', []))

    # Build command line arguments from config
    args = [
        f"--name '{config['name']}'",
        f"--uri 'tcp://0.0.0.0:{config['port']}'",
        f"--mic-command '{mic_command}'",
        f"--snd-command '{speaker_command}'"
    ]

    # Add VAD settings if enabled
    if config.get('vad', {}).get('enabled'):
        args.extend([
            "--vad",
            # f"--vad-threshold {config['vad']['threshold']}",
            # f"--vad-trigger-level {config['vad']['trigger_level']}"
        ])

    if config.get('wake_word'):
        args.extend([
            f"--wake-uri 'tcp://0.0.0.0:{config.get('wake_word_port', 10400)}'",
            f"--wake-word-name '{config.get('wakeword', 'ok_nabu')}'"
        ])

    # Join all arguments
    args_str = ' '.join(args)
    
    # Execute the script/run command
    logger.info("Executing command")
    cmd = f"cd {repo_path} && script/run {args_str}"
    os.execvp("bash", ["bash", "-c", cmd])

if __name__ == "__main__":
    main()