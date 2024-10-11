import numpy as np
import csv
import os
from datetime import datetime

# --- Utility Functions ---

def parse_RL_inference_output(inference_output, joint_offsets):
    """
    Parses the raw inference output from the RL model, scales it, converts to radians, and reorders the array for moteus.
    
    The input from isaaclab is scaled by 0.25, then converted to radians, and finally sorted to the order
    required by the moteus system (i.e., reordered with appropriate joint offsets).

    Args:
        inference_output (list): The output from the RL policy. a list of shape (12,).
        joint_offsets (numpy array): Joint offsets in radians, of shape (12,).

    Returns:
        list: A sorted list of joint positions after applying the scaling and joint offsets.
    """
    scaled_output = np.array(inference_output) * 0.25
    offset_output = (scaled_output + joint_offsets) / (2 * np.pi)
    
    sorted_output = []
    for i in range(4):
        for j in range(12):
            if j % 4 == i:
                sorted_output.append(offset_output[j])

    return sorted_output


def sort_isaaclab_to_moteus(arr):
    sorted_output = []
    for i in range(4):
        for j in range(12):
            if j % 4 == i:
                sorted_output.append(arr[j])

    return sorted_output

def sort_moteus_to_isaaclab(arr):
    """
    Reorders an array from the moteus system format (e.g., 11, 12, 13, 21, 22, ...) to the isaaclab format
    (e.g., 11, 21, 31, 41, 12, 22, ...) without any scaling or joint offsets.

    Args:
        arr (list or numpy array): Input array of joint positions or velocities, length must be divisible by 3.

    Returns:
        list: Reordered array where values are grouped by index % 3.
    
    Raises:
        ValueError: If the input array length is not divisible by 3.
    """
    if len(arr) % 3 != 0:
        raise ValueError("The length of the array must be divisible by 3")
    
    grouped = [[], [], []]
    for idx, value in enumerate(arr):
        grouped[idx % 3].append(value)

    return grouped[0] + grouped[1] + grouped[2]


def np_revs_to_radians(position_revs_arr):
    """
    Converts joint positions from revolutions to radians.

    Args:
        position_revs_arr (numpy array): Joint positions in revolutions.

    Returns:
        numpy array: Joint positions converted to radians.
    """
    return position_revs_arr * 2 * np.pi


# --- CSV Logging Functions ---

def generate_session_filename(base_directory="logs", prefix="session_log"):
    """
    Generates a unique filename for the session based on the current timestamp.
    
    Args:
        base_directory (str): The base directory where the CSV file will be saved.
        prefix (str): The prefix for the filename.
    
    Returns:
        str: A unique file path for the session CSV file.
    """
    # Generate a unique filename based on the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.csv"
    filepath = os.path.join(base_directory, filename)

    # Ensure the directory exists
    os.makedirs(base_directory, exist_ok=True)

    return filepath

def log_observations_and_actions(filepath, observations, actions):
    """
    Logs observations, previous actions, and current actions to a CSV file.

    Each row in the CSV will contain the observations (typically of length 48),
    followed by the previous actions (12), and the current actions (12).

    Args:
        filepath (str): The path to the CSV file where data will be logged.
        observations (list): The list of observations at the current timestep (typically length 48).
        actions (list): The list of current actions at the current timestep (typically length 12).
    """
    # Ensure the directory exists, if not, create it
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Define the CSV headers: Observations first, then joint_action
    headers = [
        'base_lin_vel_x', 'base_lin_vel_y', 'base_lin_vel_z',
        'base_ang_vel_x', 'base_ang_vel_y', 'base_ang_vel_z',
        'projected_gravity_x', 'projected_gravity_y', 'projected_gravity_z',
        'velocity_command_x', 'velocity_command_y', 'velocity_command_z',
        *[f'joint_pos_{i+1}' for i in range(12)],  # Joint positions
        *[f'joint_vel_{i+1}' for i in range(12)],  # Joint velocities
        *[f'joint_action_prev_{i+1}' for i in range(12)],  # Previous joint actions
        *[f'joint_action_{i+1}' for i in range(12)]  # Current joint actions
    ]

    # Check if the file already exists
    file_exists = os.path.isfile(filepath)

    # Write or append to the CSV file
    with open(filepath, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # If the file doesn't exist, write the header first
        if not file_exists:
            writer.writerow(headers)

        # Combine observations, previous actions, and current actions into a single row and write to the CSV
        row = observations + actions
        writer.writerow(row)

if __name__ == "__main__":


    # standing position offsets used in isaaclab, in radians
    JOINT_OFFSETS = np.array([0.0000,  0.0000,  0.0000,  0.0000,  0.5236, -0.5236, -0.5236,  0.5236, 0.8727, -0.8727, -0.8727,  0.8727])

    # joint offsets except in the order expected of the data from moteus.
    # SORTED_JOINT_OFFSETS = np.array([0.0000, 0.5236, 0.8727, 0.0000, -0.5236, -0.8727, 0.0000, -0.5236, -0.8727, 0.0000, 0.5236, 0.8727])
    
    moteus_position = np.array(sort_isaaclab_to_moteus([0.,0.,0.,0.,0.08333,-0.08333,-0.08333,0.08333,0.13891,-0.13891,-0.13891,0.13891]))
    # print(moteus_position)

    print(f'radian defaults {sort_moteus_to_isaaclab(np_revs_to_radians(moteus_position))}')

    # position_radians_rel = sort_moteus_to_isaaclab(np_revs_to_radians(moteus_position) - SORTED_JOINT_OFFSETS) 
    # position_radians_rel_different = sort_moteus_to_isaaclab(np_revs_to_radians(moteus_position)) - JOINT_OFFSETS
    # velocity_radians_rel = sort_moteus_to_isaaclab(np_revs_to_radians(np.array(np.zeros(12))))

    # print(position_radians_rel)
    # print(position_radians_rel_different)
    # print(velocity_radians_rel)
    # print(parse_RL_inference_output((-4 * JOINT_OFFSETS).tolist(), JOINT_OFFSETS))
    # print(sort_moteus_to_isaaclab([11,12,13,21,22,23,31,32,33,41,42,43]))
    # print(np_revs_to_radians(np.array([1,0.5])))
    