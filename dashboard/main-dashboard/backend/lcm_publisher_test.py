import lcm
import time
from datetime import datetime
import random
from exlcm import quad_state_t, velocity_command_t

def publish_data():
    lc = lcm.LCM(
        # "udpm://239.255.76.67:7667?ttl=1"
        )
    msg = quad_state_t()
    velocity_command = velocity_command_t()

    while True:
        msg.timestamp = int(time.time() * 1e6)
        msg.position = [-0.185 for _ in range(12)]
        msg.velocity = [random.random() * 5 for _ in range(12)]
        msg.bus_voltage = 22
        msg.fault_code = 0

        velocity_command.lin_vel_x = random.random()
        velocity_command.lin_vel_y = random.random()
        velocity_command.heading = random.random()

        lc.publish("STATE_C2D", msg.encode())
        lc.publish("VELOCITY_COMMAND", velocity_command.encode())
        # print('dd')
        time.sleep(0.1)

if __name__ == "__main__":
    publish_data()
