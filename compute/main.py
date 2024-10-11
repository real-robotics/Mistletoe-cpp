import threading
import lcm
from time import time
from exlcm import quad_command_t, quad_state_t, velocity_command_t, enabled_t
import time
import numpy as np 
import os 
from IMU import IMU
from StateEstimatorModel import StateEstimatorModel
from PPOPolicy import PPOPolicy
import socket

from utils import parse_RL_inference_output, sort_moteus_to_isaaclab, np_revs_to_radians, generate_session_filename, log_observations_and_actions

# INITIALIZATION

csv_filepath = generate_session_filename(base_directory="/home/orangepi/Documents/logs")

# standing position offsets used in isaaclab, in radians
JOINT_OFFSETS = np.array([0.0000,  0.0000,  0.0000,  0.0000,  0.5236, -0.5236, -0.5236,  0.5236, 0.8727, -0.8727, -0.8727,  0.8727])

# joint offsets except in the order expected of the data from moteus.
SORTED_JOINT_OFFSETS = np.array([0.0000, 0.5236, 0.8727, 0.0000, -0.5236, -0.8727, 0.0000, -0.5236, -0.8727, 0.0000, 0.5236, 0.8727])

# LCM setup
file_path = os.path.abspath(__file__)
directory_path = os.path.dirname(file_path)

ppo_policy = PPOPolicy(directory_path + '/rknn_models/ppo_policy.rknn')
state_estimator = StateEstimatorModel(directory_path + '/rknn_models/state_estimator.rknn')
imu = IMU()

lc_pc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
lc_pi = lcm.LCM("udpm://239.255.77.67:7667?ttl=1")

pc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pc_addr = ('10.42.0.199', 7668)

prev_action = (np.zeros(12)/(2*np.pi)).tolist()
velocity_command = [0, 0, 0]

# Shared state for latest observation
latest_state = None
state_lock = threading.Lock()

enabled = False 
enabled_lock = threading.Lock()

policy_on = False

# thanks chatgpt
# LCM state handler: this runs in a separate thread and updates the latest state
def handle_state(channel, data):
    global latest_state
    # Decode the incoming state message
    received_state = quad_state_t.decode(data)

    # Lock the shared state and update it
    with state_lock:
        latest_state = received_state

    publish_state(list(received_state.position), list(received_state.velocity), received_state.bus_voltage, received_state.fault_code)


# Function to send action via LCM
def send_command_via_lcm(action):
    command_msg = quad_command_t()
    command_msg.timestamp = time.time_ns()
    command_msg.position = action
    lc_pi.publish("COMMAND", command_msg.encode())

