# Migración a Unity ML-Agents

Este documento describe los cambios realizados para migrar el sistema de AI de evolución genética (C#) a Unity ML-Agents (Python).

## Cambios Realizados

### 1. Nuevo Script: `CarAgent.cs`
- **Ubicación**: `UnityProject/Assets/Scripts/AI/CarAgent.cs`
- **Descripción**: Componente que hereda de `Unity.MLAgents.Agent`
- **Funcionalidades**:
  - Observaciones: Lecturas de sensores (normalizadas) + velocidad
  - Acciones: 2 acciones continuas (turn, throttle) en rango [-1, 1]
  - Recompensas:
    - Recompensa por checkpoint capturado
    - Penalización por golpear pared
    - Penalización por timeout
    - Recompensa incremental por progreso en el track

### 2. Modificaciones en `CarController.cs`
- **Cambios**:
  - Detección automática de `CarAgent` (ML-Agents)
  - Compatibilidad con sistema antiguo (evolución genética)
  - Integración con `CarAgent` para notificaciones de eventos (checkpoints, colisiones)
  - Propiedad `UseMLAgents` para verificar si está usando ML-Agents

### 3. Scripts de Python

#### `train_car_mlagents.py`
- Script principal para entrenar el agente
- Usa el CLI de ML-Agents (`mlagents-learn`)

#### `config/car_racing_config.yaml`
- Configuración de hiperparámetros para PPO
- Parámetros ajustables: learning rate, batch size, network architecture, etc.

### 4. Actualización de Dependencias
- `requirements.txt` actualizado con:
  - `mlagents>=0.30.0`
  - `mlagents-envs>=0.30.0`

## Cómo Usar

### Configuración en Unity

1. Abre el proyecto Unity
2. En la escena de entrenamiento:
   - Agrega el componente `CarAgent` al GameObject del carro
   - **IMPORTANTE**: Agrega también el componente `Behavior Parameters` (ML-Agents) al mismo GameObject
     - En el Behavior Parameters:
       - `Behavior Name`: "CarAgent" (o el nombre que quieras)
       - `Vector Observation > Space Size`: 6 (5 sensores + 1 velocidad)
       - `Actions > Continuous Actions > Space Size`: 2 (turn, throttle)
       - `Actions > Continuous Actions`: Marca la casilla
       - `Actions > Discrete Actions`: Desmarca (no usamos acciones discretas)
   - Asigna las referencias en el Inspector de `CarAgent`:
     - `Car Controller`: Componente CarController
     - `Car Movement`: Componente CarMovement  
     - `Track Manager`: TrackManager de la escena
   - Ajusta las recompensas si es necesario

**Nota**: Sin el componente `Behavior Parameters`, el `CarAgent` no recibirá acciones y el auto no se moverá. Este componente es esencial para que ML-Agents funcione.

### Entrenamiento

```bash
cd python
pip install -r requirements.txt
python train_car_mlagents.py
```

O directamente:
```bash
mlagents-learn config/car_racing_config.yaml --run-id=car_racing_ppo --env=../UnityProject
```

### Visualización

```bash
tensorboard --logdir results
```

## Compatibilidad

El sistema mantiene compatibilidad con:
- Sistema de evolución genética (si no hay `CarAgent`)
- Sistema RLBridgeServer (TCP bridge)
- Control manual por teclado

El `CarController` detecta automáticamente qué sistema usar basándose en los componentes presentes.

## Estructura de Observaciones

- **Sensores**: 5 valores normalizados [0, 1] (distancia / 10.0)
- **Velocidad**: 1 valor normalizado [-1, 1] (velocidad / 20.0)
- **Total**: 6 observaciones

## Estructura de Acciones

- **Acción 0**: Turn (giro) [-1, 1]
- **Acción 1**: Throttle (aceleración) [-1, 1]

## Sistema de Recompensas

- **Checkpoint capturado**: +1.0 (configurable)
- **Golpear pared**: -10.0 (configurable)
- **Timeout**: -5.0 (configurable)
- **Progreso incremental**: (completion_delta) * 0.1 (configurable)
- **Completar track**: +100.0

