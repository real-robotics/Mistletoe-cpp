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

from utils import parse_RL_inference_output, sort_moteus_to_isaaclab, np_revs_to_radians

# INITIALIZATION

# standing position offsets used in isaaclab, in radians
JOINT_OFFSETS = np.array([0.0000,  0.0000,  0.0000,  0.0000,  0.5236, -0.5236, -0.5236,  0.5236, 0.8727, -0.8727, -0.8727,  0.8727])

# joint offsets except in the order expected of the data from moteus.
SORTED_JOINT_OFFSETS = np.array([0.0000, 0.5236, 0.8727, 0.0000, -0.5236, -0.8727, 0.0000, -0.5236, -0.8727, 0.0000, 0.5236, 0.8727])

# LCM setup
lc_pi = lcm.LCM("udpm://239.255.77.67:7667?ttl=1")
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
velocity_command = [0,0,0]

# thanks chatgpt

# Create a global condition variable and store action and state
condition = threading.Condition()
latest_state = None
expected_action_id = 0  # Keep track of the last action sent

# Callback to handle incoming LCM state message
# action ids are kept track of to match the action-state pair, so that states being passed as observations are states observed right when the action is sent.
# its mostly a safety feature that may not actually matter a whole lot, depending on the implentation details of LCM itself, but who knows (?)

def state_handler(channel, data):
    global latest_state
    # Parse the incoming data to get the new state and its action_id
    received_state = quad_state_t.decode(data)  # Parsing logic for state
    received_action_id = received_state['action_id']
    
    # Check if the received state corresponds to the last action sent
    with condition:
        if received_action_id == expected_action_id:
            latest_state = received_state
            condition.notify()  # Notify that the correct state has been received

# Blocking function to wait for LCM state with action_id check and timeout
def wait_for_lcm_state(timeout=1.0):
    global latest_state
    with condition:
        start_time = time()
        while latest_state is None:
            if timeout:
                elapsed_time = time() - start_time
                if elapsed_time >= timeout:
                    raise TimeoutError("State reception timed out")
                condition.wait(timeout - elapsed_time)
            else:
                condition.wait()
        print(f'relay time: {time() - start_time}')
        # Once state is received, return it
        state_to_return = latest_state
        latest_state = None  # Clear the state to wait for the next one
        return state_to_return

# Function to send action via LCM with a unique action_id
# action is a 1D array of length 12 
def send_command_via_lcm(action, action_id):
    # Add action_id to the action message before sending
    command_msg = quad_command_t()
    command_msg.timestamp = time.time_ns()
    command_msg.position = action

    # TODO redefine LCM
    command_msg.action_id = action_id
    lc_pi.publish("COMMAND", command_msg.encode())  # Encode and send the action

# Step function - action is a 1D array of length 12 
# takes an action, gets the observation for when the action is taken, and then returns that obs
def step(action):
    global expected_action_id
    expected_action_id += 1  # Increment action_id for the next action
    
    # Send the command via LCM with the current action_id
    send_command_via_lcm(action, expected_action_id)
    
    # Wait for the state update with the correct action_id
    try:
        new_state = wait_for_lcm_state(timeout=1.0)  # Adjust timeout as needed
    except TimeoutError:
        print("State update timed out")
        return None  # Handle timeout case

    ang_vel = imu.get_ang_vel()
    grav_proj = imu.get_projected_gravity()

    # state published to the dashboard
    publish_state(list(new_state.position), list(new_state.velocity), new_state.bus_voltage, new_state.fault_code)

    # offsets are subtracted because mdp.joint_pos_rel is used in the RL policy training (meaning default offsets are subtracted during training for obs space)
    # use sort to moteus_to_isaaclab function because this is getting inputted as obs for policy trained on isaaclab.
    position_radians_rel = sort_moteus_to_isaaclab((np_revs_to_radians(np.array(list(new_state.position))) - SORTED_JOINT_OFFSETS).tolist())
    velocity_radians_rel = sort_moteus_to_isaaclab((np_revs_to_radians(np.array(list(new_state.velocity)))).tolist())

    state_estimator_input = ang_vel + grav_proj + velocity_command + position_radians_rel + velocity_radians_rel + prev_action
    # convert into format required for model
    state_estimator_input = np.array([state_estimator_input]).astype(np.float32)

    base_lin_vel = state_estimator.compute_lin_vel([state_estimator_input])[0][0].tolist()

    observation = base_lin_vel + ang_vel + grav_proj + velocity_command + position_radians_rel + velocity_radians_rel + prev_action
    # convert into format required for model
    observation = [np.array([observation]).astype(np.float32)]
    
    # set prev action after action has taken place and state is observed
    prev_action = action

    return observation

def observe_state(timeout=1.0):
    """
    Observe the latest state without taking any action.
    This function waits for the latest state from LCM.
    """
    try:
        # Wait for the state update with a timeout
        new_state = wait_for_lcm_state(timeout=timeout)
    except TimeoutError:
        print("State observation timed out")
        return None  # Handle timeout case
    
    # state published to the dashboard
    publish_state(list(new_state.position), list(new_state.velocity), new_state.bus_voltage, new_state.fault_code)

    # offsets are subtracted because mdp.joint_pos_rel is used in the RL policy training (meaning default offsets are subtracted during training for obs space)
    # use sort to moteus_to_isaaclab function because this is getting inputted as obs for policy trained on isaaclab.
    position_radians_rel = sort_moteus_to_isaaclab((np_revs_to_radians(np.array(list(new_state.position))) - SORTED_JOINT_OFFSETS).tolist())
    velocity_radians_rel = sort_moteus_to_isaaclab((np_revs_to_radians(np.array(list(new_state.velocity)))).tolist())

    state_estimator_input = imu.get_ang_vel() + imu.get_projected_gravity() + velocity_command + position_radians_rel + velocity_radians_rel + prev_action
    # convert into format required for model
    state_estimator_input = np.array([state_estimator_input]).astype(np.float32)

    base_lin_vel = state_estimator.compute_lin_vel([state_estimator_input])[0][0].tolist()

    observation = base_lin_vel + imu.get_ang_vel() + imu.get_projected_gravity() + velocity_command + position_radians_rel + velocity_radians_rel + prev_action
    # convert into format required for model
    observation = [np.array([observation]).astype(np.float32)]

    return observation

def handle_velocity_command(channel, data):
    global velocity_command

    velocity_command_msg = velocity_command_t.decode(data)
    velocity_command = [velocity_command_msg.lin_vel_x, velocity_command_msg.lin_vel_y, velocity_command_msg.ang_vel_z]

def forward_enable_data(channel, data):
    if data is None:
        return
    print("ENABLED" if enabled_t.decode(data).enabled else "DISABLED")
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

# Subscribe to the LCM state message channel
lc_pi.subscribe("STATE_C2C", state_handler)
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

thread_pc.start()
thread_pi.start()

# Main function for policy rollout IRL
def main():
    obs = observe_state()

    print("Initialized Robot")

    while True:
        action = parse_RL_inference_output(ppo_policy.predict(obs))
        print(action)
        obs = step(action)
        print(obs)  

if __name__ == "__main__":
    main()