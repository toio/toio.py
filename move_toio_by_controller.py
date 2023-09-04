import asyncio

import os
import pprint
import pygame

from toio import *

import time


if __name__ == "__main__":
    # ps4 = PS4Controller()
    # ps4.init()
    # ps4.listen()

    # ref: https://gist.github.com/claymcleod/028386b860b75e4f5472
    pygame.init()
    pygame.joystick.init()
    controller = pygame.joystick.Joystick(0)
    controller.init()

    axis_data = {}

    button_data = {}
    for i in range(controller.get_numbuttons()):
        button_data[i] = False

    hat_data = {}
    for i in range(controller.get_numhats()):
        hat_data[i] = (0, 0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                axis_data[event.axis] = round(event.value,2)
            elif event.type == pygame.JOYBUTTONDOWN:
                button_data[event.button] = True
            elif event.type == pygame.JOYBUTTONUP:
                button_data[event.button] = False
            elif event.type == pygame.JOYHATMOTION:
                hat_data[event.hat] = event.value

            # Insert your code on what you would like to happen for each event here!
            # In the current setup, I have the state simply printing out to the screen.
            
            os.system('clear')
            # pprint.pprint(button_data)
            pprint.pprint(axis_data)
            if axis_data:
                l_val, r_val = 0, 0
                if 1 in axis_data and abs(axis_data[1]) >= 0.1:
                    l_val = - axis_data[1]
                if 3 in axis_data and abs(axis_data[3]) >= 0.1:
                    r_val = - axis_data[3]
                print(l_val, r_val)
            # pprint.pprint(hat_data)
            time.sleep(0.05)
