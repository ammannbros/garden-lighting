import time

import pigpio
from garden_lighting.MCP23017.MCP23017 import MCP23017


class RaspberryMCP23017(MCP23017):

    def __init__(self, dev_addr, rst_pin=0xFF, i2cport=1):
        super().__init__(dev_addr, rst_pin, i2cport)

    # def __del__(self):
    #     #needed to clear the RPi.GPIO channel
    #     self.io.cleanup(self.RstPin)

    def initDevice(self, pi):
        '''
        Does a reset to put all registers in initial state
        '''

        #Define the reset pin as output
        pi.set_mode(self.RstPin, pigpio.OUTPUT)
        #Create a reset impulse
        pi.write(self.RstPin, 0)
        #wait for 50 ms
        time.sleep(.050)
        pi.write(self.RstPin, 1)
