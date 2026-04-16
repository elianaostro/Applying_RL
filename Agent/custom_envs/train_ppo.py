#!/usr/bin/env python3
"""
Script genérico para entrenar agentes PPO en cualquier entorno de Gymnasium.

Uso:
    python train_ppo.py --env CartPole-v1 --timesteps 100000
    python train_ppo.py --env RandomObsBinaryRewardEnv --timesteps 10000
    python train_ppo.py --env MountainCarContinuous-v0 --timesteps 200000
"""

import argparse
import os
from typing import Tuple, Optional, Dict, Any

import numpy as np
import torch
import gymnasium as gym
from gymnasium import spaces
from torch.utils.tensorboard import SummaryWriter

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from PPO.ppo import PPOClip, PPOConfig

from custom_env import make_env


def get_default_config(env_name: str, obs_dim: int, act_dim: int, is_discrete: bool) -> PPOConfig:
    """Obtiene configuración por defecto según el entorno."""
    # Configuraciones específicas por entorno
    if "CartPole" in env_name:
        return PPOConfig(
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            learning_rate=3e-4,
            ent_coef=0.01,
            vf_coef=0.5,
            max_grad_norm=0.5,
            n_epochs=4,
            batch_size=64,
            n_steps=2048,
            hidden_sizes=(64, 64),
        )
    elif "MountainCar" in env_name:
        return PPOConfig(
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            learning_rate=3e-4,
            ent_coef=0.1,
            vf_coef=0.5,
            max_grad_norm=0.5,
            n_epochs=4,
            batch_size=64,
            n_steps=512,
            hidden_sizes=(64, 64),
        )
    elif "BipedalWalker" in env_name:
        return PPOConfig(
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            learning_rate=3e-4,
            ent_coef=0.01,
            vf_coef=0.5,
            max_grad_norm=0.5,
            n_epochs=4,
            batch_size=64,
            n_steps=2048,
            hidden_sizes=(256, 256),
        )
    else:
        # Configuración por defecto para entornos simples
        return PPOConfig(
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            learning_rate=3e-4,
            ent_coef=0.01,
            vf_coef=0.5,
            max_grad_norm=0.5,
            n_epochs=10,
            batch_size=64,
            n_steps=256,
            hidden_sizes=(64, 64),
        )


def get_reward_shaping(env_name: str, obs: np.ndarray, reward: float) -> float:
    """Aplica reward shaping específico por entorno si es necesario."""
    if "MountainCar" in env_name:
        # Reward shaping para MountainCar: pequeño bonus proporcional a la posición
        try:
            pos = float(obs[0])
            return float(reward) + 0.1 * pos
        except Exception:
            return float(reward)
    return float(reward)


def get_exploration_hack(env_name: str, total_steps: int, action: torch.Tensor, env: gym.Env) -> torch.Tensor:
    """Aplica hacks de exploración específicos por entorno."""
    if "MountainCar" in env_name:
        # Random exploration para los primeros pasos
        RANDOM_EXPL_STEPS = 2000
        if total_steps < RANDOM_EXPL_STEPS:
            action_np = env.action_space.sample().astype(np.float32)
            return torch.tensor(action_np, dtype=torch.float32)
    return action


