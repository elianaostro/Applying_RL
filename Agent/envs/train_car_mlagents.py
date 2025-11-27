#!/usr/bin/env python3
"""
Script para entrenar el agente CarAgent usando ML-Agents de Unity.

Este script usa el comando mlagents-learn para entrenar el agente PPO
en el entorno de Unity.

Uso:
    python train_car_mlagents.py [--config PATH] [--run-id ID] [--env PATH] [--resume]

Requisitos:
    1. Unity debe estar ejecutándose con la escena que contiene el CarAgent
    2. El comportamiento debe estar configurado para entrenamiento (no inference)
    3. ML-Agents debe estar instalado: pip install mlagents
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
import mlagents

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Entrenar CarAgent con ML-Agents PPO",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Entrenamiento básico
  python train_car_mlagents.py

  # Especificar configuración y run ID
  python train_car_mlagents.py --config ../config/car_racing_config.yaml --run-id my_training_run

  # Continuar entrenamiento desde checkpoint
  python train_car_mlagents.py --resume

  # Entrenar con build de Unity (sin editor)
  python train_car_mlagents.py --env ../Build/Applying\ EANNs.exe
        """
    )
    
    # Get project root (assuming script is in Agent/envs/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    parser.add_argument(
        "--config",
        type=str,
        default=str(project_root / "Agent" / "config" / "car_racing_config.yaml"),
        help="Ruta al archivo de configuración YAML (default: Agent/config/car_racing_config.yaml)"
    )
    
    parser.add_argument(
        "--run-id",
        type=str,
        default="car_racing_ppo",
        help="ID único para esta ejecución de entrenamiento (default: car_racing_ppo)"
    )
    
    parser.add_argument(
        "--env",
        type=str,
        default=None,
        help="Ruta al ejecutable de Unity (opcional, por defecto usa Unity Editor)"
    )
    
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Continuar entrenamiento desde el último checkpoint"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescribir resultados existentes con el mismo run-id"
    )
    
    parser.add_argument(
        "--num-envs",
        type=int,
        default=1,
        help="Número de instancias del entorno (default: 1)"
    )
    
    parser.add_argument(
        "--base-port",
        type=int,
        default=5004,
        help="Puerto base para comunicación con Unity (default: 5004)"
    )
    
    parser.add_argument(
        "--no-graphics",
        action="store_true",
        help="Desactivar gráficos (útil para servidores sin display)"
    )
    
    return parser.parse_args()





def check_mlagents_installed():
    """Verificar que ML-Agents está instalado."""
    try:
        import mlagents
        return True
    except ImportError:
        print("✗ ML-Agents no está instalado.")
        print("  Instala ML-Agents con: uv sync")
        return False


def check_config_file(config_path):
    """Verificar que el archivo de configuración existe."""
    if not os.path.exists(config_path):
        print(f"✗ Archivo de configuración no encontrado: {config_path}")
        return False
    
    print(f"✓ Archivo de configuración encontrado: {config_path}")
    return True


def build_mlagents_command(args):
    """Construir el comando mlagents-learn."""
    cmd = ["mlagents-learn", args.config, "--run-id", args.run_id]
    
    if args.env:
        cmd.extend(["--env", args.env])
        print(f"✓ Usando build de Unity: {args.env}")
    else:
        print("✓ Usando Unity Editor (asegúrate de que Unity esté ejecutándose)")
    
    if args.resume:
        cmd.append("--resume")
        print("✓ Continuando desde checkpoint anterior")
    
    if args.force:
        cmd.append("--force")
        print("✓ Sobrescribiendo resultados existentes")
    
    if args.num_envs > 1:
        cmd.extend(["--num-envs", str(args.num_envs)])
        print(f"✓ Usando {args.num_envs} instancias del entorno")
    
    if args.base_port != 5004:
        cmd.extend(["--base-port", str(args.base_port)])
    
    if args.no_graphics:
        cmd.append("--no-graphics")
        print("✓ Modo sin gráficos activado")
    
    return cmd


