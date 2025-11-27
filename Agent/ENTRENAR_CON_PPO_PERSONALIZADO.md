# Entrenar con tu Implementación Personalizada de PPO

## 🎯 Diferencia Clave

### ❌ Método Anterior (mlagents-learn)
- Usa el algoritmo PPO **interno de Unity** (precompilado)
- **NO usa tu código** en `PPO/ppo.py`
- Solo sirve para entrenar con el PPO de Unity

### ✅ Método Nuevo (train_custom_ppo.py)
- Usa **TU implementación** de PPO (`PPO/ppo.py`)
- Unity solo proporciona el entorno (simulación)
- Tu código es el "cerebro" que aprende

## 🚀 Cómo Usar

### Paso 1: Preparar Unity

1. **Abre Unity Editor** con el proyecto
2. **Carga la escena `Main.unity`**
3. **Verifica que el prefab `Car` tenga**:
   - `CarAgent` ✅
   - `Behavior Parameters` ✅
     - Behavior Name: `CarAgent`
     - Behavior Type: `Default`
     - Vector Observation Space Size: `6`
     - Actions Space Size: `2`, Type: `Continuous`
4. **NO presiones Play todavía**

### Paso 2: Sincronizar Dependencias

```bash
cd Agent
uv sync
```

Esto instalará `torch` y otras dependencias necesarias.

### Paso 3: Ejecutar Entrenamiento

**Opción A: Con Unity Editor (Recomendado para desarrollo)**

```bash
cd Agent
./train_custom_ppo.sh
```

Luego, cuando el script indique, **presiona Play en Unity**.

**Opción B: Con Build de Unity (Recomendado para entrenamiento largo)**

```bash
cd Agent
./train_custom_ppo.sh --env ../Build/Applying\ EANNs.exe --time-scale 50.0
```

### Paso 4: Monitorear Progreso

El script mostrará:
- Recompensas promedio cada 10 episodios
- Métricas de entrenamiento cuando se actualiza el modelo:
  - Policy Loss
  - Value Loss
  - Entropy

## 📊 Opciones del Script

```bash
./train_custom_ppo.sh [opciones]

Opciones:
  --env PATH          Ruta al ejecutable de Unity
                      (opcional, por defecto usa Unity Editor)
  
  --max-steps N       Número máximo de pasos (default: 5000000)
  
  --time-scale F      Time scale de Unity (default: 20.0)
                      Valores más altos = simulación más rápida
  
  --save-dir PATH     Directorio para guardar modelos
                      (default: results/custom_ppo)
  
  --save-freq N       Frecuencia de guardado en pasos
                      (default: 100000)
  
  --seed N            Seed para reproducibilidad (default: 1)
```

## 🔧 Configuración del Algoritmo

El algoritmo PPO se configura en `train_custom_ppo.py` (líneas 135-147):

```python
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
```

Puedes modificar estos valores según tus necesidades.

## 📁 Archivos Generados

Los modelos entrenados se guardan en:
```
results/custom_ppo/
├── ppo_step_100000.pt
├── ppo_step_200000.pt
├── ...
└── ppo_final.pt
```

## 🔍 Solución de Problemas

### Error: "No module named 'torch'"

```bash
cd Agent
uv sync
```

### Error: "Connection timeout"

1. Asegúrate de que Unity esté en **Play mode**
2. Verifica que el `Behavior Parameters` esté configurado correctamente
3. Verifica que haya al menos un auto activo en la escena

### El auto no se mueve

1. Verifica que el auto tenga `CarAgent` y `Behavior Parameters`
2. Verifica que `Behavior Type` sea `Default`
3. Revisa la consola de Unity para errores

### El entrenamiento es muy lento

1. Aumenta el `--time-scale` (ej: `--time-scale 50.0`)
2. Usa un build de Unity en lugar del Editor
3. Reduce `n_steps` en la configuración (pero esto puede afectar el aprendizaje)

## 📝 Notas Importantes

1. **Unity como Entorno**: Unity solo proporciona la simulación. Tu código Python es el que aprende.

2. **Asíncrono**: Unity es asíncrono. Los agentes pueden terminar en diferentes momentos, y el script maneja esto automáticamente.

3. **Múltiples Agentes**: El script actualmente maneja un agente a la vez. Si quieres múltiples agentes, necesitarás modificar el código.

4. **Recompensas**: Las recompensas vienen de `CarAgent.cs` (métodos `OnCheckpointCaptured()`, `OnWallHit()`, etc.).

## 🎓 Comparación con mlagents-learn

| Característica | mlagents-learn | train_custom_ppo.py |
|----------------|----------------|---------------------|
| Algoritmo | PPO de Unity | **Tu PPO** |
| Control | Totalmente automático | Control total |
| Personalización | Limitada | **Completa** |
| Debugging | Difícil | **Fácil** |
| Experimentación | Limitada | **Total libertad** |

## ✅ Ventajas de Usar tu PPO

1. **Control Total**: Modifica el algoritmo como quieras
2. **Debugging**: Puedes agregar logs y breakpoints fácilmente
3. **Experimentación**: Prueba diferentes variantes de PPO
4. **Aprendizaje**: Entiendes completamente cómo funciona tu algoritmo
5. **Flexibilidad**: Puedes cambiar hiperparámetros en tiempo real

