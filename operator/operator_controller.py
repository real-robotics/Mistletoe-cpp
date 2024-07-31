import pygame
import math
import lcm
import time

from exlcm import velocity_command_t

# TODO: max angular velocity in the z axis
MAX_ANG_VEL_Z = 1

lc = lcm.LCM()
msg = velocity_command_t()

# Initialize Pygame
pygame.init()

# Initialize the joystick
pygame.joystick.init()

# Check if any joysticks are connected
if pygame.joystick.get_count() == 0:
    print("No joystick connected.")
    pygame.quit()
    exit()

# Initialize the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Function to get direction in radians from the joystick axes
def get_direction_in_radians(x, y):
    return math.atan2(y, x)

# Variable to store the last non-zero direction in radians
last_direction_radians = 0

# joystick threshold
threshold = 0.05

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Get joystick values
        x_velocity = joystick.get_axis(0)  # X-axis of the first joystick
        y_velocity = joystick.get_axis(1)  # Y-axis of the first joystick

        ang_vel_z = joystick.get_axis(2) * MAX_ANG_VEL_Z

        # Print the results
        msg.timestamp = time.time_ns()
        msg.lin_vel_x = x_velocity
        msg.lin_vel_y = y_velocity
        msg.ang_vel_z = ang_vel_z
        print(y_velocity)
        # print(ang_vel_z)
        lc.publish("VELOCITY_COMMAND", msg.encode())

        pygame.time.wait(100)  # Wait for 100 milliseconds

except KeyboardInterrupt:
    pygame.quit()

