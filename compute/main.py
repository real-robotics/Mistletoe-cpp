import lcm
import time
from exlcm import quad_command_t, quad_state_t, velocity_command_t
import threading
import numpy as np 

import os 

from IMU import IMU
from StateEstimatorModel import StateEstimatorModel
from PPOPolicy import PPOPolicy

file_path = os.path.abspath(__file__)
directory_path = os.path.dirname(file_path)

ppo_policy = PPOPolicy(directory_path + '/rknn_models/ppo_policy.rknn')
state_estimator = StateEstimatorModel(directory_path + '/rknn_models/state_estimator.rknn')
imu = IMU()

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

# this is stupid but its to match the outputs of the network models
target_joint_pos = [0,0,0,0,0,0,0,0,0,0,0,0]
velocity_command = [0,0,0]

# observation items size of 48
# base_lin_vel, base_ang_vel, projected_gravity, velocity command of size 3
# joint pos,vel,action of size 12

# initailze to zeros, don't know how good this actually is
prev_action = [0,0,0,0,0,0,0,0,0,0,0,0]

def publish_state(position, velocity, bus_voltage, fault_code):
    state_c2d_msg = quad_state_t()
    state_c2d_msg.timestamp = time.time_ns()
    state_c2d_msg.position = position
    state_c2d_msg.velocity = velocity
    state_c2d_msg.bus_voltage = bus_voltage
    state_c2d_msg.fault_code = fault_code
    lc.publish("STATE_C2D", state_c2d_msg.encode())
        
def publish_command():
    global target_joint_pos

    command_msg = quad_command_t()
    command_msg.timestamp = time.time_ns()
    command_msg.position = target_joint_pos
    lc.publish("COMMAND", command_msg.encode())

def handle_state(channel, data):
    global target_joint_pos
    msg = quad_state_t.decode(data)
    # print(type(target_joint_pos))
    # print(target_joint_pos)
    # also this is kind of disgusting
    # have to do [0][0].tolist() because weird outputs of models
    state_estimator_input = imu.get_ang_vel() + imu.get_projected_gravity() + velocity_command + list(msg.position) + list(msg.velocity) + target_joint_pos
    # convert into format required for model
    state_estimator_input = np.array([state_estimator_input]).astype(np.float32)

    base_lin_vel = state_estimator.compute_lin_vel(state_estimator_input)[0][0].tolist()

    observation = base_lin_vel + imu.get_ang_vel() + imu.get_projected_gravity() + velocity_command + list(msg.position) + list(msg.velocity) + target_joint_pos

    observation = np.array([observation]).astype(np.float32)
    target_joint_pos = ppo_policy.compute_joint_pos(observation)
    publish_state(list(msg.position), list(msg.velocity), msg.bus_voltage, msg.fault_code)
    publish_command()

def handle_velocity_command(channel, data):
    global velocity_command

    velocity_command_msg = velocity_command_t.decode(data)
    velocity_command = [velocity_command_msg.lin_vel_x, velocity_command_msg.lin_vel_y, velocity_command_msg.ang_vel_z]

lc.subscribe("STATE_C2C", handle_state)
lc.subscribe("VELOCITY_COMMAND", handle_velocity_command)

def handle_lcm():
    while True:
        lc.handle()

handle_lcm()
