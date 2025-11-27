# Solución: No Aparecen Autos y No Entrena

## 🔴 Problema

- No aparecen autos en la escena
- ML-Agents no está entrenando

## ✅ Soluciones

### Problema 1: ML-Agents No Crea Autos Automáticamente

ML-Agents **NO crea autos automáticamente**. Necesitas que haya al menos un agente (carro) en la escena cuando Unity está en Play.

#### Solución A: Agregar un Auto Manualmente en la Escena del Track

1. **Abre la escena del track** (ej: `Track1.unity`)
2. **Arrastra el prefab `Car`** desde `Assets/Prefabs/Car.prefab` a la escena
3. **Posiciónalo** en la posición inicial del track (donde normalmente empiezan los autos)
4. **Asegúrate de que el GameObject esté activo** (checkbox en el Inspector)
5. **Guarda la escena**

#### Solución B: Configurar TrackManager para Crear un Auto

Si el `TrackManager` tiene un método para crear autos, puedes llamarlo:

1. **Abre la escena del track** (ej: `Track1.unity`)
2. **Selecciona `TrackManager`** en la jerarquía
3. **En el Inspector**, busca si hay algún script que pueda crear autos
4. O crea un script simple que llame a `TrackManager.Instance.SetCarAmount(1)` al inicio

### Problema 2: PrototypeCar No Está Configurado

El `TrackManager` necesita tener el `PrototypeCar` asignado.

1. **Abre la escena del track** (ej: `Track1.unity`)
2. **Selecciona `TrackManager`** en la jerarquía
3. **En el Inspector**, busca el campo **"Prototype Car"**
4. **Arrastra el prefab `Car`** desde `Assets/Prefabs/Car.prefab` al campo `Prototype Car`
5. **Guarda la escena**

### Problema 3: EvolutionManager Está Interfiriendo

Si `EvolutionManager` está activo, podría estar interfiriendo con ML-Agents.

1. **En `Main.unity`**, selecciona `EvolutionManager`
2. **Desactiva el GameObject** (uncheck el checkbox en el Inspector)
3. O **desactiva el componente** `EvolutionManager` (no el GameObject completo)

### Problema 4: El Auto Está Desactivado

1. **Verifica que el prefab `Car`** tenga el checkbox activado (en el prefab)
2. **Verifica que cualquier instancia del auto en la escena** esté activa
3. **Verifica que el `PrototypeCar` en `TrackManager`** no esté desactivado

### Problema 5: ML-Agents No Detecta el Agente

1. **Verifica que el prefab `Car` tenga**:
   - ✅ Componente `CarAgent`
   - ✅ Componente `Behavior Parameters`
   - ✅ Behavior Name: `CarAgent`
   - ✅ Behavior Type: `Default`

2. **Verifica que haya al menos un auto en la escena** cuando Unity está en Play

3. **Verifica la consola de Unity** para ver si hay errores relacionados con ML-Agents

## 🎯 Solución Recomendada (Más Simple)

### Opción 1: Auto Manual en la Escena

1. Abre `Track1.unity` (o la escena del track que uses)
2. Arrastra `Car.prefab` a la escena
3. Posiciónalo en la posición inicial
4. Guarda la escena
5. Ejecuta el entrenamiento

### Opción 2: Usar el Script MLAgentsCarSpawner (Recomendado)

Ya creé el script `MLAgentsCarSpawner.cs` en `Assets/Scripts/AI/`. Para usarlo:

1. **Abre la escena del track** (ej: `Track1.unity`)
2. **Crea un GameObject vacío**:
   - Click derecho en la jerarquía → Create Empty
   - Nómbralo "MLAgentsCarSpawner"
3. **Agrega el componente**:
   - Selecciona el GameObject
   - Add Component → busca "ML Agents Car Spawner"
4. **Configura**:
   - **Number Of Cars**: `1` (para empezar, puedes aumentar después)
   - **Auto Spawn On Start**: ✅ (checked)
5. **Guarda la escena**

Este script creará automáticamente los autos cuando Unity entre en Play.

## 🔍 Verificación

Después de aplicar las soluciones:

1. **Abre Unity Editor**
2. **Carga `Main.unity`**
3. **Presiona Play**
4. **Verifica que aparezca al menos un auto** en la escena
5. **Verifica en la consola** que no haya errores de ML-Agents
6. **Ejecuta el script de entrenamiento**: `./train_mlagents.sh`
7. **Presiona Play en Unity** cuando el script lo indique

## 📝 Nota Importante

ML-Agents necesita que haya **al menos un agente activo** en la escena cuando Unity está en Play. Si no hay ningún agente, ML-Agents no puede entrenar.

El agente debe:
- Estar activo (GameObject activo)
- Tener el componente `CarAgent`
- Tener el componente `Behavior Parameters` configurado correctamente
- Estar en la escena cuando Unity está en Play

