# Cómo Poner Unity en Play Mode

## 🎮 Pasos Simples

### Paso 1: Abrir Unity Editor

1. Abre Unity Editor con tu proyecto
2. Asegúrate de que la escena `Main.unity` esté cargada

### Paso 2: Verificar la Escena

1. En la jerarquía (panel izquierdo), verifica que tengas:
   - `Main Camera`
   - `GameStateManager`
   - `EvolutionManager` (puede estar desactivado)
   
2. Verifica que la escena del track se cargue automáticamente (esto lo hace `GameStateManager`)

### Paso 3: Verificar que Haya un Auto

1. **Opción A**: Si agregaste el auto manualmente a la escena del track:
   - Abre la escena del track (ej: `Track1.unity`)
   - Verifica que haya un GameObject con el prefab `Car`
   - El auto debe estar activo (checkbox activado)

2. **Opción B**: Si usas el script `MLAgentsCarSpawner`:
   - El auto se creará automáticamente cuando presiones Play

### Paso 4: Presionar el Botón Play

1. **Busca el botón Play** en la parte superior del Editor de Unity:
   ```
   [▶]  Play
   ```
   Está en la barra de herramientas, cerca del centro.

2. **Haz clic en el botón Play** (o presiona la tecla `P`)

3. **Verifica que esté en Play mode**:
   - El botón se volverá azul/activo
   - Verás `[▶]` cambiado a `[⏸]` (pausa)
   - La escena comenzará a ejecutarse

### Paso 5: Verificar que Funciona

1. **En la jerarquía**, deberías ver el auto activo
2. **En la vista Scene o Game**, deberías ver el auto en el track
3. **En la consola de Unity** (panel inferior), no debería haber errores rojos

## ⚠️ Orden Correcto de Ejecución

### Para `train_custom_ppo.py`:

1. **Abre Unity Editor** con el proyecto
2. **Carga la escena `Main.unity`**
3. **NO presiones Play todavía**
4. **Ejecuta el script**:
   ```bash
   cd Agent
   ./train_custom_ppo.sh
   ```
5. **Espera a que el script muestre**:
   ```
   Conectando con Unity...
   ✓ Conectado a Unity
   ...
   NOTA: Asegúrate de que Unity esté en Play mode
   ```
6. **AHORA presiona Play en Unity**
7. El entrenamiento comenzará automáticamente

## 🔍 Verificación Visual

Cuando Unity está en **Play mode**:
- ✅ El botón Play está activo/azul
- ✅ La escena se está ejecutando
- ✅ Puedes ver el auto moviéndose (después de que se conecte)
- ✅ La consola muestra mensajes de ML-Agents

Cuando Unity **NO está en Play mode**:
- ❌ El botón Play está gris/inactivo
- ❌ La escena no se ejecuta
- ❌ No hay movimiento

## 🎯 Atajos de Teclado

- **Presionar `P`**: Alterna Play/Pause
- **Presionar `Ctrl+P`**: También inicia Play mode

## 📝 Notas Importantes

1. **Unity debe estar en Play ANTES de que el script intente conectarse** (o muy poco después)
2. **Si presionas Play demasiado tarde**, el script hará timeout
3. **Si presionas Play demasiado temprano**, puede que no se conecte correctamente
4. **El mejor momento**: Justo después de que el script muestre "Conectando con Unity..."

## 🔧 Si No Funciona

### El botón Play no hace nada:

1. Verifica que no haya errores de compilación en Unity
2. Revisa la consola de Unity para errores
3. Intenta cerrar y reabrir Unity

### El script no se conecta:

1. Asegúrate de que Unity esté en Play mode
2. Verifica que haya al menos un auto activo en la escena
3. Verifica que el `Behavior Parameters` esté configurado correctamente
4. Revisa la consola de Unity para errores

### El auto no aparece:

1. Verifica que el auto esté en la escena del track
2. O usa el script `MLAgentsCarSpawner` para crearlo automáticamente
3. Verifica que el prefab `Car` tenga todos los componentes necesarios

