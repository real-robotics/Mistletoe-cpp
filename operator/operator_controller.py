import pygame
import math
import lcm
import time

from exlcm import velocity_command_t

# TODO: max angular velocity in the z axis
MAX_ANG_VEL_Z = 1

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")    
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

        x_velocity = joystick.get_axis(1)  # X-axis of the first joystick
        y_velocity = joystick.get_axis(0)  # Y-axis of the first joystick
        ang_vel_z = -1 * joystick.get_axis(2)

        if (abs(x_velocity) < 0.01):
            x_velocity = 0
        if (abs(y_velocity) < 0.01):
            y_velocity = 0
        if (abs(ang_vel_z) < 0.01):
            ang_vel_z = 0

        # Print the results
        msg.timestamp = time.time_ns()
        msg.lin_vel_x = x_velocity
        msg.lin_vel_y = y_velocity
        msg.ang_vel_z = ang_vel_z
        print(f'x: {x_velocity}')
        print(f'y: {y_velocity}')
        print(f'ang_vel: {ang_vel_z}')
        # print(ang_vel_z)
        lc.publish("VELOCITY_COMMAND", msg.encode())

        pygame.time.wait(10)  # Wait for 10 milliseconds

except KeyboardInterrupt:
    pygame.quit()

