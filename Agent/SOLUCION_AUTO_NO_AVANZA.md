# Solución: Auto Aparece Pero No Avanza

## 🔴 Problema

- El auto aparece en la escena
- Pero no se mueve (no avanza)

## ✅ Posibles Causas y Soluciones

### Problema 1: CarMovement No Está Aplicando Inputs

El `CarMovement` podría no estar aplicando los inputs cuando `UseUserInput` es false.

#### Verificación:

1. **Abre Unity Editor** y entra en Play mode
2. **Selecciona el auto** en la jerarquía
3. **En el Inspector**, verifica:
   - `CarMovement` → `enabled`: ✅ debe estar activo
   - `CarController` → `Use User Input`: ❌ debe estar en false (para ML-Agents)
   - `CarAgent` → debe estar presente y activo

#### Solución:

El código de `CarMovement` debería aplicar los inputs incluso cuando `UseUserInput` es false, porque `SetInputs()` se llama directamente. Pero verifica que:

1. **El `CarMovement` esté habilitado**:
   - Selecciona el auto
   - Verifica que el componente `CarMovement` tenga el checkbox activado

2. **El `CarController` esté habilitado**:
   - Verifica que el componente `CarController` esté activo

### Problema 2: ML-Agents No Está Enviando Acciones

ML-Agents podría no estar conectado correctamente o no estar enviando acciones.

#### Verificación:

1. **Verifica la consola de Unity**:
   - Busca mensajes de ML-Agents
   - Deberías ver: `[INFO] Connected to Unity environment...`
   - No deberías ver errores de conexión

2. **Verifica que el Behavior Parameters esté correcto**:
   - Behavior Name: `CarAgent` (exactamente)
   - Behavior Type: `Default` (no `Inference Only`)

#### Solución:

1. **Asegúrate de que ML-Agents esté conectado**:
   - Ejecuta el script de entrenamiento: `./train_mlagents.sh`
   - Espera a que veas: `[INFO] Connected to Unity environment...`
   - Luego presiona Play en Unity

2. **Verifica que no haya errores en la consola**:
   - Si hay errores, corrígelos antes de continuar

### Problema 3: El Auto Está en Modo Heuristic (Control Manual)

Si el Behavior Type está en modo que usa Heuristic, el auto esperará input del teclado.

#### Verificación:

1. **Selecciona el auto** en Unity
2. **En `Behavior Parameters`**:
   - **Behavior Type**: Debe ser `Default` (NO `Heuristic Only`)

#### Solución:

1. Cambia **Behavior Type** a `Default`
2. Guarda el prefab
3. Vuelve a ejecutar el entrenamiento

### Problema 4: El Auto Está Desactivado o Pausado

#### Verificación:

1. **Selecciona el auto** en la jerarquía
2. **Verifica que el GameObject esté activo** (checkbox en el Inspector)
3. **Verifica que todos los componentes estén habilitados**:
   - `CarController` ✅
   - `CarMovement` ✅
   - `CarAgent` ✅

### Problema 5: El Auto Está Fuera del Área de Movimiento

#### Verificación:

1. **Verifica la posición del auto**:
   - Debe estar en el track
   - No debe estar dentro de una pared
   - Debe estar en una posición válida

### Problema 6: CarMovement No Está Aplicando Física

#### Verificación en Código:

El `CarMovement` aplica movimiento en `FixedUpdate()`. Verifica que:

1. El método `ApplyInput()` se esté llamando
2. El método `ApplyVelocity()` se esté llamando
3. La velocidad no sea 0

#### Debug Temporal:

Puedes agregar un debug temporal en `CarAgent.OnActionReceived()`:

```csharp
public override void OnActionReceived(ActionBuffers actions)
{
    float turn = Mathf.Clamp(actions.ContinuousActions[0], -1f, 1f);
    float throttle = Mathf.Clamp(actions.ContinuousActions[1], -1f, 1f);
    
    Debug.Log($"ML-Agents Action: turn={turn}, throttle={throttle}");
    
    if (carMovement != null)
    {
        carMovement.SetInputs(new double[] { turn, throttle });
        Debug.Log($"CarMovement Velocity: {carMovement.Velocity}");
    }
}
```

Esto te ayudará a ver si:
- ML-Agents está enviando acciones
- Las acciones se están pasando a CarMovement
- La velocidad está cambiando

## 🎯 Solución Recomendada (Paso a Paso)

1. **Verifica la conexión de ML-Agents**:
   ```bash
   ./train_mlagents.sh
   ```
   Espera a ver: `[INFO] Connected to Unity environment...`

2. **En Unity Editor**:
   - Presiona Play
   - Selecciona el auto en la jerarquía
   - Verifica en el Inspector:
     - `CarAgent` está presente
     - `Behavior Parameters` → Behavior Type: `Default`
     - `CarMovement` → enabled: ✅
     - `CarController` → enabled: ✅

3. **Verifica la consola de Unity**:
   - No debería haber errores
   - Deberías ver mensajes de ML-Agents

4. **Si el auto sigue sin moverse**:
   - Agrega el debug temporal mencionado arriba
   - Ejecuta el entrenamiento
   - Revisa los logs para ver qué está pasando

## 🔍 Debug Adicional

### Verificar que CarMovement Recibe Inputs

Agrega esto temporalmente en `CarMovement.SetInputs()`:

```csharp
public void SetInputs(double[] input)
{
    horizontalInput = input[0];
    verticalInput = input[1];
    Debug.Log($"CarMovement.SetInputs: horizontal={horizontalInput}, vertical={verticalInput}, Velocity={Velocity}");
}
```

### Verificar que FixedUpdate Se Ejecuta

Agrega esto temporalmente en `CarMovement.FixedUpdate()`:

```csharp
void FixedUpdate()
{
    Debug.Log($"CarMovement.FixedUpdate: horizontalInput={horizontalInput}, verticalInput={verticalInput}, Velocity={Velocity}");
    // ... resto del código
}
```

Estos logs te ayudarán a identificar dónde se está perdiendo el movimiento.

