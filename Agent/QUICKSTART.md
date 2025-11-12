# Inicio Rápido: Entrenar CarAgent con ML-Agents

## Pasos Rápidos

### 1. Instalar dependencias
```bash
cd Agent
pip install -r requirements.txt
```

### 2. Configurar Unity

En Unity Editor:
1. Abre la escena que contiene el `CarAgent`
2. Selecciona el GameObject con el `CarAgent`
3. En el componente **Behavior Parameters**:
   - **Behavior Name**: `CarAgent` (debe coincidir con el YAML)
   - **Behavior Type**: `Default` (no `Inference Only`)
   - **Vector Observation** → **Space Size**: `6`
   - **Actions** → **Space Size**: `2`, **Action Type**: `Continuous`

### 3. Entrenar

**Opción A: Con Unity Editor (desarrollo)**
```bash
cd Agent
python envs/train_car_mlagents.py
```
Luego presiona **Play** en Unity cuando veas el mensaje de conexión.

**Opción B: Con build de Unity (entrenamiento largo)**
```bash
cd Agent
python envs/train_car_mlagents.py --env ../Build/Applying\ EANNs.exe --num-envs 4
```

### 4. Monitorear
```bash
tensorboard --logdir results/car_racing_ppo
```

## Archivos Importantes

- **Configuración**: `Agent/config/car_racing_config.yaml`
- **Script de entrenamiento**: `Agent/envs/train_car_mlagents.py`
- **Documentación completa**: `Agent/MLAGENTS_TRAINING.md`

## Solución Rápida de Problemas

- **"No connection"**: Asegúrate de que Unity esté ejecutándose y la escena esté abierta
- **"Behavior name mismatch"**: Verifica que el Behavior Name sea `CarAgent` en Unity
- **Puerto ocupado**: Usa `--base-port 5005`

