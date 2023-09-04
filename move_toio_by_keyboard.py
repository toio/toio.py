import asyncio
import sys
import termios
import tty

from toio import *

class ReadChar():

    def __enter__(self):

        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setraw(sys.stdin.fileno())
        return sys.stdin.read(1)

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

async def motor_1():
    # connect to a cube
    dev_list = await BLEScanner.scan(1)
    assert len(dev_list)
    cube = ToioCoreCube(dev_list[0].interface)
    await cube.connect()

    # go
    timeout = 10
    interval = 0.1
    import datetime
    s_time = current_time = datetime.datetime.now()
    while (datetime.datetime.now() - s_time).seconds < timeout:
        with ReadChar() as rc:
            char = rc
        if char == 'w':
            print('w')
            await cube.api.motor.motor_control(30, 30)
            await asyncio.sleep(interval)
        elif char == 'a':
            print('a')
            await cube.api.motor.motor_control(-10, 10)
            await asyncio.sleep(interval)
        elif char == 'd':
            print('d')
            await cube.api.motor.motor_control(10, -10)
            await asyncio.sleep(interval)
        elif char == 'x':
            print('x')
            await cube.api.motor.motor_control(-30, -30)
            await asyncio.sleep(interval)
        elif char == 's':
            print('s')
            await cube.api.motor.motor_control(0, 0)
        if char in "^C":
            print('finish!')
            break


    # await cube.api.motor.motor_control(30, 30)
    # await asyncio.sleep(2)

    # stop
    await cube.api.motor.motor_control(0, 0)

    await cube.disconnect()
    return 0

if __name__ == "__main__":
    asyncio.run(motor_1())