def main():
    """Función principal."""
    args = parse_args()
    
    print("=" * 70)
    print("Entrenamiento de CarAgent con ML-Agents PPO")
    print("=" * 70)
    print()
    
    # Verificaciones
    if not check_mlagents_installed():
        sys.exit(1)
    
    if not check_config_file(args.config):
        sys.exit(1)
    
    print()
    print("Configuración:")
    print(f"  Config: {args.config}")
    print(f"  Run ID: {args.run_id}")
    print(f"  Env: {args.env if args.env else 'Unity Editor'}")
    print(f"  Resume: {args.resume}")
    print()
    
    # Construir comando
    cmd = build_mlagents_command(args)
    
    print()
    print("=" * 70)
    print("⚠️  IMPORTANTE: Preparación antes de iniciar")
    print("=" * 70)
    print()
    if not args.env:
        print("Si usas Unity Editor, DEBES hacer lo siguiente ANTES de continuar:")
        print()
        print("  1. ✅ Unity Editor debe estar ABIERTO")
        print("  2. ✅ La escena con CarAgent debe estar CARGADA")
        print("  3. ✅ El Behavior Parameters del CarAgent debe estar configurado:")
        print("     - Behavior Name: 'CarAgent' (debe coincidir con el config YAML)")
        print("     - Behavior Type: 'Default' (NO 'Inference')")
        print("  4. ⏸️  Unity NO debe estar en Play todavía")
        print()
        print("Después de presionar ENTER, tendrás 10 segundos para:")
        print("  → Presionar PLAY en Unity Editor")
        print()
        input("Presiona ENTER cuando estés listo para iniciar el entrenamiento... ")
        print()
        print("⏳ Iniciando en 10 segundos... Presiona PLAY en Unity AHORA!")
        print()
        for i in range(10, 0, -1):
            print(f"  {i}...", end='\r', flush=True)
            time.sleep(1)
        print("  ¡Iniciando!                                    ")
        print()
    
    print("=" * 70)
    print("Iniciando entrenamiento...")
    print("=" * 70)
    print()
    print("Comando ejecutado:")
    print("  " + " ".join(cmd))
    print()
    print("Para ver el progreso en TensorBoard:")
    print(f"  tensorboard --logdir results/{args.run_id}")
    print()
    print("=" * 70)
    print()
    
    # Ejecutar comando
    # Ejecutamos con capture_output para analizar errores, pero el usuario ya vio el error
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Si llegamos aquí, mostrar el output
        if result.stdout:
            print(result.stdout)
    except KeyboardInterrupt:
        print("\n\nEntrenamiento interrumpido por el usuario.")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        # Mostrar el output que se capturó
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        
        # Analizar el error
        error_text = (e.stderr or "") + (e.stdout or "")
        
        print("\n" + "=" * 70)
        print("Sugerencias para resolver el error:")
        print("=" * 70)
        
        # Detectar diferentes tipos de errores
        if "Previous data from this run ID was found" in error_text:
            print(f"\n✗ Error: Se encontraron datos previos para este run ID.")
            print(f"  Run ID: {args.run_id}")
            print("\n  Opciones:")
            print("  1. Continuar entrenamiento existente:")
            print(f"     ./train_mlagents.sh --resume --run-id {args.run_id}")
            print("  2. Sobrescribir datos existentes:")
            print(f"     ./train_mlagents.sh --force --run-id {args.run_id}")
            print("  3. Usar un nuevo run ID:")
            print(f"     ./train_mlagents.sh --run-id nuevo_run_id")
        elif "UnityTimeOutException" in error_text or "took too long to respond" in error_text:
            print("\n✗ Error: Unity tardó demasiado en responder (timeout).")
            print("\n  Posibles soluciones:")
            print("  1. Asegúrate de que Unity Editor esté ejecutándose y la escena esté en Play")
            print("  2. Verifica que el Behavior Type esté en 'Default' (no 'Inference')")
            print("  3. Si estás en un servidor sin gráficos, usa:")
            print(f"     ./train_mlagents.sh --no-graphics")
            print("  4. Verifica que las versiones de ML-Agents sean compatibles")
            print("  5. Intenta aumentar el timeout o reiniciar Unity")
        else:
            print("\n✗ Error durante el entrenamiento.")
            print("  Revisa el mensaje de error arriba para más detalles.")
            print("\n  Comandos útiles:")
            print(f"  - Continuar: ./train_mlagents.sh --resume --run-id {args.run_id}")
            print(f"  - Forzar: ./train_mlagents.sh --force --run-id {args.run_id}")
            print(f"  - Sin gráficos: ./train_mlagents.sh --no-graphics")
        
        print()
        sys.exit(1)
    except FileNotFoundError:
        print("\n✗ Comando 'mlagents-learn' no encontrado.")
        print("  Asegúrate de que ML-Agents esté instalado correctamente:")
        print("  uv sync")
        sys.exit(1)


if __name__ == "__main__":
    main()

