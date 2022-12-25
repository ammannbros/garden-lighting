import time
import os
from garden_lighting.MCP23017.MCP23017 import MCP23017

GPIO_ROOT = '/sys/class/gpio'

class RaspberryMCP23017(MCP23017):
    def __init__(self, dev_addr, rst_pin=0xFF, i2cport=1):
        super().__init__(dev_addr, rst_pin, i2cport)

    def initDevice(self):
        '''
        Does a reset to put all registers in initial state
        '''

        self.initRstPin()
        # Create a reset impulse
        self.digitalWrite(False)
        # wait for 50 ms
        time.sleep(.050)
        self.digitalWrite(True)

    def initRstPin(self):
        if os.path.exists(os.path.join(GPIO_ROOT, f"gpio{self.RstPin}")):
            self.deinitRstPin()

        with open(os.path.join(GPIO_ROOT, "export"), 'w') as f:
            f.write(str(self.RstPin))
            f.flush()

        # Define the reset pin as output
        with open(os.path.join(GPIO_ROOT, f"gpio{self.RstPin}", 'direction'), 'w') as f:
            f.write(str('out'))
            f.flush()

    def deinitRstPin(self):
        with open(os.path.join(GPIO_ROOT, "unexport"), 'w') as f:
            f.write(str(self.RstPin))
            f.flush()

    def digitalWrite(self, high):
        with open(os.path.join(GPIO_ROOT, f"gpio{self.RstPin}", "value"), 'w') as f:
            f.write('1' if high else '0')
            f.flush()
