# TODO: Actually implment the reading of the sensor here

import random
import time
from Adafruit_BNO055 import BNO055

class IMU:

    def __init__(self):
        self.sensor = BNO055.BNO055(busnum=1)
        if not self.sensor.begin():
            raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

    def get_projected_gravity(self):
        projected_gravity = [self.sensor.read_gravity()[0], self.sensor.read_gravity()[1], self.sensor.read_gravity()[2]]
        return projected_gravity
    
    def get_orientation(self):
        orientation = [self.sensor.read_euler()[0], self.sensor.read_euler()[1], self.sensor.read_euler()[2]]
        return orientation

    def get_ang_vel(self):
        ang_vel = [self.sensor.read_gyroscope()[0], self.sensor.read_gyroscope()[1], self.sensor.read_gyroscope()[2]]
        return ang_vel
    
    