# Function to run the RL policy at a fixed rate using delta time
def run_policy_loop(frequency=200):
    global prev_action

    # Calculate the time step duration based on the desired frequency
    time_step = 1.0 / frequency
    iteration_count = 0
    frequency_check_time = time.time()  # Track the starting time for frequency calculation
    
    while True:        
        # Record the start time of this loop iteration
        loop_start_time = time.time()

        # --- Profiling: Time to get state ---
        state_start_time = time.time()
        
        # Get the latest state
        with state_lock:
            if latest_state is None:
                continue  # Skip if no state is available yet
            # Extract the most recent state
            received_state = latest_state

        state_elapsed_time = time.time() - state_start_time
        # print(f"Time to get state: {state_elapsed_time:.6f} s")

        # --- Profiling: IMU reading (asynchronously fetched) ---
        imu_start_time = time.time()

        # Get the most recent IMU data (non-blocking)
        with imu_lock:
            if imu_data is None:
                continue  # Skip if no state is available yet
            ang_vel, grav_proj = imu_data

        imu_elapsed_time = time.time() - imu_start_time
        # print(f"Time to read IMU: {imu_elapsed_time:.6f} s")

        # --- Profiling: Process RL inputs ---
        rl_input_start_time = time.time()

        # Process the state for RL input
        position_radians_rel = sort_moteus_to_isaaclab(np_revs_to_radians(np.array(received_state.position)) - SORTED_JOINT_OFFSETS) 
        velocity_radians = sort_moteus_to_isaaclab(np_revs_to_radians(np.array(received_state.velocity)))
        state_estimator_input = ang_vel + grav_proj + position_radians_rel + velocity_radians + prev_action
        state_estimator_input = np.array([state_estimator_input]).astype(np.float32)

        # Estimate base linear velocity
        base_lin_vel = state_estimator.compute_lin_vel([state_estimator_input])[0][0].tolist()

        # Prepare the observation for the RL policy
        observation = base_lin_vel + ang_vel + grav_proj + velocity_command + position_radians_rel + velocity_radians + prev_action
        observation = np.array([observation]).astype(np.float32)
        # print(f'pos {position_radians_rel}')
        rl_input_elapsed_time = time.time() - rl_input_start_time
        # print(f"Time to prepare RL inputs: {rl_input_elapsed_time:.6f} s")

        # --- Profiling: RL policy prediction ---
        rl_predict_start_time = time.time()
        
        # Use the policy to predict the next action

        inference_output = ppo_policy.predict([observation])
        # print(f'inference out: {inference_output}')
        # print(inference_output[0])
        action = parse_RL_inference_output(inference_output, JOINT_OFFSETS)
        
        rl_predict_elapsed_time = time.time() - rl_predict_start_time
        # print(f"Time for RL policy prediction: {rl_predict_elapsed_time:.6f} s")

        log_start_time = time.time()

        if (enabled):
            log_observations_and_actions(csv_filepath, observation.tolist()[0], inference_output)

        log_elapsed = time.time() - log_start_time

        # print(f"Time for log: {log_elapsed:.6f} s")

        # --- Profiling: Sending command ---
        send_command_start_time = time.time()

        # Send the computed action
        if policy_on == True:
            send_command_via_lcm(action)
        elif policy_on == False:
            # standstill when policy is toggled off
            send_command_via_lcm(parse_RL_inference_output(np.zeros(12).tolist(), JOINT_OFFSETS))
            # print('standby')

        send_command_elapsed_time = time.time() - send_command_start_time
        # print(f"Time to send command: {send_command_elapsed_time:.6f} s")

        # Update the previous action only if enabled, since actions aren't taken during disabled state
        with enabled_lock:
            if enabled == True and policy_on == True:
                prev_action = inference_output
            else:
                prev_action = np.zeros(12).tolist()

        # Calculate elapsed time and adjust sleep duration
        elapsed_time = time.time() - loop_start_time
        sleep_duration = max(0, time_step - elapsed_time)
        # print(f"Iteration time: {elapsed_time:.6f} s, Sleep duration: {sleep_duration:.6f} s")

        # Sleep for the remaining time to maintain the loop frequency
        time.sleep(sleep_duration)

        # Increment the iteration count and check frequency consistency
        iteration_count += 1
        current_time = time.time()
        if current_time - frequency_check_time >= 1.0:  # Check once every second
            actual_frequency = iteration_count / (current_time - frequency_check_time)
            print(f"Current frequency: {actual_frequency:.2f} Hz")

            # Reset for the next second
            iteration_count = 0
            frequency_check_time = current_time

def handle_velocity_command(channel, data):
    global velocity_command
    global policy_on
    
    velocity_command_msg = velocity_command_t.decode(data)
    velocity_command = [velocity_command_msg.lin_vel_x, velocity_command_msg.lin_vel_y, velocity_command_msg.ang_vel_z]

    policy_on = velocity_command_msg.policy_on

def forward_enable_data(channel, data):
    global enabled
    
    if data is None:
        return
    print("ENABLED" if enabled_t.decode(data).enabled else "DISABLED")
    enabled_data = enabled_t.decode(data)
    enabled = enabled_data.enabled
    lc_pi.publish("ENABLED", data)

def publish_state(position, velocity, bus_voltage, fault_code):
    state_c2d_msg = quad_state_t()
    state_c2d_msg.timestamp = time.time_ns()
    state_c2d_msg.position = position
    state_c2d_msg.velocity = velocity
    state_c2d_msg.bus_voltage = bus_voltage
    state_c2d_msg.fault_code = fault_code

    pc_socket.sendto(state_c2d_msg.encode(), pc_addr)

    # print('published to c2d')

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


# Subscribe to the LCM state message channel
lc_pi.subscribe("STATE_C2C", handle_state)
lc_pc.subscribe("VELOCITY_COMMAND", handle_velocity_command)
lc_pc.subscribe("ENABLED", forward_enable_data)

def handle_lc_pc():
    while True:
        lc_pc.handle()

def handle_lc_pi():
    while True:
        lc_pi.handle()

thread_pc = threading.Thread(target=handle_lc_pc)
thread_pi = threading.Thread(target=handle_lc_pi)
imu_thread = threading.Thread(target=read_imu_async)

imu_thread.start()
thread_pc.start()
thread_pi.start()

# Start the policy loop
def main():
    freq = 200
    print(f'Starting policy rollout at {freq}hz')
    run_policy_loop(frequency=freq)

if __name__ == "__main__":
    main()