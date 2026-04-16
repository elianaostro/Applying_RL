import gymnasium as gym
from gymnasium import spaces
import numpy as np


CUSTOM_ENVS = {}  # populated after class definitions


def make_env(env_name: str, seed: int, render_mode: str = None) -> gym.Env:
    """Create environment - supports both Gymnasium and custom environments."""
    if env_name in CUSTOM_ENVS:
        env = CUSTOM_ENVS[env_name]()
        env.reset(seed=seed)
        return env

    try:
        kwargs = {"render_mode": render_mode} if render_mode else {}
        env = gym.make(env_name, **kwargs)
        env.reset(seed=seed)
        return env
    except Exception as e:
        error_str = str(e).lower()
        error_type = type(e).__name__

        if "pygame" in error_str or "DependencyNotInstalled" in error_type:
            if render_mode:
                print("Warning: pygame not installed. Rendering disabled.")
                env = gym.make(env_name, render_mode=None)
                env.reset(seed=seed)
                return env
            raise Exception("pygame is required. Install with: pip install pygame")

        if "box2d" in error_str or "Box2D" in error_str:
            print("ERROR: Box2D is required but not installed.")
            print("Install via: conda install -c conda-forge box2d-py")
        raise


class ConstantRewardEnv(gym.Env):
    def __init__(self):
        """Initialize ConstantRewardEnv"""
        super().__init__()
        self.observation_space = spaces.Discrete(1) # 0 constant observation
        self.action_space = spaces.Discrete(1)  # 1 action: 0 (reward = 1)

        self.done = False
        self.obs = 0

    def reset(self, seed=None, options=None):
        """Reset ConstantRewardEnv"""
        super().reset(seed=seed)
        self.done = False
        info = {}
        return self.obs, info

    def step(self, action):
        """Step ConstantRewardEnv"""
        assert self.action_space.contains(action), "Acción inválida"
        
        if self.done:
            raise RuntimeError("El episodio ya terminó. Llama a reset().")

        reward = 1

        self.done = True
        terminated = True
        truncated = False
        info = {}

        return self.obs, reward, terminated, truncated, info
    
    def render(self):
        """Render ConstantRewardEnv"""
        print("Entorno ConstantRewardEnv (observación siempre = 0)")


class RandomObsBinaryRewardEnv(gym.Env):
    def __init__(self):
        """Initialize RandomObsBinaryRewardEnv"""
        super().__init__()
        self.observation_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.int64)
        self.action_space = spaces.Discrete(1)  # 1 action

        self.done = False
        self.obs = np.random.choice([-1, 1])

    def reset(self, seed=None, options=None):
        """Reset RandomObsBinaryRewardEnv"""
        super().reset(seed=seed)
        self.done = False
        self.obs = np.random.choice([-1, 1])
        info = {}
        return self.obs, info

    def step(self, action):
        """Step RandomObsBinaryRewardEnv"""
        assert self.action_space.contains(action), "Acción inválida"
        
        if self.done:
            raise RuntimeError("El episodio ya terminó. Llama a reset().")

        reward = self.obs 

        self.done = True
        terminated = True
        truncated = False
        info = {}

        return self.obs, reward, terminated, truncated, info
    
    def render(self):
        """Render RandomObsBinaryRewardEnv"""
        print(f"Observación: {self.obs}, Recompensa: {self.obs}")


class TwoStepDelayedRewardEnv(gym.Env):
    def __init__(self):
        """Initialize TwoStepDelayedRewardEnv"""
        super().__init__()
        self.observation_space = spaces.Discrete(2) # 0 in the first step, 1 in the second step
        self.action_space = spaces.Discrete(1)  # 1 action

        self.done = False
        self.obs = 0
        self.step_count = 0

    def reset(self, seed=None, options=None):
        """Reset TwoStepDelayedRewardEnv"""
        super().reset(seed=seed)
        self.done = False
        self.step_count = 0
        info = {}
        return self.obs, info

    def step(self, action):
        """Step TwoStepDelayedRewardEnv"""
        assert self.action_space.contains(action), "Acción inválida"

        if self.done:
            raise RuntimeError("El episodio ya terminó. Llama a reset().")

        if self.step_count == 0:
            self.obs = 0
            reward = 0
            terminated = False
        elif self.step_count == 1:
            self.obs = 1
            reward = 1
            terminated = True
        else:
            raise RuntimeError("El episodio ya terminó. Llama a reset().")

        truncated = False
        self.done = terminated
        info = {}
        
        self.step_count += 1

        return self.obs, reward, terminated, truncated, info
    
    def render(self):
        """Render TwoStepDelayedRewardEnv"""
        print(f"Step: {self.step_count}, Obs: {self.obs}, Done: {self.done}")


# Register custom environments for make_env lookup
CUSTOM_ENVS.update({
    "ConstantRewardEnv": ConstantRewardEnv,
    "RandomObsBinaryRewardEnv": RandomObsBinaryRewardEnv,
    "TwoStepDelayedRewardEnv": TwoStepDelayedRewardEnv,
})