
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

lc_pi = lcm.LCM("udpm://239.255.77.67:7667?ttl=1")

def send_command_via_lcm(action):
    command_msg = quad_command_t()
    command_msg.timestamp = time.time_ns()
    command_msg.position = action
    lc_pi.publish("COMMAND", command_msg.encode())

def forward_enable_data(channel, data):
    global enabled
    
    if data is None:
        return
    print("ENABLED" if enabled_t.decode(data).enabled else "DISABLED")
    enabled_data = enabled_t.decode(data)
    enabled = enabled_data.enabled
    lc_pi.publish("ENABLED", data)

while True:
    send_command_via_lcm(np.zeros(12).tolist())
    time.sleep(0.05)