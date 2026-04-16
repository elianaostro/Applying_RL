#!/usr/bin/env python3
"""
Script genérico para evaluar agentes PPO entrenados en cualquier entorno de Gymnasium.

Uso:
    python eval_ppo.py --env CartPole-v1 --weights runs/cartpole_ppo/final.pt
    python eval_ppo.py --env RandomObsBinaryRewardEnv --weights runs/random_obs_ppo/final.pt --episodes 20
"""

import argparse
import torch
import numpy as np
import gymnasium as gym
from gymnasium import spaces

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from PPO.ppo import PPOClip

from custom_env import make_env


def parse_args():
    p = argparse.ArgumentParser(
        description="Evaluar agente PPO entrenado en cualquier entorno de Gymnasium",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("--env", type=str, required=True, help="Nombre del entorno (ej: CartPole-v1, MountainCarContinuous-v0)")
    p.add_argument("--weights", type=str, required=True, help="Ruta al archivo .pt con los pesos del modelo")
    p.add_argument("--episodes", type=int, default=10, help="Número de episodios para evaluar")
    p.add_argument("--seed", type=int, default=0, help="Semilla para reproducibilidad")
    p.add_argument("--render", action="store_true", help="Renderizar el entorno (requiere pygame)")
    return p.parse_args()


def main():
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Determinar modo de renderizado
    render_mode = None
    if args.render:
        try:
            import pygame
            render_mode = "human"
        except ImportError:
            print("Warning: pygame is not installed. Rendering disabled.")
            print("To enable rendering, install pygame: pip install pygame")
            render_mode = None
    
    # Crear entorno
    try:
        env = make_env(args.env, args.seed, render_mode=render_mode)
        obs, _ = env.reset(seed=args.seed)
    except Exception as e:
        if "pygame" in str(e).lower() or "DependencyNotInstalled" in str(type(e).__name__):
            print("Error: pygame is required for rendering.")
            print("Continuing without rendering...")
            env = make_env(args.env, args.seed, render_mode=None)
            obs, _ = env.reset(seed=args.seed)
        else:
            raise
    
    # Determinar dimensiones
    if isinstance(env.observation_space, spaces.Discrete):
        obs_dim = 1
    else:
        obs_dim = int(obs.shape[0])
    
    if isinstance(env.action_space, spaces.Discrete):
        act_dim = int(env.action_space.n)
        is_discrete = True
    else:
        act_dim = int(env.action_space.shape[0])
        is_discrete = False
    
    # Cargar agente
    agent = PPOClip.load(args.weights, obs_dim=obs_dim, act_dim=act_dim, device=device, discrete=is_discrete)
    
    # Variables de evaluación
    returns = []
    episode_lengths = []
    solved_count = 0
    solved_episode_indices = []
    
    print(f"Evaluating agent for {args.episodes} episodes on {args.env}...")
    print(f"Observation space: {obs_dim}D {'(discrete)' if isinstance(env.observation_space, spaces.Discrete) else '(continuous)'}")
    print(f"Action space: {act_dim} {'(discrete)' if is_discrete else 'D (continuous)'}")
    
    # Determinar criterio de solved
    if "MountainCar" in args.env:
        print(f"Solved criteria: Reach the goal (terminated=True)")
    elif "RandomObsBinaryRewardEnv" in args.env or "ConstantRewardEnv" in args.env:
        print(f"Solved criteria: Return >= 1.0")
    
    print("-" * 50)
    
    for ep in range(args.episodes):
        done = False
        ret = 0.0
        steps = 0
        obs, _ = env.reset()
        
        while not done:
            # Preparar observación
            if isinstance(env.observation_space, spaces.Discrete):
                obs_t = torch.tensor([obs], dtype=torch.float32, device=device)
            else:
                obs_t = torch.tensor(obs, dtype=torch.float32, device=device)
            
            # Seleccionar acción
            with torch.no_grad():
                action, _, _ = agent.select_action(obs_t)
            
            # Convertir acción
            if is_discrete:
                action_int = action.item() if isinstance(action, torch.Tensor) else int(action)
            else:
                action_np = action.numpy() if isinstance(action, torch.Tensor) else action
                action_np = np.clip(action_np, env.action_space.low, env.action_space.high)
                action_int = action_np
            
            # Ejecutar paso
            obs, reward, terminated, truncated, _ = env.step(action_int)
            ret += float(reward)
            done = bool(terminated) or bool(truncated)
            steps += 1
        
        # Verificar solved
        is_solved = False
        if "MountainCar" in args.env:
            is_solved = bool(terminated) and not bool(truncated)
        elif "RandomObsBinaryRewardEnv" in args.env or "ConstantRewardEnv" in args.env:
            is_solved = ret >= 1.0
        
        if is_solved:
            solved_count += 1
            solved_episode_indices.append(ep)
        
        returns.append(ret)
        episode_lengths.append(steps)
        status = " SOLVED" if is_solved else ""
        print(f"Episode {ep+1}: return={ret:.2f}, steps={steps}{status}")
    
    env.close()
    
    # Calcular estadísticas
    solve_rate = (solved_count / args.episodes * 100) if args.episodes > 0 else 0.0
    
    print("\n" + "="*50)
    print(f"Evaluation Results ({args.episodes} episodes):")
    print(f"  Mean Return: {np.mean(returns):.2f} ± {np.std(returns):.2f}")
    print(f"  Mean Episode Length: {np.mean(episode_lengths):.2f} ± {np.std(episode_lengths):.2f}")
    print(f"  Min Return: {np.min(returns):.2f}")
    print(f"  Max Return: {np.max(returns):.2f}")
    
    if "MountainCar" in args.env or "RandomObsBinaryRewardEnv" in args.env or "ConstantRewardEnv" in args.env:
        print(f"\nSolved Status:")
        print(f"  Solved episodes: {solved_count} / {args.episodes} ({solve_rate:.1f}%)")
        if solved_count > 0:
            solved_returns = [returns[i] for i in solved_episode_indices]
            print(f"  Average solved return: {np.mean(solved_returns):.2f}")
            print(f"  Average solved steps: {np.mean([episode_lengths[i] for i in solved_episode_indices]):.2f}")
    
    print("="*50)


if __name__ == "__main__":
    main()

