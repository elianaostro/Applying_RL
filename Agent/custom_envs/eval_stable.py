#!/usr/bin/env python3
"""
Script genérico para evaluar agentes PPO entrenados con Stable-Baselines3.

Uso:
    python eval_stable.py --env CartPole-v1 --weights runs/cartpole_sb3_ppo/final_model.zip
    python eval_stable.py --env MountainCarContinuous-v0 --weights runs/mountain_car_sb3_ppo/final_model.zip --episodes 20
"""

import argparse
import numpy as np
import torch
import gymnasium as gym
from stable_baselines3 import PPO


def parse_args():
    p = argparse.ArgumentParser(
        description="Evaluar agente PPO entrenado con Stable-Baselines3",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("--env", type=str, required=True, help="Nombre del entorno (ej: CartPole-v1, MountainCarContinuous-v0)")
    p.add_argument("--weights", type=str, required=True, help="Ruta al archivo .zip con los pesos del modelo")
    p.add_argument("--episodes", type=int, default=10, help="Número de episodios para evaluar")
    p.add_argument("--seed", type=int, default=0, help="Semilla para reproducibilidad")
    p.add_argument("--render", action="store_true", help="Renderizar el entorno (requiere pygame)")
    return p.parse_args()


def make_env(env_id: str, render_mode: str | None):
    """Crea el entorno."""
    try:
        return gym.make(env_id, render_mode=render_mode)
    except Exception as e:
        error_str = str(e).lower()
        error_type = str(type(e).__name__)
        
        if "pygame" in error_str or "DependencyNotInstalled" in error_type:
            print("Warning: pygame is not installed. Rendering disabled.")
            print("To enable rendering, install pygame: pip install pygame")
            return gym.make(env_id, render_mode=None)
        raise


def main():
    args = parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    render_mode = None
    if args.render:
        try:
            import pygame  # noqa: F401
            render_mode = "human"
        except ImportError:
            print("Warning: pygame is not installed. Rendering disabled.")
            print("To enable rendering, install pygame: pip install pygame")
            render_mode = None
    
    try:
        env = make_env(args.env, render_mode)
        env.reset(seed=args.seed)
    except Exception as exc:
        if "pygame" in str(exc).lower() or "DependencyNotInstalled" in type(exc).__name__:
            print("Error: pygame is required for rendering.")
            print("Continuing without rendering...")
            env = make_env(args.env, None)
            env.reset(seed=args.seed)
        else:
            raise
    
    model = PPO.load(args.weights, device=device)
    
    returns: list[float] = []
    episode_lengths: list[int] = []
    solved_count = 0
    solved_episode_indices = []
    
    print(f"Evaluating SB3 PPO agent for {args.episodes} episodes on {args.env}...")
    
    # Determinar criterio de solved
    if "MountainCar" in args.env:
        print(f"Solved criteria: Reach the goal (terminated=True)")
    print("-" * 50)
    
    for ep in range(args.episodes):
        obs, _ = env.reset(seed=args.seed + ep)
        done = False
        ret = 0.0
        steps = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            if isinstance(action, np.ndarray) and action.shape == ():
                action_env = int(action.item())
            elif isinstance(action, np.ndarray):
                action_env = action
            else:
                action_env = int(action)
            
            obs, reward, terminated, truncated, _ = env.step(action_env)
            ret += float(reward)
            done = bool(terminated) or bool(truncated)
            steps += 1
        
        # Verificar solved
        is_solved = False
        if "MountainCar" in args.env:
            is_solved = bool(terminated) and not bool(truncated)
        
        if is_solved:
            solved_count += 1
            solved_episode_indices.append(ep)
        
        returns.append(ret)
        episode_lengths.append(steps)
        status = " SOLVED" if is_solved else ""
        print(f"Episode {ep + 1}: return={ret:.2f}, steps={steps}{status}")
    
    env.close()
    
    solve_rate = (solved_count / args.episodes * 100) if args.episodes > 0 else 0.0
    
    print("\n" + "=" * 50)
    print(f"Evaluation Results ({args.episodes} episodes):")
    print(f"  Mean Return: {np.mean(returns):.2f} ± {np.std(returns):.2f}")
    print(f"  Mean Episode Length: {np.mean(episode_lengths):.2f} ± {np.std(episode_lengths):.2f}")
    print(f"  Min Return: {np.min(returns):.2f}")
    print(f"  Max Return: {np.max(returns):.2f}")
    
    if "MountainCar" in args.env:
        print(f"\nSolved Status:")
        print(f"  Solved episodes: {solved_count} / {args.episodes} ({solve_rate:.1f}%)")
        if solved_count > 0:
            solved_returns = [returns[i] for i in solved_episode_indices]
            print(f"  Average solved return: {np.mean(solved_returns):.2f}")
            print(f"  Average solved steps: {np.mean([episode_lengths[i] for i in solved_episode_indices]):.2f}")
    
    print("=" * 50)


if __name__ == "__main__":
    main()

