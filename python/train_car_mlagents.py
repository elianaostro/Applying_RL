"""
Training script for Car Racing using Unity ML-Agents
This script trains a car agent to navigate a track using reinforcement learning.

Usage:
    python train_car_mlagents.py
    
    Or use mlagents-learn directly:
    mlagents-learn config/car_racing_config.yaml --run-id=car_racing_ppo --env=../UnityProject
"""

import os
import sys
import subprocess

def main():
    """
    Main training function using ML-Agents CLI.
    """
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the YAML configuration file
    config_path = os.path.join(script_dir, "config", "car_racing_config.yaml")
    
    # Path to Unity project (relative to python directory)
    unity_project_path = os.path.join(script_dir, "..", "UnityProject")
    unity_project_path = os.path.abspath(unity_project_path)
    
    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found at {config_path}")
        print("Please create the configuration file first.")
        sys.exit(1)
    
    # Check if Unity project exists
    if not os.path.exists(unity_project_path):
        print(f"Warning: Unity project not found at {unity_project_path}")
        print("You may need to specify the path manually.")
    
    # Run training using mlagents-learn CLI
    print(f"Starting ML-Agents training...")
    print(f"Config: {config_path}")
    print(f"Unity Project: {unity_project_path}")
    print("\nMake sure Unity is running with the training scene open!")
    
    # Check if running in non-interactive mode (from Unity auto-trainer)
    auto_mode = os.environ.get("MLAGENTS_AUTO_MODE", "false").lower() == "true"
    if not auto_mode:
        print("Press Enter to continue...")
        input()
    
    try:
        # Use mlagents-learn command
        cmd = [
            "mlagents-learn",
            config_path,
            "--run-id=car_racing_ppo",
            f"--env={unity_project_path}"
        ]
        
        # Run in background if auto mode
        if auto_mode:
            print("Running in auto mode (non-interactive)...")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Don't wait, let it run
            print(f"Training process started (PID: {process.pid})")
            print("Check Unity console or Python output for progress.")
        else:
            subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during training: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: mlagents-learn command not found.")
        print("Make sure ML-Agents is installed: pip install mlagents")
        sys.exit(1)

if __name__ == "__main__":
    main()

