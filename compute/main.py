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
# target_joint_pos = (np.array([0.0000,  0.0000,  0.0000,  0.0000,  0.5236, -0.5236, -0.5236,  0.5236, 0.8727, -0.8727, -0.8727,  0.8727])/(2*np.pi)).tolist()
target_joint_pos = (np.zeros(12)/(2*np.pi)).tolist()
velocity_command = [0,0,0]

# observation items size of 48
# base_lin_vel, base_ang_vel, projected_gravity, velocity command of size 3
# joint pos,vel,action of size 12

# initailze to joint offset, don't know how good this actually is
# prev_action = (np.array([0.0000,  0.0000,  0.0000,  0.0000,  0.5236, -0.5236, -0.5236,  0.5236, 0.8727, -0.8727, -0.8727,  0.8727])/(2*np.pi)).tolist()
prev_action = (np.zeros(12)/(2*np.pi)).tolist()

# TODO: fix this messy manual command handling that was used for testing
# manual_command is by default false
manual_command_enabled = False

prev_position = 0

JOINT_OFFSETS = np.array([0.0000,  0.0000,  0.0000,  0.0000,  0.5236, -0.5236, -0.5236,  0.5236, 0.8727, -0.8727, -0.8727,  0.8727])

# joint offsets except in the order expected of the data from moteus.
SORTED_JOINT_OFFSETS = np.array([0.0000, 0.5236, 0.8727, 0.0000, -0.5236, -0.8727, 0.0000, -0.5236, -0.8727, 0.0000, 0.5236, 0.8727])

def parse_RL_inference_output(inference_output):
    # for whatever reason isaaclab scales output by 0.25, and then convert to radians, then convert to format that can be used by us
    scaled_output = inference_output[0]*0.25
    offset_output = ((scaled_output + JOINT_OFFSETS)/(2*np.pi))
    sorted_output = []
    for i in range(4):
        for j in range(12):
            if j%4==i:
                sorted_output.append(offset_output[j])

    return sorted_output

# sorts an array with the format expected from moteus (ie. 11,12,13,21,22, etc.) to format expected for isaaclab (ie. 11,21,31,41,12,22, etc.)
# thanks to chatgpt

def sort_moteus_to_isaaclab(arr):
    if len(arr) % 3 != 0:
        raise ValueError("The length of the array must be divisible by 3")
    
    grouped = [[], [], []]  # Three groups for idx % 3 = 0, 1, 2

    # Iterate over the array and group elements based on idx % 3
    for idx, value in enumerate(arr):
        grouped[idx % 3].append(value)

    # Flatten the grouped lists into a single list
    return grouped[0] + grouped[1] + grouped[2]

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
        
def publish_RL_command(target_joint_pos):
    command_msg = quad_command_t()
    command_msg.timestamp = time.time_ns()
    command_msg.position = target_joint_pos
    lc_pi.publish("COMMAND", command_msg.encode())


# numpy
def np_revs_to_radians(position_revs_arr):
    position_rads = (position_revs_arr*2*np.pi)
    return position_rads

def handle_state(channel, data):

    # print(imu.get_projected_gravity())

    global target_joint_pos
    global manual_command_enabled
    global prev_action
    # print(f'{target_joint_pos}\n{velocity_command}')
    
    msg = quad_state_t.decode(data)
    # print(f'lcm msg recieved: {msg}')
    # print(type(target_joint_pos))
    # print(target_joint_pos)
    # also this is kind of disgusting
    # have to do [0][0].tolist() because weird outputs of models

    # offsets are subtracted because mdp.joint_pos_rel is used in the RL policy training (meaning default offsets are subtracted during training for obs space)
    # use sort to moteus_to_isaaclab function because this is getting inputted as obs for policy trained on isaaclab.
    position_radians_rel = sort_moteus_to_isaaclab((np_revs_to_radians(np.array(list(msg.position))) - SORTED_JOINT_OFFSETS).tolist())
    velocity_radians_rel = sort_moteus_to_isaaclab((np_revs_to_radians(np.array(list(msg.velocity)))).tolist())
    
    # print(list(msg.position))

    # only publish RL based position commands when manual control is false
    if manual_command_enabled == False:
        # print(target_joint_pos)
        state_estimator_input = imu.get_ang_vel() + imu.get_projected_gravity() + velocity_command + position_radians_rel + velocity_radians_rel + prev_action
        # convert into format required for model
        state_estimator_input = np.array([state_estimator_input]).astype(np.float32)

        base_lin_vel = state_estimator.compute_lin_vel([state_estimator_input])[0][0].tolist()

        observation = base_lin_vel + imu.get_ang_vel() + imu.get_projected_gravity() + velocity_command + position_radians_rel + velocity_radians_rel + prev_action
        # print(position_radians_rel)
        # print(observation)
        observation = np.array([observation]).astype(np.float32)
        print(observation)
        # convert to format understandable by moteus
        inference_output = ppo_policy.compute_joint_pos([observation])
        target_joint_pos = parse_RL_inference_output(inference_output)
        prev_action = inference_output
        publish_RL_command(target_joint_pos)

    publish_state(list(msg.position), list(msg.velocity), msg.bus_voltage, msg.fault_code)

    # print('published stuff')

def handle_velocity_command(channel, data):
    # print('velocity command')
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
    global prev_position

    # print(imu.get_projected_gravity())
    
    if data is None:
        return
    
    msg = quad_command_t.decode(data)

    manual_command_enabled = msg.manual_command

    if abs(msg.position[2] - prev_position) > 0.1:
        print(abs(msg.position[2] - prev_position))
    prev_position = msg.position[2]

    # technically this should always be true, but just in case.
    if (manual_command_enabled == True):
        # print('forwarded command')
        # print(quad_command_t.decode(data).position)
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