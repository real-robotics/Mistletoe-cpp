import threading
import lcm
from time import time
import time
import numpy as np 
import os 
from IMU import IMU
import socket

from utils import parse_RL_inference_output, sort_moteus_to_isaaclab, np_revs_to_radians, generate_session_filename, log_observations_and_actions

# INITIALIZATION

# standing position offsets used in isaaclab, in radians
JOINT_OFFSETS = np.array([0.0000,  0.0000,  0.0000,  0.0000,  0.5236, -0.5236, -0.5236,  0.5236, 0.8727, -0.8727, -0.8727,  0.8727])

# joint offsets except in the order expected of the data from moteus.
SORTED_JOINT_OFFSETS = np.array([0.0000, 0.5236, 0.8727, 0.0000, -0.5236, -0.8727, 0.0000, -0.5236, -0.8727, 0.0000, 0.5236, 0.8727])

# LCM setup

imu = IMU()

prev_action = (np.zeros(12)/(2*np.pi)).tolist()
velocity_command = [0, 0, 0]

# Shared state for latest observation
latest_state = None
state_lock = threading.Lock()

enabled = False 
enabled_lock = threading.Lock()

def send_command_via_lcm(action):
    print(f'action published to control: {action}')

# Function to run the RL policy at a fixed rate using delta time
def run_policy_loop(frequency=200):
    global prev_action    
    while True:        
        # Get the latest state
        with state_lock:
            if latest_state is None:
                continue  # Skip if no state is available yet
            # Extract the most recent state
            received_state = latest_state

        # Get the most recent IMU data (non-blocking)
        with imu_lock:
            if imu_data is None:
                continue  # Skip if no state is available yet
            ang_vel, grav_proj = imu_data

        # Process the state for RL input
        position_radians_rel = sort_moteus_to_isaaclab(np_revs_to_radians(np.array(received_state.position)) - SORTED_JOINT_OFFSETS) 
        velocity_radians_rel = sort_moteus_to_isaaclab(np_revs_to_radians(np.array(received_state.velocity)))

        state_estimator_input = ang_vel + grav_proj + position_radians_rel + velocity_radians_rel + prev_action
        state_estimator_input = np.array([state_estimator_input]).astype(np.float32)

        # Estimate base linear velocity
        base_lin_vel = state_estimator.compute_lin_vel([state_estimator_input])[0][0].tolist()

        # Prepare the observation for the RL policy
        observation = base_lin_vel + ang_vel + grav_proj + velocity_command + position_radians_rel + velocity_radians_rel + prev_action
        observation = np.array([observation]).astype(np.float32)

        # TEST POINT 
        inference_output = np.zeros(12).tolist()

        action = parse_RL_inference_output(inference_output, JOINT_OFFSETS)
        
        send_command_via_lcm(action)

        with enabled_lock:
            if enabled == True:
                prev_action = inference_output
            elif enabled == False:
                prev_action = np.zeros(12).tolist()

def handle_velocity_command(channel, data):
    global velocity_command

    lin_vel_x = 0
    lin_vel_y = 0
    ang_vel_z = 0

    velocity_command = [lin_vel_x, lin_vel_y, ang_vel_z]

imu_data = None
imu_lock = threading.Lock()

# Asynchronous IMU reader thread
def read_imu_async():
    global imu_data
    while True:
        ang_vel = imu.get_ang_vel()
        grav_proj = imu.get_projected_gravity()
        with imu_lock:
            imu_data = (ang_vel, grav_proj)
            # print(imu_data)

# Start the policy loop
def main():
    print("Starting policy rollout at 200hz")
    run_policy_loop(frequency=200)

if __name__ == "__main__":
    main()