import lcm
import time
from datetime import datetime
import random
from exlcm import quad_state_t

def publish_data():
    lc = lcm.LCM()
    msg = quad_state_t()

    while True:
        msg.timestamp = int(time.time() * 1e6)
        msg.position = [random.random() * 5 for _ in range(12)]
        msg.velocity = [random.random() * 5 for _ in range(12)]
        msg.bus_voltage = random.random() * 5
        msg.fault_code = 1
        lc.publish("STATE_C2D", msg.encode())
        time.sleep(0.1)

if __name__ == "__main__":
    publish_data()
