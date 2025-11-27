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
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter
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
    
    parser.add_argument(
        "--base-port",
        type=int,
        default=5004,
        help="Puerto base para comunicación con Unity (default: 5004)"
    )
    
    parser.add_argument(
        "--worker-id",
        type=int,
        default=0,
        help="ID del worker (default: 0). Usa un número diferente si el puerto está ocupado"
    )
    
    parser.add_argument(
        "--tensorboard-dir",
        type=str,
        default=None,
        help="Directorio para logs de TensorBoard (default: {save_dir}/tensorboard)"
    )
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    print("=" * 70)
    print("Entrenamiento con PPO Personalizado")
    print("=" * 70)
    print()
    # Crear directorios necesarios
    save_dir = Path(args.save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Configurar TensorBoard
    if args.tensorboard_dir is None:
        tensorboard_dir = save_dir / "tensorboard"
    else:
        tensorboard_dir = Path(args.tensorboard_dir)
    
    # Crear un subdirectorio con timestamp para esta ejecución
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = tensorboard_dir / f"run_{timestamp}"
    writer = SummaryWriter(log_dir=str(run_dir))
    
    print("Configuración:")
    print(f"  Env: {args.env if args.env else 'Unity Editor'}")
    print(f"  Max Steps: {args.max_steps}")
    print(f"  Time Scale: {args.time_scale}")
    print(f"  Save Dir: {args.save_dir}")
    print(f"  TensorBoard Dir: {run_dir}")
    print(f"  Base Port: {args.base_port}")
    print(f"  Worker ID: {args.worker_id}")
    print()
    
    # 1. Configuración de conexión con Unity
    print("Conectando con Unity...")
    engine_channel = EngineConfigurationChannel()
    
    try:
        env = UnityEnvironment(
            file_name=args.env,
            seed=args.seed,
            side_channels=[engine_channel],
            worker_id=args.worker_id,
            base_port=args.base_port
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
        
        # Diccionario para guardar transiciones pendientes (obs, action, logp, val)
        # Se guardan aquí antes de obtener el reward del siguiente paso
        pending_transitions = {}  # {agent_id: {'obs': obs, 'action': action, 'logp': logp, 'val': val}}
        
        print("=" * 70)
        print("Iniciando entrenamiento...")
        print("=" * 70)
        print()
        print("NOTA: Asegúrate de que Unity esté en Play mode")
        print()
        
        while total_steps < args.max_steps:
            # 1. Obtener datos de TODOS los agentes
            decision_steps, terminal_steps = env.get_steps(behavior_name)
            
            # 2. Procesar agentes que terminaron (Terminal Steps)
            # Aquí recibimos el reward final y guardamos la transición con done=True
            for agent_id in terminal_steps.agent_id:
                term_step = terminal_steps[agent_id]
                final_reward = term_step.reward
                
                # Si tenemos una transición pendiente, guardarla con el reward final
                if agent_id in pending_transitions:
                    trans = pending_transitions[agent_id]
                    agent.buffer.add(
                        obs=trans['obs'],
                        act=trans['action'],
                        logp=trans['logp'],
                        rew=final_reward,
                        done=True,
                        val=trans['val']
                    )
                    
                    episode_rewards.append(final_reward)
                    episode_count += 1
                    total_steps += 1
                    
                    # Registrar reward en TensorBoard
                    writer.add_scalar("Reward/Episode_Reward", final_reward, episode_count)
                    
                    # Limpiar transición pendiente
                    del pending_transitions[agent_id]
                    
                    if episode_count % 10 == 0:
                        avg_reward = np.mean(episode_rewards[-10:])
                        print(f"Episodio {episode_count}, Recompensa promedio: {avg_reward:.2f}, Pasos: {total_steps}")
                        # Registrar promedio de rewards
                        writer.add_scalar("Reward/Average_Reward_10", avg_reward, episode_count)
            
            # 3. Procesar agentes activos que necesitan actuar (Decision Steps)
            if len(decision_steps) > 0:
                # Preparamos lista para juntar las acciones de todos los agentes
                actions_list = []
                
                # Iteramos por cada agente que pide acción
                for agent_id in decision_steps.agent_id:
                    # Obtener la obs de ESTE agente específico
                    decision_step = decision_steps[agent_id]
                    obs = decision_step.obs[0]
                    
                    # Convertir a tensor
                    obs_tensor = torch.tensor(obs, dtype=torch.float32)
                    
                    # Tu PPO selecciona acción (devuelve acción para 1 solo agente)
                    action, logp, val = agent.select_action(obs_tensor)
                    
                    # Guardar transición pendiente (obs, action, logp, val)
                    # El reward lo obtendremos en el siguiente paso
                    pending_transitions[agent_id] = {
                        'obs': obs,
                        'action': action.numpy(),
                        'logp': logp,
                        'val': val
                    }
                    
                    # Agregar acción a la lista
                    actions_list.append(action.numpy())
                
                # Enviar TODAS las acciones a Unity de una vez
                if actions_list:
                    actions_np = np.vstack(actions_list)  # Shape (NumAgents, act_dim)
                    action_tuple = ActionTuple(continuous=actions_np)
                    
                    # ML-Agents empareja las acciones con los agent_id de decision_steps en orden
                    env.set_actions(behavior_name, action_tuple)
            
            # 4. Avanzar simulación
            env.step()
            
            # 5. Obtener rewards del paso siguiente y guardar transiciones completas
            decision_steps_next, terminal_steps_next = env.get_steps(behavior_name)
            
            # Procesar agentes que siguen activos (obtener sus rewards)
            for agent_id in decision_steps_next.agent_id:
                if agent_id in pending_transitions:
                    decision_step_next = decision_steps_next[agent_id]
                    step_reward = decision_step_next.reward
                    
                    # Ahora tenemos todo: obs, action, logp, reward, val, done=False
                    trans = pending_transitions[agent_id]
                    agent.buffer.add(
                        obs=trans['obs'],
                        act=trans['action'],
                        logp=trans['logp'],
                        rew=step_reward,
                        done=False,
                        val=trans['val']
                    )
                    
                    total_steps += 1
                    
                    # Limpiar transición pendiente (ya guardada)
                    del pending_transitions[agent_id]
            
            # 6. Actualizar cuando el buffer esté lleno
            if agent.buffer.is_full():
                # Obtener el último valor para GAE
                # Usar el valor de los agentes activos actuales
                if len(decision_steps_next) > 0:
                    # Usar el primer agente activo para obtener el último valor
                    last_agent_id = decision_steps_next.agent_id[0]
                    last_obs = decision_steps_next[last_agent_id].obs[0]
                    last_obs_tensor = torch.tensor(last_obs, dtype=torch.float32).to(device).unsqueeze(0)
                    last_value = agent.value(last_obs_tensor).squeeze(-1).item()
                else:
                    last_value = 0.0
                
                # Calcular GAE y obtener batch
                batch = agent.buffer.get(
                    last_value=last_value,
                    gamma=config.gamma,
                    lam=config.gae_lambda
                )
                
                # Actualizar el agente
                metrics = agent.update(batch)
                
                # Registrar métricas en TensorBoard
                writer.add_scalar("Loss/Policy_Loss", metrics['loss_policy'], total_steps)
                writer.add_scalar("Loss/Value_Loss", metrics['loss_value'], total_steps)
                writer.add_scalar("Loss/Total_Loss", metrics.get('loss_total', metrics['loss_policy'] + metrics['loss_value']), total_steps)
                writer.add_scalar("Metrics/Entropy", metrics['entropy'], total_steps)
                
                # Registrar también por update number
                update_number = total_steps // config.n_steps
                writer.add_scalar("Loss/Policy_Loss_Update", metrics['loss_policy'], update_number)
                writer.add_scalar("Loss/Value_Loss_Update", metrics['loss_value'], update_number)
                writer.add_scalar("Metrics/Entropy_Update", metrics['entropy'], update_number)
                
                print(f"Update en paso {total_steps}:")
                print(f"  Policy Loss: {metrics['loss_policy']:.4f}")
                print(f"  Value Loss: {metrics['loss_value']:.4f}")
                print(f"  Entropy: {metrics['entropy']:.4f}")
                print()
                
                # Guardar modelo periódicamente
                if total_steps % args.save_freq == 0:
                    save_path = save_dir / f"ppo_step_{total_steps}.pt"
                    agent.save(str(save_path))
                    print(f"Modelo guardado en: {save_path}")
                    print()
        
        # Guardar modelo final
        save_path = save_dir / "ppo_final.pt"
        agent.save(str(save_path))
        print(f"Modelo final guardado en: {save_path}")
        
        # Cerrar TensorBoard writer
        writer.close()
        print(f"Logs de TensorBoard guardados en: {run_dir}")
        print(f"\nPara visualizar los resultados, ejecuta:")
        print(f"  tensorboard --logdir {tensorboard_dir}")
        
    except KeyboardInterrupt:
        print("\n\nEntrenamiento interrumpido por el usuario.")
        if 'agent' in locals():
            save_path = save_dir / "ppo_interrupted.pt"
            agent.save(str(save_path))
            print(f"Modelo guardado en: {save_path}")
        if 'writer' in locals():
            writer.close()
            print(f"Logs de TensorBoard guardados en: {run_dir}")
    except Exception as e:
        error_msg = str(e)
        
        # Detectar error de puerto ocupado
        if "worker number" in error_msg and "still in use" in error_msg:
            print("\n" + "=" * 70)
            print("✗ Error: Puerto ocupado")
            print("=" * 70)
            print()
            print("El puerto está siendo usado por otra instancia.")
            print()
            print("Soluciones:")
            print("  1. Cierra cualquier instancia anterior del script")
            print("  2. Cierra Unity Editor y vuelve a abrirlo")
            print("  3. Usa un puerto diferente:")
            print(f"     ./train_custom_ppo.sh --base-port 5005")
            print("  4. O usa un worker_id diferente:")
            print(f"     ./train_custom_ppo.sh --worker-id 1")
            print()
        else:
            print(f"\n✗ Error durante el entrenamiento: {e}")
            import traceback
            traceback.print_exc()
    finally:
        if 'env' in locals():
            env.close()
            print("Entorno cerrado.")
        if 'writer' in locals():
            writer.close()


if __name__ == "__main__":
    main()

