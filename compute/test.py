import lcm
import exlcm

class QuadStateSubscriber:
    def __init__(self):
        self.lcm = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
        self.lcm.subscribe("STATE_C2C", self.handle_message)

    def handle_message(self, channel, data):
        msg = exlcm.quad_state_t.decode(data)
        
        print(f"Received message on channel: {channel}")
        print(f"Timestamp: {msg.timestamp}")
        
        print("Positions: ", end="")
        for i in range(12):
            print(msg.position[i], end=" ")
        print()
        
        print("Velocities: ", end="")
        for i in range(12):
            print(msg.velocity[i], end=" ")
        print()
        
        print(f"Bus Voltage: {msg.bus_voltage}")
        print(f"Fault Code: {msg.fault_code}")

    def run(self):
        print("Subscriber is running...")
        try:
            while True:
                self.lcm.handle()
        except KeyboardInterrupt:
            print("Subscriber interrupted and exiting...")

if __name__ == "__main__":
    subscriber = QuadStateSubscriber()
    subscriber.run()
