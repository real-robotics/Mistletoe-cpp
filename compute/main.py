import lcm
import time
from exlcm import quad_command_t, quad_state_t, velocity_command_t
import threading
import numpy as np 

from .BNO055 import BNO055
from .VelocityTrackingModel import VelocityTrackingModel
from.StateEstimatorModel import StateEstimatorModel

# TODO: put real paths to the models 
velocity_tracking_model = VelocityTrackingModel("/home/easternspork/Test-RKNN_Model/what_the_sigma.rknn")
state_estimator = StateEstimatorModel()
imu = BNO055()

lc = lcm.LCM()

# observation items size of 48
# base_lin_vel, base_ang_vel, projected_gravity, velocity command of size 3
# joint pos,vel,action of size 12

observation_list = []

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

def handle_velocity_command(channel, data):
    msg = velocity_command_t.decode(data)
    robot_state["velocity_command"] = [msg.lin_vel_x, msg.lin_vel_y, msg.heading]
    
lc.subscribe("STATE", handle_state)
lc.subscribe("VELOCITY_COMMAND", handle_velocity_command)

def handle_lcm():
    while True:
        # technically the values get queried sequentially so some values could be more updated than others but whatever I guess
        robot_state["base_ang_vel"] = imu.get_ang_vel
        robot_state["projected_gravity"] = imu.get_projected_gravity

        lc.handle()

        #TODO: what happens when the previous action is none ie. when the robot gets initialzied?
        # also this is kind of disgusting
        state_estimator_input = robot_state["base_ang_vel"] + robot_state["projected_gravity"] + robot_state["velocity_command"] + robot_state["joint_pos"] + robot_state["joint_vel"] + robot_state["prev_action"]

        robot_state["base_lin_vel"] = state_estimator.compute_lin_vel(state_estimator_input)
        

handler_thread = threading.Thread(target=handle_lcm)
handler_thread.start()

try:
    while True:
        msg = quad_command_t()
        msg.timestamp = time.time_ns()
        msg.position = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        model_output = velocity_tracking_model.compute_inference()

        lc.publish("COMMAND", msg.encode())

        time.sleep(0.1)

except KeyboardInterrupt:
    handler_thread.join()
