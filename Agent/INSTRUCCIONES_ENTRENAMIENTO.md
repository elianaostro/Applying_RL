# Instrucciones para Entrenar con ML-Agents

## ⚠️ Orden Correcto de Ejecución

El problema más común es el **orden de ejecución**. Sigue estos pasos EXACTAMENTE:

### Paso 1: Preparar Unity Editor

1. **Abrir Unity Editor** con el proyecto
2. **Cargar la escena `Main.unity`** que contiene el CarAgent
   - La escena está en: `UnityProject/Assets/Scenes/Main.unity`
   - Esta es la escena principal del proyecto
3. **Verificar que el Prefab Car tenga CarAgent y Behavior Parameters**:
   - ⚠️ **IMPORTANTE**: `CarAgent` y `Behavior Parameters` deben estar en el **prefab `Car`**, NO en `EvolutionManager`
   - Abre el prefab: `Assets/Prefabs/Car.prefab`
   - Verifica que tenga:
     - Componente `CarAgent`
     - Componente `Behavior Parameters` con:
       - **Behavior Name**: `CarAgent` (exactamente, case-sensitive)
       - **Behavior Type**: `Default` (NO `Inference Only`)
       - **Vector Observation > Space Size**: `6` (5 sensores + 1 velocidad)
       - **Actions > Space Size**: `2`, **Action Type**: `Continuous`
   - Si no los tiene, sigue las instrucciones en `CONFIGURAR_CARAGENT.md`

4. **NO presiones Play todavía** - Unity debe estar listo pero NO en ejecución

### Paso 2: Ejecutar el Script de Entrenamiento

```bash
cd Agent
./train_mlagents.sh
```

O con opciones:
```bash
./train_mlagents.sh --resume --run-id car_racing_ppo
```

### Paso 3: Cuando el Script Pida Confirmación

El script te pedirá que presiones ENTER. En ese momento:

1. **Presiona ENTER** en la terminal
2. **Inmediatamente después**, presiona **PLAY** en Unity Editor
3. El script esperará 10 segundos antes de iniciar mlagents-learn

### Paso 4: Verificar Conexión

Deberías ver en la terminal:
```
[INFO] Listening on port 5004. Start training by pressing the Play button in the Unity Editor.
[INFO] Connected to Unity environment with package version 2.0.2 and communication version 1.5.0
```

Si ves esto, ¡la conexión fue exitosa! El entrenamiento comenzará automáticamente.

## 🔧 Solución de Problemas

### Error: "UnityTimeOutException"

**Causa**: Unity no está en Play cuando mlagents-learn intenta conectarse.

**Solución**:
1. Asegúrate de que Unity esté en **Play** ANTES de que mlagents-learn se conecte
2. Verifica que el **Behavior Type** esté en `Default`
3. Verifica que el **Behavior Name** sea exactamente `CarAgent`
4. Intenta reiniciar Unity Editor

### Error: "Previous data from this run ID was found"

**Solución**:
```bash
# Continuar entrenamiento existente
./train_mlagents.sh --resume --run-id car_racing_ppo

# O sobrescribir datos existentes
./train_mlagents.sh --force --run-id car_racing_ppo

# O usar un nuevo run ID
./train_mlagents.sh --run-id nuevo_id
```

### Unity no se conecta

**Verificaciones**:
1. ✅ Unity Editor está abierto
2. ✅ La escena correcta está cargada
3. ✅ Unity está en modo **Play**
4. ✅ Behavior Parameters está configurado correctamente
5. ✅ El puerto 5004 no está bloqueado por firewall

### Ver el Progreso

Abre TensorBoard en otra terminal:
```bash
cd Agent
tensorboard --logdir results/car_racing_ppo
```

Luego abre http://localhost:6006 en tu navegador.

## 📝 Configuración del Behavior Parameters

En Unity Editor, el CarAgent debe tener:

- **Behavior Name**: `CarAgent` (exactamente como en el YAML)
- **Behavior Type**: `Default` (para entrenamiento)
- **Vector Observation**:
  - Space Size: número de sensores + 1 (ej: si tienes 5 sensores + velocidad = 6)
- **Actions**:
  - Continuous Actions > Space Size: `2` (turn, throttle)

## 🎯 Flujo Completo

```
1. Abrir Unity Editor
2. Cargar escena con CarAgent
3. Verificar Behavior Parameters
4. NO presionar Play todavía
5. Ejecutar: ./train_mlagents.sh
6. Cuando pida ENTER, presionar ENTER
7. Inmediatamente presionar PLAY en Unity
8. Esperar conexión exitosa
9. El entrenamiento comenzará automáticamente
```

