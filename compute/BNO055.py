# TODO: Actually implment the reading of the sensor here

import random

class BNO055:

    def __init__(self):
        pass

    def get_projected_gravity(self):
        projected_gravity = [random.randint(), random.randint(), random.randint()]
        return projected_gravity
    
    def get_orientation(self):
        orientation = [random.randint(), random.randint(), random.randint()]
        return orientation

    def get_ang_vel(self):
        ang_vel = [random.randint(), random.randint(), random.randint()]
        return ang_vel
    
    