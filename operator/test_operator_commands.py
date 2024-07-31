import lcm
from exlcm import velocity_command_t

class VelocityCommandSubscriber():
    def __init__(self):
        super().__init__()

    def on_message(self, channel, data):
        # Decode the message
        msg = velocity_command_t.decode(data)
        
        # Print the output
        print(f"Timestamp: {msg.timestamp}")
        print(f"Linear Velocity X: {msg.lin_vel_x}")
        print(f"Linear Velocity Y: {msg.lin_vel_y}")
        print(f"Angular Vel Z: {msg.ang_vel_z}")

if __name__ == "__main__":
    # Create an LCM instance
    lc = lcm.LCM()

    # Create a subscriber for the VELOCITY_COMMAND channel
    subscriber = VelocityCommandSubscriber()
    lc.subscribe("VELOCITY_COMMAND", subscriber.on_message)

    print("Listening for VELOCITY_COMMAND messages...")
    
    # Start the LCM event loop
    try:
        while True:
            lc.handle()
    except KeyboardInterrupt:
        print("Subscriber stopped.")
