import lcm
from exlcm import velocity_command_t

class VelocityCommandSubscriber(object):
    def __init__(self):
        self.lcm = lcm.LCM("udpm://239.255.76.68:7667?ttl=2")
        self.lcm.subscribe("VELOCITY_COMMAND", self.handle_message)

    def handle_message(self, channel, data):
        print(data)
        msg = velocity_command_t.decode(data)
        print(f"Received message on channel {channel}")
        print(f"Timestamp: {msg.timestamp}")
        print(f"Linear Velocity X: {msg.lin_vel_x}")
        print(f"Linear Velocity Y: {msg.lin_vel_y}")
        print(f"Angular Velocity Z: {msg.ang_vel_z}")
        print()

    def run(self):
        try:
            while True:
                self.lcm.handle()
        except KeyboardInterrupt:
            print("Subscriber interrupted by user")

if __name__ == "__main__":
    subscriber = VelocityCommandSubscriber()
    subscriber.run()