def parse_args():
    p = argparse.ArgumentParser(
        description="Entrenar agente PPO en cualquier entorno de Gymnasium",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("--env", type=str, required=True, help="Nombre del entorno (ej: CartPole-v1, MountainCarContinuous-v0, RandomObsBinaryRewardEnv)")
    p.add_argument("--timesteps", type=int, default=100_000, help="Número total de pasos de entrenamiento")
    p.add_argument("--logdir", type=str, default=None, help="Directorio para logs de TensorBoard (por defecto: runs/{env_name}_ppo)")
    p.add_argument("--save_path", type=str, default=None, help="Ruta para guardar el modelo final (por defecto: {logdir}/final.pt)")
    p.add_argument("--checkpoint_freq", type=int, default=50_000, help="Frecuencia de guardado de checkpoints (0 para desactivar)")
    p.add_argument("--seed", type=int, default=0, help="Semilla para reproducibilidad")
    p.add_argument("--config", type=str, default=None, help="Ruta a archivo JSON con configuración personalizada (opcional)")
    return p.parse_args()


def main():
    args = parse_args()
    
    # Configurar directorios por defecto
    if args.logdir is None:
        env_safe_name = args.env.replace("/", "_").replace("-", "_")
        args.logdir = f"runs/{env_safe_name}_ppo"
    if args.save_path is None:
        args.save_path = os.path.join(args.logdir, "final.pt")
    
    os.makedirs(args.logdir, exist_ok=True)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    writer = SummaryWriter(args.logdir)
    
    # Información de TensorBoard
    logdir_abs = os.path.abspath(args.logdir)
    logdir_rel = args.logdir
    if not os.path.isabs(logdir_rel) and not logdir_rel.startswith("envs/"):
        logdir_rel = f"envs/{logdir_rel}"
    
    print("\n" + "="*70)
    print("TensorBoard Logging")
    print("="*70)
    print(f"Log directory (absolute): {logdir_abs}")
    print(f"\nTo view training plots, run:")
    print(f"  tensorboard --logdir {logdir_rel}")
    print(f"\nThen open your browser and navigate to:")
    print(f"  http://localhost:6006")
    print("="*70 + "\n")
    
    # Crear entorno
    env = make_env(args.env, args.seed)
    obs, _ = env.reset(seed=args.seed)
    
    # Determinar dimensiones y tipo de espacios
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
    
    # Cargar configuración
    if args.config:
        import json
        with open(args.config, 'r') as f:
            config_dict = json.load(f)
        cfg = PPOConfig(**config_dict)
    else:
        cfg = get_default_config(args.env, obs_dim, act_dim, is_discrete)
    
    # Crear agente
    agent = PPOClip(obs_dim=obs_dim, act_dim=act_dim, config=cfg, device=device, discrete=is_discrete)
    
    # Variables de entrenamiento
    episode_return = 0.0
    episode_len = 0
    total_steps = 0
    best_return = -1e9
    episode_count = 0
    recent_returns = []
    recent_returns_window = 10
    
    # Estadísticas de solved (si aplica)
    solved_episodes = []
    first_solved_at = None
    first_solved_episode = None
    
    print(f"Training PPO on {args.env}")
    print(f"Observation space: {obs_dim}D {'(discrete)' if isinstance(env.observation_space, spaces.Discrete) else '(continuous)'}")
    print(f"Action space: {act_dim} {'(discrete)' if is_discrete else 'D (continuous)'}")
    print(f"Device: {device}")
    print(f"Total timesteps: {args.timesteps}")
    print("-" * 70)
    print(f"{'Episode':<8} {'Return':<10} {'Length':<8} {'Avg Return':<12} {'Best':<10} {'Steps':<10} {'Status':<10}")
    print("-" * 80)
    
    while total_steps < args.timesteps:
        # Colectar rollout
        for _ in range(cfg.n_steps):
            # Preparar observación
            if isinstance(env.observation_space, spaces.Discrete):
                obs_tensor = torch.tensor([obs], dtype=torch.float32, device=device)
            else:
                obs_tensor = torch.tensor(obs, dtype=torch.float32, device=device)
            
            # Seleccionar acción
            with torch.no_grad():
                action, logp, value = agent.select_action(obs_tensor)
            
            # Aplicar hacks de exploración
            action = get_exploration_hack(args.env, total_steps, action, env)
            
            # Convertir acción a formato apropiado
            if is_discrete:
                action_np = int(action.item()) if isinstance(action, torch.Tensor) else int(action)
                action_for_buffer = np.array([action_np], dtype=np.float32)
            else:
                action_np = action.numpy() if isinstance(action, torch.Tensor) else action
                action_np = np.asarray(action_np, dtype=np.float32).reshape(env.action_space.shape)
                action_np = np.clip(action_np, env.action_space.low, env.action_space.high)
                action_for_buffer = action_np
            
            # Ejecutar paso
            next_obs, reward, terminated, truncated, _ = env.step(action_np)
            
            # Aplicar reward shaping
            shaped_reward = get_reward_shaping(args.env, next_obs, reward)
            
            # Preparar observación para buffer
            obs_for_buffer = np.array([obs], dtype=np.float32) if isinstance(env.observation_space, spaces.Discrete) else obs
            
            # Agregar al buffer
            agent.buffer.add(obs_for_buffer, action_for_buffer, logp, shaped_reward, bool(terminated), float(value))
            
            # Actualizar estadísticas
            episode_return += shaped_reward
            episode_len += 1
            total_steps += 1
            obs = next_obs
            
            # Verificar si el episodio terminó
            if terminated or truncated:
                episode_count += 1
                
                # Logging a TensorBoard
                writer.add_scalar("rollout/episode_return", episode_return, total_steps)
                writer.add_scalar("rollout/episode_len", episode_len, total_steps)
                writer.add_scalar("rollout/episode_count", episode_count, total_steps)
                writer.add_scalar("episode/reward_vs_episode", episode_return, episode_count)
                writer.add_scalar("episode/length_vs_episode", episode_len, episode_count)
                
                # Track recent returns
                recent_returns.append(episode_return)
                if len(recent_returns) > recent_returns_window:
                    recent_returns.pop(0)
                avg_return = np.mean(recent_returns) if recent_returns else 0.0
                std_return = np.std(recent_returns) if len(recent_returns) > 1 else 0.0
                
                writer.add_scalar("episode/avg_return_recent", avg_return, total_steps)
                writer.add_scalar("episode/std_return_recent", std_return, total_steps)
                writer.add_scalar("episode/best_return", best_return, total_steps)
                writer.add_scalar("episode/avg_return_recent_vs_episode", avg_return, episode_count)
                writer.add_scalar("episode/best_return_vs_episode", best_return, episode_count)
                
                # Track best return
                is_best = False
                if episode_return > best_return:
                    best_return = episode_return
                    agent.save(os.path.join(args.logdir, "best.pt"))
                    is_best = True
                    writer.add_scalar("episode/new_best_return", best_return, total_steps)
                
                # Verificar solved (específico por entorno)
                is_solved = False
                if "MountainCar" in args.env:
                    is_solved = bool(terminated) and not bool(truncated)
                elif "RandomObsBinaryRewardEnv" in args.env or "ConstantRewardEnv" in args.env:
                    is_solved = episode_return >= 1.0
                
                if is_solved:
                    solved_episodes.append(episode_count)
                    if first_solved_at is None:
                        first_solved_at = total_steps
                        first_solved_episode = episode_count
                        agent.save(os.path.join(args.logdir, "solved.pt"))
                        print("\n" + "="*80)
                        print(" ENVIRONMENT SOLVED! ")
                        print("="*80)
                        print(f"First solved at Episode {episode_count} (Step {total_steps})")
                        print(f"Return: {episode_return:.2f}")
                        print(f"Episode Length: {episode_len}")
                        print("="*80 + "\n")
                
                if is_solved:
                    writer.add_scalar("rollout/is_solved", 1.0, total_steps)
                    writer.add_scalar("episode/is_solved_vs_episode", 1.0, episode_count)
                else:
                    writer.add_scalar("rollout/is_solved", 0.0, total_steps)
                    writer.add_scalar("episode/is_solved_vs_episode", 0.0, episode_count)
                
                # Imprimir información
                status = "SOLVED!" if is_solved else ("BEST!" if is_best else "")
                print(f"{episode_count:<8} {episode_return:<10.2f} {episode_len:<8} {avg_return:<12.2f} {best_return:<10.2f} {total_steps:<10} {status:<10}")
                
                # Reset episodio
                obs, _ = env.reset()
                episode_return = 0.0
                episode_len = 0
        
        # Bootstrap value para GAE
        with torch.no_grad():
            if isinstance(env.observation_space, spaces.Discrete):
                obs_tensor = torch.tensor([obs], dtype=torch.float32, device=device)
            else:
                obs_tensor = torch.tensor(obs, dtype=torch.float32, device=device)
            last_value = agent.value(obs_tensor.unsqueeze(0)).item()
        
        # Obtener batch y actualizar
        batch = agent.buffer.get(last_value=last_value, gamma=cfg.gamma, lam=cfg.gae_lambda, adv_norm=True)
        metrics = agent.update(batch)
        
        # Logging de métricas de entrenamiento
        for k, v in metrics.items():
            writer.add_scalar(f"train/{k}", v, total_steps)
        
        # Imprimir métricas periódicamente
        if total_steps % (cfg.n_steps * 5) == 0 or total_steps < cfg.n_steps * 2:
            print(f"\n[Training Update @ Step {total_steps}]")
            print(f"  Policy Loss: {metrics.get('loss_policy', 0):.6f}")
            print(f"  Value Loss: {metrics.get('loss_value', 0):.6f}")
            print(f"  Entropy: {metrics.get('entropy', 0):.6f}")
            print(f"  Approx KL: {metrics.get('approx_kl', 0):.6f}")
            print(f"  Clip Fraction: {metrics.get('clip_fraction', 0):.4f}")
            if recent_returns:
                print(f"  Recent Avg Return: {np.mean(recent_returns):.2f}")
            print()
        
        # Checkpoint periódico
        if args.checkpoint_freq > 0 and total_steps // args.checkpoint_freq != (total_steps - cfg.n_steps) // args.checkpoint_freq:
            ckpt_path = os.path.join(args.logdir, f"ckpt_{total_steps}.pt")
            agent.save(ckpt_path)
            writer.add_text("checkpoint", f"Saved {ckpt_path}", total_steps)
            print(f"\n[Checkpoint] Saved checkpoint at step {total_steps} -> {ckpt_path}")
            print(f"  Progress: {100 * total_steps / args.timesteps:.1f}% | Episodes: {episode_count} | Best return: {best_return:.2f}\n")
        
        # Resumen periódico
        if total_steps % 25000 == 0 and total_steps > 0:
            print("\n" + "="*70)
            print(f"Progress Summary @ Step {total_steps}/{args.timesteps} ({100 * total_steps / args.timesteps:.1f}%)")
            print("="*70)
            print(f"Total Episodes: {episode_count}")
            print(f"Best Return: {best_return:.2f}")
            if recent_returns:
                print(f"Average Return (last {len(recent_returns)} episodes): {np.mean(recent_returns):.2f}")
                print(f"Std Return (last {len(recent_returns)} episodes): {np.std(recent_returns):.2f}")
            if solved_episodes:
                solve_rate = len(solved_episodes) / episode_count * 100
                print(f"\nSolved Status:")
                print(f"  First solved: Episode {first_solved_episode} @ Step {first_solved_at}")
                print(f"  Solved episodes: {len(solved_episodes)} / {episode_count} ({solve_rate:.1f}%)")
            print("="*70 + "\n")
    
    # Guardar modelo final
    env.close()
    writer.close()
    agent.save(args.save_path)
    
    print("\n" + "="*70)
    print("Training Completed!")
    print("="*70)
    print(f"Final model saved to: {args.save_path}")
    print(f"\nFinal Statistics:")
    print(f"  Total Episodes: {episode_count}")
    print(f"  Total Steps: {total_steps}")
    print(f"  Best Return: {best_return:.2f}")
    if recent_returns:
        print(f"  Average Return (last {len(recent_returns)} episodes): {np.mean(recent_returns):.2f}")
    if solved_episodes:
        solve_rate = len(solved_episodes) / episode_count * 100
        print(f"\nSolved Statistics:")
        print(f"   SOLVED! First solved at Episode {first_solved_episode} (Step {first_solved_at})")
        print(f"  Solved episodes: {len(solved_episodes)} / {episode_count} ({solve_rate:.1f}%)")
    print("="*70)


if __name__ == "__main__":
    main()

