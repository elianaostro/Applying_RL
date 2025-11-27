#!/usr/bin/env python3
"""
Script para entrenar el agente CarAgent usando TU implementación de PPO con Unity.

Este script usa la Python Low-Level API de ML-Agents para conectar tu algoritmo PPO
con el entorno de Unity, permitiendo que TU código sea el "cerebro" del agente.

Uso:
    python train_custom_ppo.py [--env PATH] [--max-steps N] [--time-scale F]
"""

import sys
import os
import argparse
import numpy as np
import torch
from pathlib import Path
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel

# Ajustar el path para importar tu PPO
sys.path.append(str(Path(__file__).parent.parent))
from PPO.ppo import PPOClip, PPOConfig


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Entrenar CarAgent con tu implementación de PPO",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--env",
        type=str,
        default=None,
        help="Ruta al ejecutable de Unity (opcional, por defecto usa Unity Editor)"
    )
    
    parser.add_argument(
        "--max-steps",
        type=int,
        default=5000000,
        help="Número máximo de pasos de entrenamiento (default: 5000000)"
    )
    
    parser.add_argument(
        "--time-scale",
        type=float,
        default=20.0,
        help="Time scale de Unity para acelerar la simulación (default: 20.0)"
    )
    
    parser.add_argument(
        "--save-dir",
        type=str,
        default="results/custom_ppo",
        help="Directorio para guardar modelos (default: results/custom_ppo)"
    )
    
    parser.add_argument(
        "--save-freq",
        type=int,
        default=100000,
        help="Frecuencia de guardado en pasos (default: 100000)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=1,
        help="Seed para reproducibilidad (default: 1)"
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 70)
    print("Entrenamiento con PPO Personalizado")
    print("=" * 70)
    print()
    print("Configuración:")
    print(f"  Env: {args.env if args.env else 'Unity Editor'}")
    print(f"  Max Steps: {args.max_steps}")
    print(f"  Time Scale: {args.time_scale}")
    print(f"  Save Dir: {args.save_dir}")
    print()
    
    # 1. Configuración de conexión con Unity
    print("Conectando con Unity...")
    engine_channel = EngineConfigurationChannel()
    
    try:
        env = UnityEnvironment(
            file_name=args.env,
            seed=args.seed,
            side_channels=[engine_channel],
            worker_id=0,
            base_port=5004
        )
        
        # Acelerar la simulación en Unity
        engine_channel.set_configuration_parameters(
            width=800,
            height=600,
            time_scale=args.time_scale
        )
        
        # Esperar a que el entorno se inicialice
        env.reset()
        
        # 2. Obtener información del comportamiento
        behavior_name = list(env.behavior_specs)[0]
        spec = env.behavior_specs[behavior_name]
        
        # Obtener dimensiones automáticamente desde Unity
        # Asumiendo que la primera observación es un Vector Sensor
        obs_dim = spec.observation_specs[0].shape[0]
        act_dim = spec.action_spec.continuous_size
        
        print(f"✓ Conectado a Unity")
        print(f"  Behavior Name: {behavior_name}")
        print(f"  Observation Dimension: {obs_dim}")
        print(f"  Action Dimension: {act_dim}")
        print()
        
        # 3. Inicializar TU agente PPO
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Usando dispositivo: {device}")
        print()
        
        config = PPOConfig(
            learning_rate=3e-4,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            batch_size=128,
            n_steps=2048,
            n_epochs=10,
            hidden_sizes=(256, 256),
            ent_coef=0.01,
            vf_coef=0.5
        )
        
        agent = PPOClip(obs_dim, act_dim, config, device, discrete=False)
        
        # 4. Bucle de Entrenamiento
        total_steps = 0
        episode_count = 0
        episode_rewards = []
        
        # Diccionario para trackear episodios por agente
        agent_episodes = {}  # {agent_id: {'obs': obs, 'action': action, 'logp': logp, 'val': val, 'reward': reward}}
        
        print("=" * 70)
        print("Iniciando entrenamiento...")
        print("=" * 70)
        print()
        print("NOTA: Asegúrate de que Unity esté en Play mode")
        print()
        
        while total_steps < args.max_steps:
            # Obtener observaciones actuales
            decision_steps, terminal_steps = env.get_steps(behavior_name)
            
            # Manejar agentes que terminaron (episodio terminado)
            for agent_id in terminal_steps.agent_id:
                # CORRECCIÓN: Usar terminal_steps[agent_id] para acceder al paso del agente
                term_step = terminal_steps[agent_id]
                final_reward = term_step.reward
                
                # Si tenemos datos del episodio, actualizar la última entrada
                if agent_id in agent_episodes:
                    episode_data = agent_episodes[agent_id]
                    
                    # La última entrada ya está en el buffer, solo necesitamos agregar la recompensa final
                    # y marcar como done. Como el buffer ya tiene la entrada, agregamos una entrada
                    # final con la recompensa acumulada
                    agent.buffer.add(
                        obs=episode_data['obs'],
                        act=episode_data['action'],
                        logp=episode_data['logp'],
                        rew=episode_data['reward'] + final_reward,
                        done=True,
                        val=episode_data['val']
                    )
                    
                    episode_rewards.append(episode_data['reward'] + final_reward)
                    episode_count += 1
                    
                    # Limpiar tracking del episodio
                    del agent_episodes[agent_id]
                    
                    if episode_count % 10 == 0:
                        avg_reward = np.mean(episode_rewards[-10:])
                        print(f"Episodio {episode_count}, Recompensa promedio: {avg_reward:.2f}, Pasos: {total_steps}")
            
            # Manejar agentes activos (tomar decisiones)
            if len(decision_steps) > 0:
                # Por simplicidad, trabajamos con el primer agente activo
                agent_id = decision_steps.agent_id[0]
                
                # CORRECCIÓN: Usar decision_steps[agent_id] para acceder al paso del agente
                decision_step = decision_steps[agent_id]
                obs = decision_step.obs[0]  # Primera observación del agente
                
                # Convertir observación a tensor
                obs_tensor = torch.tensor(obs, dtype=torch.float32)
                
                # Tu PPO selecciona acción
                action, logp, val = agent.select_action(obs_tensor)
                
                # Obtener recompensa del paso actual
                step_reward = decision_step.reward
                
                # Guardar en buffer
                agent.buffer.add(
                    obs=obs,
                    act=action.numpy(),
                    logp=logp,
                    rew=step_reward,
                    done=False,
                    val=val
                )
                
                # Guardar datos del episodio para cuando termine
                agent_episodes[agent_id] = {
                    'obs': obs,
                    'action': action.numpy(),
                    'logp': logp,
                    'val': val,
                    'reward': step_reward
                }
                
                # Convertir acción a formato Unity
                action_np = action.numpy().reshape(1, -1)  # Shape (1, act_dim)
                action_tuple = ActionTuple(continuous=action_np)
                
                # Enviar acción a Unity
                env.set_actions(behavior_name, action_tuple)
                
                total_steps += 1
                
                # Actualizar cuando el buffer esté lleno
                if agent.buffer.is_full():
                    # Obtener el último valor para GAE
                    # Usar el valor actual del agente activo
                    last_obs_tensor = obs_tensor.to(device).unsqueeze(0)
                    last_value = agent.value(last_obs_tensor).squeeze(-1).item()
                    
                    # Calcular GAE y obtener batch
                    batch = agent.buffer.get(
                        last_value=last_value,
                        gamma=config.gamma,
                        lam=config.gae_lambda
                    )
                    
                    # Actualizar el agente
                    metrics = agent.update(batch)
                    
                    print(f"Update en paso {total_steps}:")
                    print(f"  Policy Loss: {metrics['loss_policy']:.4f}")
                    print(f"  Value Loss: {metrics['loss_value']:.4f}")
                    print(f"  Entropy: {metrics['entropy']:.4f}")
                    print()
                    
                    # Guardar modelo periódicamente
                    if total_steps % args.save_freq == 0:
                        save_path = Path(args.save_dir) / f"ppo_step_{total_steps}.pt"
                        agent.save(str(save_path))
                        print(f"Modelo guardado en: {save_path}")
                        print()
            
            # Avanzar simulación
            env.step()
        
        # Guardar modelo final
        save_path = Path(args.save_dir) / "ppo_final.pt"
        agent.save(str(save_path))
        print(f"Modelo final guardado en: {save_path}")
        
    except KeyboardInterrupt:
        print("\n\nEntrenamiento interrumpido por el usuario.")
        if 'agent' in locals():
            save_path = Path(args.save_dir) / "ppo_interrupted.pt"
            agent.save(str(save_path))
            print(f"Modelo guardado en: {save_path}")
    except Exception as e:
        print(f"\n✗ Error durante el entrenamiento: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'env' in locals():
            env.close()
            print("Entorno cerrado.")


if __name__ == "__main__":
    main()

