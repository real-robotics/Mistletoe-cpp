import lcm
import time
from exlcm import quad_command_t, quad_state_t
import threading

lc = lcm.LCM()

def handle_lcm():
    while True:
        lc.handle()

handler_thread = threading.Thread(target=handle_lcm)
handler_thread.start()

def handle_state(channel, data):
    msg = quad_state_t.decode(data)
    print(f'Message received on channel: {channel}')
    print(f'Timestamp: {msg.timestamp}')
    print(f'Position: {msg.position}')
    print(f'Velocity: {msg.velocity}')

lc.subscribe("STATE", handle_state)

try:
    while True:
        msg = quad_command_t()
        msg.timestamp = time.time_ns()
        msg.position = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        lc.publish("COMMAND", msg.encode())

        time.sleep(0.1)
except KeyboardInterrupt:
    handler_thread.join()
