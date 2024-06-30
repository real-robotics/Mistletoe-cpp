# TODO: actually implement the model here

import random

class StateEstimatorModel:
    def __init__(self, model_path) -> None:
        pass


    # takes a list of 45 items that includes the following in this specific order:
    # base_ang_vel, projected_gravity, velocity command of size 3
    # joint pos,vel,action of size 12
    def compute_lin_vel(state):
        lin_vel_x = random.randint()
        lin_vel_y = random.randint()
        lin_vel_z = random.randint()
        return [lin_vel_x, lin_vel_y, lin_vel_z]