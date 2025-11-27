# Cómo Configurar Correctamente el CarAgent en Unity

## ⚠️ Problema Actual

Tienes `CarAgent` y `Behavior Parameters` en `EvolutionManager`, pero **deben estar en el prefab `Car`**.

## ✅ Configuración Correcta

### Paso 1: Abrir el Prefab Car

1. En Unity Editor, navega a `Assets/Prefabs/Car.prefab`
2. **Haz doble clic** en el prefab para abrirlo en modo de edición de prefab
3. O selecciona el prefab y haz clic en "Open Prefab" en el Inspector

### Paso 2: Agregar CarAgent al Prefab

1. Con el prefab `Car` abierto, selecciona el GameObject raíz del prefab
2. En el Inspector, haz clic en **"Add Component"**
3. Busca y agrega: **"Car Agent"** (el script `CarAgent.cs`)
4. Si no aparece, verifica que el script `CarAgent.cs` esté en `Assets/Scripts/AI/`

### Paso 3: Configurar CarAgent

En el componente `CarAgent` que acabas de agregar:

1. **Car Controller**: Arrastra el componente `CarController` del mismo GameObject (o déjalo vacío, se asignará automáticamente)
2. **Car Movement**: Arrastra el componente `CarMovement` del mismo GameObject (o déjalo vacío, se asignará automáticamente)
3. **Track Manager**: Déjalo vacío (se buscará automáticamente)
4. **Reward Settings**: Puedes ajustar los valores según necesites:
   - Checkpoint Reward: `1.0`
   - Wall Hit Penalty: `-10.0`
   - Timeout Penalty: `-5.0`
   - Progress Reward Multiplier: `0.1`

### Paso 4: Agregar Behavior Parameters

1. Con el mismo GameObject seleccionado, haz clic en **"Add Component"**
2. Busca y agrega: **"Behavior Parameters"** (componente de ML-Agents)

### Paso 5: Configurar Behavior Parameters

En el componente `Behavior Parameters`:

1. **Behavior Name**: `CarAgent` (debe coincidir exactamente con el nombre en `car_racing_config.yaml`)
2. **Behavior Type**: `Default` (NO `Inference Only`)
3. **Vector Observation**:
   - **Space Size**: `6` ⚠️ **IMPORTANTE: Debe ser 6, NO 1**
     - 5 sensores (delanteros)
     - 1 velocidad
   - **Stacked Vectors**: `1`
4. **Actions**:
   - **Space Size**: `2` (turn, throttle)
   - **Action Type**: `Continuous`
5. **Model**: Déjalo vacío (se asignará cuando uses un modelo entrenado)

⚠️ **Error común**: Si ves el error "More observations (6) made than vector observation size (1)", significa que el Space Size está en 1 en lugar de 6. Cámbialo a 6.

### Paso 6: Guardar el Prefab

1. Haz clic en el botón **"Overrides"** en la parte superior del Inspector (si aparece)
2. Selecciona **"Apply All"** para guardar los cambios en el prefab
3. O haz clic en la flecha hacia atrás para salir del modo de edición de prefab

### Paso 7: Remover CarAgent de EvolutionManager

1. En la escena `Main.unity`, selecciona el GameObject `EvolutionManager`
2. En el Inspector, busca el componente `CarAgent`
3. Haz clic en los **tres puntos** (⋮) del componente
4. Selecciona **"Remove Component"**
5. Repite lo mismo para `Behavior Parameters` si está en EvolutionManager

## ✅ Verificación Final

### En el Prefab Car:

- ✅ Tiene componente `CarController`
- ✅ Tiene componente `CarMovement`
- ✅ Tiene componente `CarAgent` (nuevo)
- ✅ Tiene componente `Behavior Parameters` (nuevo)
- ✅ Behavior Parameters tiene:
  - Behavior Name: `CarAgent`
  - Behavior Type: `Default`
  - Vector Observation Space Size: `6`
  - Actions Space Size: `2`, Type: `Continuous`

### En la Escena Main.unity:

- ✅ `EvolutionManager` NO tiene `CarAgent`
- ✅ `EvolutionManager` NO tiene `Behavior Parameters`
- ✅ `GameStateManager` tiene configurado el `TrackName` (ej: "Track1", "Track2", etc.)

### En la Escena del Track (cargada dinámicamente):

- ✅ La escena del track (ej: `Track1.unity`) contiene el `TrackManager`
- ✅ `TrackManager` tiene referencia al `PrototypeCar` (que es el prefab Car)
- ✅ El `PrototypeCar` en el `TrackManager` debe ser el prefab `Car` que configuraste

## 🎯 Por Qué Esta Configuración

- **ML-Agents** necesita que cada agente individual tenga su propio componente `Agent` y `Behavior Parameters`
- El `TrackManager` instancia múltiples copias del `PrototypeCar` (prefab Car)
- Cada copia necesita su propio `CarAgent` para que ML-Agents pueda controlarlo
- `EvolutionManager` es un manager, no un agente individual

## 📝 Nota sobre EvolutionManager

Si `EvolutionManager` era parte del sistema de algoritmos genéticos original, puedes:
- Desactivarlo cuando uses ML-Agents
- O mantenerlo pero sin los componentes de ML-Agents
- ML-Agents manejará el entrenamiento, no el algoritmo genético

## 🔍 Verificar Configuración del TrackManager

El `TrackManager` está en la escena del track (no en Main.unity). Para verificar:

1. **Abre la escena del track** que está configurada en `GameStateManager.TrackName`:
   - Ejemplo: Si `TrackName = "Track1"`, abre `Assets/Scenes/Tracks/Track1.unity`

2. **En la escena del track**, busca el GameObject `TrackManager` en la jerarquía

3. **Selecciona `TrackManager`** y en el Inspector verifica:
   - **Prototype Car**: Debe estar asignado al prefab `Car` que configuraste
   - Si está vacío o asignado a otro objeto, arrastra el prefab `Car` desde `Assets/Prefabs/Car.prefab`

4. **Importante**: El `PrototypeCar` en el `TrackManager` debe ser el mismo prefab `Car` que tiene `CarAgent` y `Behavior Parameters`

## 🔍 Si No Funciona

1. Verifica que el prefab `Car` tenga todos los componentes necesarios:
   - `CarController`
   - `CarMovement`
   - `CarAgent` ✅
   - `Behavior Parameters` ✅

2. Verifica que `TrackManager.PrototypeCar` esté asignado al prefab `Car`:
   - Abre la escena del track (ej: `Track1.unity`)
   - Selecciona `TrackManager`
   - Verifica que `Prototype Car` apunte al prefab `Car`

3. Verifica que el Behavior Name sea exactamente `CarAgent` (case-sensitive)

4. Verifica que el Behavior Type sea `Default` (no `Inference Only`)

5. Asegúrate de que la escena `Main.unity` esté abierta cuando ejecutes el entrenamiento

