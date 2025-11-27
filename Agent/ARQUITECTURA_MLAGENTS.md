# Arquitectura de ML-Agents en el Proyecto

## 🔄 Cómo Funcionan los Componentes Juntos

### Componentes en el Prefab Car:

```
Car (GameObject)
├── CarController      → Coordina el carro (checkpoints, muerte, estado)
├── CarMovement        → Maneja el movimiento físico (velocidad, rotación)
├── CarAgent           → Conecta con ML-Agents (recibe acciones del modelo)
└── Behavior Parameters → Configuración de ML-Agents (nombre, observaciones, acciones)
```

### Flujo de Control:

```
ML-Agents (Python)
    ↓
    ↓ [envía acciones]
    ↓
CarAgent.OnActionReceived()
    ↓
    ↓ [llama a]
    ↓
CarMovement.SetInputs(turn, throttle)
    ↓
    ↓ [aplica físicamente]
    ↓
Car se mueve
```

### Flujo de Observaciones:

```
Sensores del Car
    ↓
    ↓ [datos]
    ↓
CarAgent.CollectObservations()
    ↓
    ↓ [envía a]
    ↓
ML-Agents (Python)
```

### Flujo de Recompensas:

```
CarController (detecta eventos)
    ↓
    ↓ [notifica]
    ↓
CarAgent.OnCheckpointCaptured() / OnWallHit()
    ↓
    ↓ [envía recompensa]
    ↓
ML-Agents (Python)
```

## 🎯 ¿Por Qué CarAgent Debe Estar en el Prefab?

### 1. ML-Agents Requiere el Componente Agent

- ML-Agents busca componentes que heredan de `Unity.MLAgents.Agent`
- `CarAgent` hereda de `Agent` (línea 8 de CarAgent.cs)
- ML-Agents se conecta automáticamente a estos componentes
- **NO puede conectarse a `CarController`** porque no hereda de `Agent`

### 2. CarAgent Es el Puente

`CarAgent` actúa como puente entre ML-Agents y el sistema existente:

```csharp
// CarAgent recibe acciones de ML-Agents
public override void OnActionReceived(ActionBuffers actions)
{
    float turn = actions.ContinuousActions[0];
    float throttle = actions.ContinuousActions[1];
    
    // Y las pasa a CarMovement (que es controlado por CarController)
    carMovement.SetInputs(new double[] { turn, throttle });
}
```

### 3. CarController Sigue Siendo Importante

`CarController` NO se elimina, sigue siendo necesario porque:

- Coordina eventos (checkpoints, colisiones)
- Notifica a `CarAgent` cuando ocurren eventos:
  ```csharp
  // En CarController.cs línea 146
  if (carAgent != null)
      carAgent.OnWallHit();
  ```
- Maneja el estado del carro (vida, muerte, restart)

## 📋 Resumen de Responsabilidades

| Componente | Responsabilidad |
|------------|----------------|
| **CarAgent** | Conecta con ML-Agents, recibe acciones, envía observaciones y recompensas |
| **CarController** | Coordina el carro, detecta eventos, notifica a CarAgent |
| **CarMovement** | Aplica el movimiento físico (velocidad, rotación) |
| **Behavior Parameters** | Configuración de ML-Agents (nombre, tamaño de observaciones/acciones) |

## ✅ Configuración Correcta

### En el Prefab Car:

```
Car (GameObject)
├── ✅ CarController (ya existe)
├── ✅ CarMovement (ya existe)
├── ✅ CarAgent (DEBE agregarse)
└── ✅ Behavior Parameters (DEBE agregarse)
```

### Relaciones:

- `CarAgent` tiene referencia a `CarController` y `CarMovement`
- `CarController` tiene referencia a `CarAgent` (para notificar eventos)
- `CarMovement` tiene referencia a `CarController` (para verificar si usar input de usuario)

## 🔍 Código Relevante

### CarAgent.cs - Recibe acciones de ML-Agents:
```csharp
public override void OnActionReceived(ActionBuffers actions)
{
    float turn = actions.ContinuousActions[0];
    float throttle = actions.ContinuousActions[1];
    
    // Pasa las acciones a CarMovement
    carMovement.SetInputs(new double[] { turn, throttle });
}
```

### CarController.cs - Notifica eventos a CarAgent:
```csharp
private void Die()
{
    // Notifica a CarAgent cuando el carro muere
    if (carAgent != null)
        carAgent.OnWallHit();
}

public void CheckpointCaptured()
{
    // Notifica a CarAgent cuando captura un checkpoint
    if (carAgent != null)
        carAgent.OnCheckpointCaptured();
}
```

## 💡 Analogía

Piensa en `CarController` como el "cerebro" del carro (lógica de negocio) y `CarAgent` como el "traductor" que:
- Traduce las acciones de ML-Agents al formato que entiende `CarMovement`
- Traduce los eventos de `CarController` a recompensas que entiende ML-Agents
- Traduce las observaciones del carro al formato que entiende ML-Agents

**Ambos son necesarios**, pero `CarAgent` es el que se conecta directamente con ML-Agents.

