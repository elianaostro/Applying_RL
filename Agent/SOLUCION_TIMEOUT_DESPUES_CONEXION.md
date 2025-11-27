# Solución: Timeout Después de Conexión Exitosa

## 🔴 Problema

ML-Agents se conecta exitosamente:
```
[INFO] Listening on port 5004. Start training by pressing the Play button in the Unity Editor.
```

Pero luego falla con timeout:
```
UnityTimeOutException: The Unity environment took too long to respond.
```

## ✅ Soluciones

### Problema 1: El Agente No Está Respondiendo Correctamente

Cuando ML-Agents intenta hacer el reset del entorno, necesita que el agente responda. Si el agente no está configurado correctamente, no responderá.

#### Verificación:

1. **En Unity Editor (con Play activo)**:
   - Selecciona el auto en la jerarquía
   - Verifica en el Inspector:
     - `CarAgent` está presente y activo ✅
     - `Behavior Parameters` está presente y activo ✅
     - Behavior Name: `CarAgent` (exactamente) ✅
     - Behavior Type: `Default` ✅
     - Vector Observation Space Size: `6` ✅

2. **Verifica la consola de Unity**:
   - Busca errores relacionados con `CarAgent`
   - Busca errores de ML-Agents
   - Si hay errores, corrígelos primero

#### Solución:

1. **Asegúrate de que el prefab `Car` tenga todo configurado**:
   - Abre `Assets/Prefabs/Car.prefab`
   - Verifica que tenga `CarAgent` y `Behavior Parameters`
   - Guarda el prefab

2. **Si hay instancias del auto en la escena**:
   - Elimínalas
   - Deja que ML-Agents las cree automáticamente
   - O asegúrate de que sean instancias del prefab actualizado

### Problema 2: El Auto No Está Activo o Está Deshabilitado

#### Verificación:

1. **En Unity Editor (con Play activo)**:
   - Busca el auto en la jerarquía
   - Verifica que el GameObject esté activo (checkbox activado)
   - Verifica que todos los componentes estén habilitados:
     - `CarController` ✅
     - `CarMovement` ✅
     - `CarAgent` ✅
     - `Behavior Parameters` ✅

#### Solución:

1. **Asegúrate de que el auto esté activo**:
   - Si el auto está desactivado, actívalo
   - Si algún componente está deshabilitado, habilítalo

### Problema 3: OnEpisodeBegin Está Fallando

El método `OnEpisodeBegin()` del `CarAgent` podría estar fallando silenciosamente.

#### Verificación:

Agrega logs temporales en `CarAgent.OnEpisodeBegin()`:

```csharp
public override void OnEpisodeBegin()
{
    Debug.Log("[CarAgent] OnEpisodeBegin called");
    base.OnEpisodeBegin();
    
    if (carController == null)
    {
        Debug.LogError("[CarAgent] carController is NULL!");
        return;
    }
    
    Debug.Log("[CarAgent] Resetting car position");
    // ... resto del código
}
```

#### Solución:

1. Agrega los logs temporales
2. Ejecuta el entrenamiento
3. Revisa la consola de Unity para ver si `OnEpisodeBegin` se está llamando
4. Si hay errores, corrígelos

### Problema 4: CollectObservations Está Fallando

Si `CollectObservations()` falla, ML-Agents no puede obtener las observaciones y hace timeout.

#### Verificación:

Agrega logs temporales en `CarAgent.CollectObservations()`:

```csharp
public override void CollectObservations(VectorSensor sensor)
{
    try
    {
        Debug.Log("[CarAgent] CollectObservations called");
        
        if (sensors != null)
        {
            Debug.Log($"[CarAgent] Found {sensors.Length} sensors");
            foreach (Sensor s in sensors)
            {
                float normalizedOutput = Mathf.Clamp01(s.Output / 10f);
                sensor.AddObservation(normalizedOutput);
            }
        }
        else
        {
            Debug.LogWarning("[CarAgent] sensors is NULL, using default values");
            for (int i = 0; i < 5; i++)
                sensor.AddObservation(0f);
        }
        
        // ... resto del código
    }
    catch (System.Exception e)
    {
        Debug.LogError($"[CarAgent] Error in CollectObservations: {e.Message}");
        throw;
    }
}
```

