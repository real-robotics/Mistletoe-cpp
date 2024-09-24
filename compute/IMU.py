# TODO: Actually implment the reading of the sensor here

import random
import time
from Adafruit_BNO055 import BNO055
import math

class IMU:

    def __init__(self):
        self.sensor = BNO055.BNO055(busnum=1)

        if not self.sensor.begin():
            raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')

    #axes flipped:
    # x: same
    # y: flipped
    # z: same

    # gravity m/s^2 stays the same

    def get_projected_gravity(self):
        # sys, gyro, accel, mag = self.sensor.get_calibration_status()
        # print(f'{sys} {gyro} {accel} {mag}')
        projected_gravity = [self.sensor.read_gravity()[0], -1 * self.sensor.read_gravity()[1], self.sensor.read_gravity()[2]]
        return projected_gravity
    
    def get_orientation(self):
        orientation = [self.sensor.read_euler()[0], self.sensor.read_euler()[1], self.sensor.read_euler()[2]]
        return orientation

    # order is weird because the output is not in the format used for observation space in policy
    # output of the read_gyroscope function is heading, roll, pitch, or z,y,x so it must be flipped

    # axes flipped:
    # z-vel: flipped
    # y-vel: same
    # x-vel: flipped

    # units are in degrees, we need to convert to rads for the policy obs

    def get_ang_vel(self):
        ang_vel = [-1 * self.degrees_to_rads(self.sensor.read_gyroscope()[2]), self.degrees_to_rads(self.sensor.read_gyroscope()[1]), -1 * self.degrees_to_rads(self.sensor.read_gyroscope()[0])]
        return ang_vel
    
    def degrees_to_rads(self, angle_degrees):
        angle_radians = angle_degrees * (math.pi/180)
        return angle_radians