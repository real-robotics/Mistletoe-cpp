import lcm
import time
from exlcm import quad_command_t, quad_state_t, velocity_command_t, enabled_t
import threading
import numpy as np 

import os 

from IMU import IMU
from StateEstimatorModel import StateEstimatorModel
from PPOPolicy import PPOPolicy

import socket

file_path = os.path.abspath(__file__)
directory_path = os.path.dirname(file_path)

ppo_policy = PPOPolicy(directory_path + '/rknn_models/ppo_policy.rknn')
state_estimator = StateEstimatorModel(directory_path + '/rknn_models/state_estimator.rknn')
imu = IMU()

lc_pc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
lc_pi = lcm.LCM("udpm://239.255.77.67:7667?ttl=1")

pc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pc_addr = ('10.42.0.199', 7668)

# this is stupid but its to match the outputs of the network models
target_joint_pos = [0,0,0,0,0,0,0,0,0,0,0,0]
velocity_command = [0,0,0]

# observation items size of 48
# base_lin_vel, base_ang_vel, projected_gravity, velocity command of size 3
# joint pos,vel,action of size 12

# initailze to zeros, don't know how good this actually is
prev_action = [0,0,0,0,0,0,0,0,0,0,0,0]

manual_command_enabled = True

def publish_state(position, velocity, bus_voltage, fault_code):
    state_c2d_msg = quad_state_t()
    state_c2d_msg.timestamp = time.time_ns()
    state_c2d_msg.position = position
    state_c2d_msg.velocity = velocity
    state_c2d_msg.bus_voltage = bus_voltage
    state_c2d_msg.fault_code = fault_code

    # lc_pc.publish("STATE_C2D", state_c2d_msg.encode())
    pc_socket.sendto(state_c2d_msg.encode(), pc_addr)

    # print('published to c2d')
        
def publish_RL_command():
    global target_joint_pos

    command_msg = quad_command_t()
    command_msg.timestamp = time.time_ns()
    command_msg.position = target_joint_pos
    lc_pi.publish("COMMAND", command_msg.encode())

def handle_state(channel, data):
    print('state recieved')
    global target_joint_pos
    global manual_command_enabled
    
    msg = quad_state_t.decode(data)
    # print(f'lcm msg recieved: {msg}')
    # print(type(target_joint_pos))
    # print(target_joint_pos)
    # also this is kind of disgusting
    # have to do [0][0].tolist() because weird outputs of models
    
    # only publish RL based position commands when manual control is false
    if manual_command_enabled == False:
        state_estimator_input = imu.get_ang_vel() + imu.get_projected_gravity() + velocity_command + list(msg.position) + list(msg.velocity) + target_joint_pos
        # convert into format required for model
        state_estimator_input = np.array([state_estimator_input]).astype(np.float32)

        base_lin_vel = state_estimator.compute_lin_vel([state_estimator_input])[0][0].tolist()

        observation = base_lin_vel + imu.get_ang_vel() + imu.get_projected_gravity() + velocity_command + list(msg.position) + list(msg.velocity) + target_joint_pos

        observation = np.array([observation]).astype(np.float32)
        target_joint_pos = ppo_policy.compute_joint_pos([observation])
        publish_RL_command()

    publish_state(list(msg.position), list(msg.velocity), msg.bus_voltage, msg.fault_code)

    # print('published stuff')

def handle_velocity_command(channel, data):
    global velocity_command

    velocity_command_msg = velocity_command_t.decode(data)
    velocity_command = [velocity_command_msg.lin_vel_x, velocity_command_msg.lin_vel_y, velocity_command_msg.ang_vel_z]

def forward_enable_data(channel, data):
    if data is None:
        return
    print("ENABLED" if enabled_t.decode(data).enabled else "DISABLED")
    lc_pi.publish("ENABLED", data)

def forward_command_data(channel, data):
    global manual_command_enabled
    
    if data is None:
        return
    
    manual_command_enabled = quad_command_t.decode(data).manual_command

    # technically this should always be true, but just in case.
    if (manual_command_enabled == True):
        print('forwarded command')
        print(quad_command_t.decode(data).position)
        lc_pi.publish("COMMAND", data)

lc_pi.subscribe("STATE_C2C", handle_state)

lc_pc.subscribe("VELOCITY_COMMAND", handle_velocity_command)
lc_pc.subscribe("ENABLED", forward_enable_data)
lc_pc.subscribe("COMMAND", forward_command_data)

def handle_lc_pc():
    while True:
        lc_pc.handle()

def handle_lc_pi():
    while True:
        lc_pi.handle()

thread_pc = threading.Thread(target=handle_lc_pc)
thread_pi = threading.Thread(target=handle_lc_pi)

thread_pc.start()
thread_pi.start()