import lcm
import time
from exlcm import quad_command_t, quad_state_t, velocity_command_t
import threading
import numpy as np 

from .BNO055 import BNO055
from .StateEstimatorModel import StateEstimatorModel
from .PPOActorModel import PPOActorModel

# TODO: put real paths to the models 
ppo_actor_model = PPOActorModel("/home/easternspork/Test-RKNN_Model/what_the_sigma.rknn")
state_estimator = StateEstimatorModel("/home/easternspork/Test-RKNN_Model/what_the_sigma.rknn")
imu = BNO055()

lc = lcm.LCM()

target_joint_pos = []

# observation items size of 48
# base_lin_vel, base_ang_vel, projected_gravity, velocity command of size 3
# joint pos,vel,action of size 12

robot_state = {
    "base_lin_vel": [],
    "base_ang_vel": [],
    "projected_gravity": [],
    "velocity_command" : [],
    "joint_pos": [],
    "joint_vel": [],
    "prev_action": []
}

# initailze to zeros, don't know how good this actually is
prev_action = np.zeros(12)

def handle_state(channel, data):
    msg = quad_state_t.decode(data)
    robot_state["joint_pos"] = msg.position
    robot_state["joint_vel"] = msg.velocity
    # TODO: actually make this real
    robot_state["prev_action"] = msg.prev_action

    # technically the values get queried sequentially so some values could be more updated than others but whatever I guess
    robot_state["base_ang_vel"] = imu.get_ang_vel()
    robot_state["projected_gravity"] = imu.get_projected_gravity()

    #TODO: what happens when the previous action is none ie. when the robot gets initialzied?
    # also this is kind of disgusting
    state_estimator_input = robot_state["base_ang_vel"] + robot_state["projected_gravity"] + robot_state["velocity_command"] + robot_state["joint_pos"] + robot_state["joint_vel"] + robot_state["prev_action"]

    robot_state["base_lin_vel"] = state_estimator.compute_lin_vel(state_estimator_input)

def handle_velocity_command(channel, data):
    velocity_command = velocity_command_t.decode(data)
    robot_state["velocity_command"] = [velocity_command.lin_vel_x, velocity_command.lin_vel_y, velocity_command.heading]
    # TODO: double check if matches observation space of RL
    observation = robot_state["base_lin_vel"] + robot_state["base_ang_vel"] + robot_state["projected_gravity"] + robot_state["velocity_command"] + robot_state["joint_pos"] + robot_state["joint_vel"] + robot_state["prev_action"]
    # scope might be weird (?)
    target_joint_pos = ppo_actor_model.compute_joint_pos()

# I am somewhat worried that these two will have a large enough time gap between that it woul mess up the sim to real transfer (we assume these infos come at the same time in sim) but maybe not 
lc.subscribe("STATE_C2C", handle_state)
lc.subscribe("VELOCITY_COMMAND", handle_velocity_command)

def handle_lcm():
    while True:
        lc.handle()

handler_thread = threading.Thread(target=handle_lcm)
handler_thread.start()

try:
    while True:
        command_msg = quad_command_t()
        command_msg.timestamp = time.time_ns()
        command_msg.position = target_joint_pos

        state_c2d_msg = quad_state_t()
        state_c2d_msg.timestamp = time.time_ns()
        state_c2d_msg.position = robot_state["joint_pos"]
        state_c2d_msg.velocity = robot_state["joint_vel"]

        lc.publish("COMMAND", command_msg.encode())
        lc.publish("STATE_C2D", state_c2d_msg.encode())

        time.sleep(0.1)

except KeyboardInterrupt:
    handler_thread.join()
