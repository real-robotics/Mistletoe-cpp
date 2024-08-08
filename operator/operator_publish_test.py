import lcm
from exlcm import velocity_command_t
import time

def main():
    # Create an LCM instance
    lcm_instance = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

    # Create a message with all values set to zero
    msg = velocity_command_t()
    msg.timestamp = time.time_ns()
    msg.lin_vel_x = 0.0
    msg.lin_vel_y = 0.0
    msg.ang_vel_z = 0.0

    # Publish the message on the VELOCITY_COMMAND channel
    while True:
        print(msg.encode())
        lcm_instance.publish("VELOCITY_COMMAND", msg.encode())
        print("Published operator message.")
        time.sleep(1)  # Publish every second

if __name__ == "__main__":
    main()