### Problema 5: El Auto No Tiene Sensores

Si el auto no tiene sensores configurados, `CollectObservations` podría fallar.

#### Verificación:

1. **Selecciona el auto** en Unity
2. **Verifica que tenga sensores**:
   - Debe haber 5 sensores como hijos del GameObject del auto
   - Cada sensor debe tener el componente `Sensor`

#### Solución:

1. Si no hay sensores, agrégalos:
   - Crea 5 GameObjects hijos del auto
   - Agrega el componente `Sensor` a cada uno
   - Configúralos según tu diseño original

### Problema 6: Unity Está Pausado o Hay Errores

#### Verificación:

1. **Verifica que Unity NO esté pausado**:
   - El botón de Play debe estar activo (no pausado)
   - No debe haber un cuadro de diálogo bloqueando

2. **Revisa la consola de Unity**:
   - No debe haber errores rojos
   - Si hay errores, corrígelos antes de continuar

## 🎯 Solución Recomendada (Paso a Paso)

### Paso 1: Verificar Configuración del Prefab

1. Abre `Assets/Prefabs/Car.prefab`
2. Verifica:
   - ✅ `CarAgent` presente
   - ✅ `Behavior Parameters` presente
   - ✅ Behavior Name: `CarAgent`
   - ✅ Behavior Type: `Default`
   - ✅ Vector Observation Space Size: `6`
   - ✅ Actions Space Size: `2`, Type: `Continuous`
3. Guarda el prefab

### Paso 2: Limpiar la Escena

1. Abre la escena del track (ej: `Track1.unity`)
2. **Elimina cualquier instancia del auto** que esté en la escena
3. Guarda la escena

### Paso 3: Agregar Auto Manualmente (Temporal)

1. En la escena del track, arrastra el prefab `Car` a la escena
2. Posiciónalo en la posición inicial
3. Asegúrate de que esté activo
4. Guarda la escena

### Paso 4: Ejecutar con Debug

1. Agrega los logs temporales mencionados arriba
2. Ejecuta: `./train_mlagents.sh --force`
3. Presiona Play en Unity cuando se indique
4. Revisa la consola de Unity para ver los logs
5. Identifica dónde está fallando

### Paso 5: Verificar Consola de Unity

Busca en la consola:
- ¿Se llama `OnEpisodeBegin`?
- ¿Se llama `CollectObservations`?
- ¿Hay algún error?
- ¿El auto está activo?

## 🔍 Debug Avanzado

### Verificar que ML-Agents Detecta el Agente

En la consola de Unity, deberías ver mensajes como:
- `[ML-Agents] Agent CarAgent initialized`
- O mensajes similares cuando el agente se inicializa

Si no ves estos mensajes, ML-Agents no está detectando el agente.

### Verificar Comunicación

1. Abre la consola de Unity
2. Ejecuta el entrenamiento
3. Presiona Play en Unity
4. Observa los mensajes:
   - Deberías ver mensajes de conexión
   - Deberías ver mensajes de reset
   - No deberías ver timeouts inmediatos

## 📝 Checklist Final

Antes de ejecutar el entrenamiento:

- [ ] Prefab `Car` tiene `CarAgent` y `Behavior Parameters`
- [ ] Behavior Name es exactamente `CarAgent`
- [ ] Behavior Type es `Default`
- [ ] Vector Observation Space Size es `6`
- [ ] Actions Space Size es `2`, Type es `Continuous`
- [ ] El auto tiene 5 sensores configurados
- [ ] No hay errores en la consola de Unity
- [ ] Unity está en Play (no pausado)
- [ ] Hay al menos un auto activo en la escena

