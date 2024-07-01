import lcm
import time
import random
from your_lcm_types import example_t  # Replace with your actual LCM type

def send_lcm_messages():
    lc = lcm.LCM()
    msg = example_t()
    
    while True:
        # Update position and velocity
        msg.position = 10 * random.randint() # Example position value
        msg.velocity = 10 * random.randint()  # Example velocity value
        
        lc.publish("EXAMPLE_CHANNEL", msg.encode())
        print(f"Sent message: {msg}")
        time.sleep(1)  # Send message every second

if __name__ == "__main__":
    send_lcm_messages()