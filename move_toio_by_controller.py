import asyncio

import os
import pprint
import pygame

from toio import *

import time


async def motor_1():
    # connect to a cube
    dev_list = await BLEScanner.scan(1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()

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

    # go
    timeout = 20
    interval = 0.05
    import datetime
    s_time = current_time = datetime.datetime.now()
    while (datetime.datetime.now() - s_time).seconds < timeout:

        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                axis_data[event.axis] = round(event.value,2)
            elif event.type == pygame.JOYBUTTONDOWN:
                button_data[event.button] = True
            elif event.type == pygame.JOYBUTTONUP:
                button_data[event.button] = False
            elif event.type == pygame.JOYHATMOTION:
                hat_data[event.hat] = event.value
            
            os.system('clear')
            pprint.pprint(axis_data)
            if axis_data:
                l_val, r_val = 0, 0
                if 1 in axis_data and abs(axis_data[1]) >= 0.1:
                    l_val = - axis_data[1]
                if 3 in axis_data and abs(axis_data[3]) >= 0.1:
                    r_val = - axis_data[3]
                print(l_val, r_val)
                await cube.api.motor.motor_control(int(r_val*20), int(l_val*20))
                await asyncio.sleep(interval)

    # stop
    print('timeout!')
    await cube.api.motor.motor_control(0, 0)

    await cube.disconnect()
    return 0


if __name__ == "__main__":
    asyncio.run(motor_1())