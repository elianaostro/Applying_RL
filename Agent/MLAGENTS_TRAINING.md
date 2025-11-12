# Guía de Entrenamiento con ML-Agents

Esta guía explica cómo entrenar el agente PPO en el entorno de Unity usando ML-Agents.

## Requisitos Previos

1. **Python 3.8+** instalado
2. **ML-Agents** instalado: `pip install mlagents>=0.30.0`
3. **Unity** con la escena que contiene el `CarAgent` configurado

## Instalación

1. Instalar dependencias:
```bash
cd Agent
pip install -r requirements.txt
```

## Configuración en Unity

Antes de entrenar, asegúrate de que en Unity:

1. **Behavior Name**: El `CarAgent` debe tener el Behavior Name configurado como `CarAgent` (debe coincidir con el nombre en el archivo YAML de configuración).

2. **Modo de Comportamiento**: En el componente `Behavior Parameters` del `CarAgent`:
   - **Behavior Type**: Debe estar en `Default` (no `Inference Only`)
   - **Behavior Name**: `CarAgent`
   - **Vector Observation**: 
     - Space Size: `6` (5 sensores + 1 velocidad)
   - **Actions**:
     - Space Size: `2` (turn, throttle)
     - Action Type: `Continuous`

3. **Escena**: Abre la escena que contiene el `CarAgent` en Unity.

## Métodos de Entrenamiento

### Método 1: Usando Unity Editor (Recomendado para desarrollo)

1. **Abrir Unity Editor** con la escena que contiene el `CarAgent`

2. **Ejecutar el script de entrenamiento**:
```bash
cd Agent
python envs/train_car_mlagents.py
```

O usando el script bash:
```bash
cd Agent
./train_mlagents.sh
```

3. **Esperar la conexión**: El script `mlagents-learn` se conectará a Unity. Verás un mensaje como:
```
[INFO] Listening on port 5004. Start training by pressing the Play button in the Unity Editor.
```

4. **Presionar Play en Unity**: Una vez que veas el mensaje anterior, presiona el botón Play en Unity Editor para iniciar el entrenamiento.

### Método 2: Usando Build de Unity (Recomendado para entrenamiento largo)

1. **Construir el ejecutable de Unity**:
   - En Unity: File → Build Settings
   - Selecciona la escena con el `CarAgent`
   - Build

2. **Entrenar con el ejecutable**:
```bash
cd Agent
python envs/train_car_mlagents.py --env ../Build/Applying\ EANNs.exe
```

O con múltiples instancias para entrenamiento más rápido:
```bash
python envs/train_car_mlagents.py --env ../Build/Applying\ EANNs.exe --num-envs 4
```

## Opciones del Script de Entrenamiento

```bash
python envs/train_car_mlagents.py [opciones]

Opciones:
  --config PATH          Ruta al archivo de configuración YAML
                        (default: Agent/config/car_racing_config.yaml)
  
  --run-id ID           ID único para esta ejecución
                        (default: car_racing_ppo)
  
  --env PATH            Ruta al ejecutable de Unity
                        (opcional, por defecto usa Unity Editor)
  
  --resume              Continuar entrenamiento desde el último checkpoint
  
  --force               Sobrescribir resultados existentes con el mismo run-id
  
  --num-envs N          Número de instancias del entorno (default: 1)
  
  --base-port PORT      Puerto base para comunicación (default: 5004)
```

## Ejemplos

### Entrenamiento básico
```bash
python envs/train_car_mlagents.py
```

### Entrenamiento con configuración personalizada
```bash
python envs/train_car_mlagents.py --config config/my_config.yaml --run-id my_experiment
```

### Continuar entrenamiento
```bash
python envs/train_car_mlagents.py --resume
```

### Entrenamiento con build y múltiples instancias
```bash
python envs/train_car_mlagents.py --env ../Build/Applying\ EANNs.exe --num-envs 4
```

## Monitoreo del Entrenamiento

### TensorBoard

Los resultados del entrenamiento se guardan en `results/{run-id}/`. Para visualizar el progreso:

```bash
tensorboard --logdir results/car_racing_ppo
```

Luego abre tu navegador en `http://localhost:6006`

### Métricas Importantes

- **Cumulative Reward**: Recompensa acumulada por episodio
- **Policy Loss**: Pérdida de la política
- **Value Loss**: Pérdida del crítico
- **Entropy**: Entropía de la política (exploración)

## Archivos de Configuración

El archivo de configuración YAML (`Agent/config/car_racing_config.yaml`) contiene los hiperparámetros de PPO:

- **batch_size**: Tamaño del batch (128)
- **buffer_size**: Tamaño del buffer de rollouts (2048)
- **learning_rate**: Tasa de aprendizaje (3.0e-4)
- **epsilon**: Rango de clipping para PPO (0.2)
- **gamma**: Factor de descuento (0.99)
- **hidden_units**: Unidades ocultas de la red (256)
- **num_layers**: Número de capas ocultas (2)

Puedes modificar estos valores según tus necesidades.

## Modelos Entrenados

Los modelos entrenados se guardan en:
```
results/{run-id}/CarAgent.onnx
```

Para usar el modelo entrenado en Unity:
1. En el componente `Behavior Parameters` del `CarAgent`
2. Cambia **Behavior Type** a `Inference Only`
3. Asigna el modelo `.onnx` al campo **Model**

## Solución de Problemas

### "Connection timeout" o "No connection"
- Asegúrate de que Unity Editor esté ejecutándose
- Verifica que la escena con el `CarAgent` esté abierta
- Comprueba que el Behavior Name sea `CarAgent`

### "Behavior name mismatch"
- Verifica que el Behavior Name en Unity coincida con el del archivo YAML (`CarAgent`)

### "Port already in use"
- Usa `--base-port` para cambiar el puerto:
```bash
python envs/train_car_mlagents.py --base-port 5005
```

### El agente no aprende
- Revisa las recompensas en `CarAgent.cs`
- Verifica que las observaciones sean correctas
- Ajusta los hiperparámetros en el archivo YAML
- Aumenta `max_steps` si el entrenamiento termina muy rápido

## Referencias

- [Documentación oficial de ML-Agents](https://github.com/Unity-Technologies/ml-agents)
- [Guía de PPO en ML-Agents](https://github.com/Unity-Technologies/ml-agents/blob/main/docs/Training-PPO.md)

