## PPO training with Unity lane simulator

**Nota importante:** Este proyecto ha sido modificado para que toda la lógica de AI se ejecute en Python usando Unity ML-Agents. El sistema de Agent en C# (red neuronal local) es ahora opcional y solo se usa para el modo de evolución genética. 

### Opciones de entrenamiento:

1. **Unity ML-Agents (Recomendado)**: Usa `CarAgent` con ML-Agents para entrenamiento desde Python
2. **RLBridgeServer (Legacy)**: Sistema TCP bridge para control externo

## Entrenamiento con Unity ML-Agents

### 1) Configuración en Unity
- Abre el proyecto en `UnityProject`
- Asegúrate de que el paquete `com.unity.ml-agents` esté instalado (ya está en `manifest.json`)
- En la escena de entrenamiento:
  - Agrega el componente `CarAgent` al GameObject del carro (o al prefab del carro)
  - Asigna las referencias en el Inspector:
    - `Car Controller`: El componente CarController del mismo GameObject
    - `Car Movement`: El componente CarMovement del mismo GameObject
    - `Track Manager`: El TrackManager de la escena
  - Ajusta las recompensas en el Inspector si es necesario
  - **Opcional**: Agrega el componente `MLAgentsAutoTrainer` a un GameObject en la escena para iniciar el entrenamiento automáticamente al presionar Play

### 2) Instalación de Python
```bash
cd python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Entrenar con ML-Agents

#### Opción A: Automático (Recomendado)
1. Agrega el componente `MLAgentsAutoTrainer` a un GameObject en la escena
2. Presiona Play en Unity
3. El entrenamiento se iniciará automáticamente

#### Opción B: Manual
```bash
# Desde el directorio python/
mlagents-learn config/car_racing_config.yaml --run-id=car_racing_ppo --env=../UnityProject
```

O usando el script Python:
```bash
python train_car_mlagents.py
```

### 4) Visualizar entrenamiento
```bash
tensorboard --logdir results
```

## Sistema Legacy: RLBridgeServer (TCP Bridge)

### 1) In Unity
- Open the project at `UnityProject`.
- Add the `RLBridgeServer` MonoBehaviour to an active GameObject in the training scene (e.g., `Main.unity`).
- The `RLBridgeServer` will automatically find or create a `CarController`:
  - First tries to use a car assigned in the Inspector
  - Then tries to instantiate from an assigned prefab
  - Then tries to find an existing car in the scene
  - Then tries to use `TrackManager`'s `PrototypeCar`
  - Finally tries to load from Resources
- **No Agent required:** When using `RLBridgeServer`, the `CarController` doesn't need an `Agent` component. The AI logic runs entirely in Python.
- Press Play; the Console should show `RLBridgeServer listening on 127.0.0.1:5555`.

### 2) Python setup
```bash
cd python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 3) Quick check
```python
from rl_bridge.envs.unity_lane_env import make_env
env = make_env()
obs, _ = env.reset()
print(obs.shape)
obs, r, term, trunc, info = env.step([0.0, 0.2])
print(r, term)
env.close()
```

### 4) Train PPO
```bash
python train_ppo.py --timesteps 200000 --logdir runs/ppo_lane
```

### 5) Notebook
Open `notebooks/ppo_experiments.ipynb` for an end-to-end walkthrough and analysis.




### 6) Test with CartPole
First, train the model:
```bash
python python/PPO/train_cartpole_ppo.py --timesteps 100000 --logdir runs/cartpole_ppo_clip
```

Then, evaluate the model:
```bash
python python/PPO/eval_cartpole_ppo.py --weights runs/cartpole_ppo_clip/final.pt --episodes 10
```

To evaluate the model with rendering, add the `--render` flag:
```bash
python python/PPO/eval_cartpole_ppo.py --weights runs/cartpole_ppo_clip/final.pt --episodes 10 --render
```

### 7) Test with BipedalWalker
First, train the model:
```bash
python python/PPO/train_bipedalwalker_ppo.py --timesteps 10000000 --logdir runs/bipedalwalker_ppo_clip
```

Then, evaluate the model:
```bash
python python/PPO/eval_bipedalwalker_ppo.py --weights runs/bipedalwalker_ppo_clip/final.pt --episodes 10
```

To evaluate the model with rendering, add the `--render` flag:
```bash
python python/PPO/eval_bipedalwalker_ppo.py --weights runs/bipedalwalker_ppo_clip/final.pt --episodes 10 --render
```


### 8) Test with MountainCar
First, train the model:
```bash
python python/PPO/train_mountain_car_ppo.py --timesteps 10000000 --logdir runs/mountain_car_ppo_clip
```

Then, evaluate the model:
```bash
python python/PPO/eval_mountain_car_ppo.py --weights runs/mountain_car_ppo_clip/final.pt --episodes 10
```

To evaluate the model with rendering, add the `--render` flag:
```bash
python python/PPO/eval_mountain_car_ppo.py --weights runs/mountain_car_ppo_clip/final.pt --episodes 10 --render
```

### Check tests in:
Open `python/PPO/env_tests.ipynb` for tests of PPO Clip in different environments.