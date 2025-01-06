#!/usr/bin/env python3
import yaml
import os
import sys
from pathlib import Path
import subprocess
import logging

# Simplified logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("wyoming-satellite")

def load_config():
    """Load the satellite configuration from YAML file."""
    config_path = '/etc/wyoming/satellite.yaml'
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)['satellite']
            return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        sys.exit(1)

def main():
    """Main function to execute wyoming-satellite."""
    config = load_config()

    # Path to the Python interpreter in your virtual environment
    venv_python = Path("/home/admin/.wyoming-satellite/bin/python")

    # Repository path
    repo_path = Path("/home/admin/.wyoming/wyoming-satellite")

    # Verify the repository path exists
    if not repo_path.exists():
        logger.error(f"Error: Repository not found at {repo_path}")
        sys.exit(1)

    # Get microphone and speaker commands from the configuration
    mic_command = ' '.join(config.get('mic', {}).get('command', []))
    speaker_command = ' '.join(config.get('speaker', {}).get('command', []))

    # Build the arguments for the satellite module
    args = [
        str(venv_python),  # Python interpreter from the virtual environment
        "-m", "wyoming_satellite",
        "--name", config['name'],
        "--uri", f"tcp://0.0.0.0:{config.get('port', 10600)}",
        "--mic-command", mic_command,
        "--snd-command", speaker_command,
    ]

    # Add VAD settings if enabled
    # if config.get('vad', {}).get('enabled'):
    #     args.append("--vad")

    # Add wake word settings if configured
    if config.get('wake_word'):
        args.extend([
            "--wake-uri", f"tcp://0.0.0.0:{config.get('wake_word_port', 10400)}",
            "--wake-word-name", config.get('wakeword', 'ok_nabu'),
        ])

    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_path)  # Add the repository to PYTHONPATH

    # Run the module using subprocess
    try:
        logger.info(f"Executing command: {' '.join(args)}")
        subprocess.check_call(args, env=env, cwd=repo_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error: Failed to run satellite service. {e}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
