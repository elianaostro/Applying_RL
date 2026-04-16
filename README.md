# Applying Reinforcement Learning to Car Navigation

A 2D Unity simulation where cars learn to navigate through courses using Reinforcement Learning. This project extends [Samuel Arzt's original simulation](https://github.com/ArztSamuel/Applying_EANNs) with a custom PPO (Proximal Policy Optimization) implementation in Python, replacing the original evolutionary approach with modern RL.

Short demo video of an early version: https://youtu.be/rEDzUT3ymw4


![](Images/Demo.gif)


## Overview

Cars must navigate through a course without hitting walls or obstacles. Each car has five front-facing distance sensors (covering ~90 degrees) and a speed reading, forming a 6-dimensional observation vector. A neural network maps these observations to continuous actions: engine force and turning force.

<img src="Images/Car.png" width="250">


## Project Structure

```
Applying_RL/
├── Agent/                        # Python RL training code
│   ├── PPO/                      # Custom PPO implementation
│   │   ├── ppo.py                # PPOClip algorithm (policy + value networks)
│   │   └── rollout.py            # GAE-based rollout buffer
│   ├── car_agent/                # Unity car training & evaluation
│   │   ├── train_unity_car.py    # Train car agent with custom PPO
│   │   ├── eval_unity_car.py     # Evaluate trained models
│   │   └── train_optuna_unity.py # Hyperparameter search with Optuna
│   ├── custom_envs/              # Gymnasium environment scripts
│   │   ├── custom_env.py         # Custom test environments
│   │   ├── train_ppo.py          # Train on any Gymnasium env
│   │   ├── eval_ppo.py           # Evaluate custom PPO models
│   │   ├── train_stable.py       # Train with Stable-Baselines3 (baseline)
│   │   └── eval_stable.py        # Evaluate SB3 models
│   └── runables/                 # Shell scripts for training/eval
├── UnityProject/                 # Unity simulation source
│   └── Assets/Scripts/           # C# scripts (CarAgent, CarController, etc.)
├── Build/                        # Pre-built Unity executables
└── Images/                       # Demo assets
```


## PPO Implementation

The custom PPO implementation (`Agent/PPO/`) features:

- **Clipped surrogate objective** with configurable clip range
- **Generalized Advantage Estimation (GAE)** for variance reduction
- **Support for both continuous and discrete** action spaces
- **Gaussian policy** (continuous) and **Categorical policy** (discrete)
- **Configurable architecture** via `PPOConfig` dataclass

The agent connects to Unity via the ML-Agents Python Low-Level API, allowing full control over the training loop.


## Quick Start

### Prerequisites

- **Python 3.10** with [uv](https://astral.sh/uv) package manager
- **Unity Editor** (for development) or use the pre-built executables in `Build/`

### Installation

```bash
cd Agent
uv sync
```

### Training

```bash
# Train with the Linux build (recommended)
cd Agent/runables
./train_unity_car.sh --time-scale 50.0

# Train with Unity Editor
./train_unity_car.sh --env editor

# Hyperparameter search with Optuna
./train_optuna_unity.sh --trials 20 --trial-steps 750000 --time-scale 50.0
```

### Evaluation

```bash
cd Agent/runables
./eval_unity_car.sh --weights ../results/custom_ppo/ppo_final.pt --episodes 10
```

### Monitoring

```bash
tensorboard --logdir Agent/results/custom_ppo/tensorboard
# Then open http://localhost:6006
```

For detailed usage, training options, and troubleshooting, see [Agent/README.md](Agent/README.md).


## The Simulation

The simulation can be run from the Unity Editor or using the built executables in [Build/](Build/). Cars are spawned on a track and must navigate checkpoints while avoiding walls. Rewards come from reaching checkpoints; hitting walls ends the episode.

### Courses

Multiple courses of increasing difficulty are available as Unity scenes in [UnityProject/Assets/Scenes/](UnityProject/Assets/Scenes/).

![Two different courses the cars can be trained on.](Images/Courses.png)


## Gymnasium Benchmarks

The PPO implementation can also be tested on standard Gymnasium environments for validation:

```bash
cd Agent/custom_envs

# CartPole
python train_ppo.py --env CartPole-v1 --timesteps 100000

# Compare with Stable-Baselines3
python train_stable.py --env CartPole-v1 --timesteps 100000
```


## License

This project is based on [Applying EANNs](https://github.com/ArztSamuel/Applying_EANNs) by Samuel Arzt, licensed under the MIT License. The Unity simulation, car physics, and sensor system originate from that project.

The RL training infrastructure (custom PPO, Optuna integration, Gymnasium benchmarks) was developed by Eliana Ostro.
