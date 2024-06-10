import lcm
import time
from exlcm import quad_command_t

lc = lcm.LCM()

msg = quad_command_t()
msg.timestamp = time.time_ns()
msg.position = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

lc.publish("COMMAND", msg.encode())
