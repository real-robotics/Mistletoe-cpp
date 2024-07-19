import lcm
import time
import datetime
import random
from exlcm import data_t

def publish_data():
    lc = lcm.LCM()
    msg = data_t()

    while True:
        msg.timestamp = datetime.datetime.utcnow().isoformat()
        msg.position = random.random() * 100
        msg.voltage = random.random() * 5

        lc.publish("EXAMPLE", msg.encode())
        time.sleep(0.1)

if __name__ == "__main__":
    publish_data()
