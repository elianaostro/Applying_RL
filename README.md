# Applying Reinforcement Learning to Car Navigation

A 2D Unity simulation in which cars learn to navigate themselves through different courses. The cars are steered by a feedforward Neural Network. The weights of the network can be trained using Reinforcement Learning (PPO) via ML-Agents.
Short demo video of an early version: https://youtu.be/rEDzUT3ymw4


![](Images/Demo.gif)


## The Simulation

Cars have to navigate through a course without touching the walls or any other obstacles of the course. A car has five front-facing sensors which measure the distance to obstacles in a given direction. The readings of these sensors serve as the input of the car's neural network. Each sensor points into a different direction, covering a front facing range of approximately 90 degrees. The maximum range of a sensor is 10 unity units. The output of the Neural Network then determines the car’s current engine and turning force.


<img src="Images/Car.png" width="250">


If you would like to tinker with the parameters of the simulation, you can do so in the Unity Editor. The simulation can be run directly from the Unity Editor or using the built executables in the [Build/](Build/) directory.


## The Neural Network

The Neural Network used is a standard, fully connected, feedforward Neural Network. For Reinforcement Learning training, the network architecture is defined in the PPO implementation and can be configured through the training scripts. The network receives observations from the car's sensors and outputs actions (engine and turning forces).


## Training the Neural Network

The weights of the Neural Network are trained using Reinforcement Learning, specifically Proximal Policy Optimization (PPO). The training is implemented using ML-Agents, which connects the Unity simulation with a Python-based PPO algorithm.

The training infrastructure is located in the [Agent/](Agent/) directory, which contains:
- A custom PPO implementation in [Agent/PPO/](Agent/PPO/)
- Training scripts for Unity car agents in [Agent/car_agent/](Agent/car_agent/)
- Support for hyperparameter optimization using Optuna
- Scripts for training and evaluation

The Unity side of the training uses the `CarAgent` component ([UnityProject/Assets/Scripts/AI/CarAgent.cs](UnityProject/Assets/Scripts/AI/CarAgent.cs)), which implements the ML-Agents interface to collect observations, receive actions, and provide rewards. For detailed information on how to train the agents, see the [Agent/README.md](Agent/README.md) file.


## User Interface

The user interface displays information about the simulation and the current car's state. The UI code is located at [UnityProject/Assets/Scripts/GUI/](UnityProject/Assets/Scripts/GUI/).


## Courses

There are multiple courses of different difficulties which are all located in different unity scenes and can be found in the folder [UnityProject/Assets/Scenes/](UnityProject/Assets/Scenes/).

In order to start the simulation on a specific course, open the Main scene and enter the desired track-name (= scene name) in the Inspector of the GameStateManager object.



![Two different courses the cars can be trained on.](Images/Courses.png)


## License

Feel free to use my code in your personal projects. I would be very interested in any work that originates from this project. I would be more than happy to hear from your impressions and results, so feel free to mail me at arzt.samuel@live.de.
You can also follow me on twitter: https://twitter.com/SamuelArzt


