import lcm
from exlcm import quad_state_t

class QuadStateSubscriber(object):
    def __init__(self):
        self.lcm = lcm.LCM("udpm://239.255.76.68:7667?ttl=1")
        self.lcm.subscribe("STATE_C2D", self.handle_message)

    def handle_message(self, channel, data):
        msg = quad_state_t.quad_state_t.decode(data)
        print(f"Received message on channel {channel}")
        print(f"Timestamp: {msg.timestamp}")
        print(f"Bus Voltage: {msg.bus_voltage}")
        print(f"Fault Code: {msg.fault_code}")
        print("Position:", " ".join(map(str, msg.position)))
        print("Velocity:", " ".join(map(str, msg.velocity)))
        print()

    def run(self):
        print("Starting LCM")
        try:
            while True:
                self.lcm.handle()
        except KeyboardInterrupt:
            print("Subscriber interrupted by user")

if __name__ == "__main__":
    subscriber = QuadStateSubscriber()
    subscriber.run()
