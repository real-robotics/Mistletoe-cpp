import pygame
import math
import lcm
import time

from exlcm import velocity_command_t

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
threshold = 0.1

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Get joystick values
        x_velocity = joystick.get_axis(0)  # X-axis of the first joystick
        y_velocity = joystick.get_axis(1)  # Y-axis of the first joystick

        x_heading = joystick.get_axis(2)  # X-axis of the second joystick
        y_heading = joystick.get_axis(3)  # Y-axis of the second joystick

        # Calculate direction in radians
        if x_heading > threshold or y_heading > threshold:
            direction_radians = get_direction_in_radians(x_heading, y_heading)
            last_direction_radians = direction_radians
        else:
            direction_radians = last_direction_radians

        # Print the results
        msg.timestamp = time.time_ns()
        msg.x_velocity = x_velocity
        msg.y_velocity = y_velocity
        msg.heading = direction_radians
        lc.publish("VELOCITY_COMMAND", msg.encode())

        pygame.time.wait(100)  # Wait for 100 milliseconds

except KeyboardInterrupt:
    pygame.quit()

