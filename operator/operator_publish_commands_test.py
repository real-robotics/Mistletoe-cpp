import lcm
from exlcm import quad_command_t
import time

def main():
    # Create an LCM instance
    lcm_instance = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

    # Create a message with all values set to zero
    msg = quad_command_t()
    msg.timestamp = time.time_ns()
    msg.position = [0,0,0,0,0,0,0,0,0,0,0,0]
    msg.manual_command = True

    # Publish the message on the VELOCITY_COMMAND channel
    while True:
        print(msg.encode())
        lcm_instance.publish("COMMAND", msg.encode())
        print("Published operator message.")
        time.sleep(1)  # Publish every second

if __name__ == "__main__":
    main()
