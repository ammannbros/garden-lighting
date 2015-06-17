import time
import os
import wiringpi2
from garden_lighting.MCP23017.MCP23017 import MCP23017


class RaspberryMCP23017(MCP23017):
    def __init__(self, dev_addr, rst_pin=0xFF, i2cport=1):
        super().__init__(dev_addr, rst_pin, i2cport)

    def initDevice(self):
        '''
        Does a reset to put all registers in initial state
        '''

        os.system("gpio export " + str(self.RstPin) + " out")
        # Set pin numbering mode
        #  We don't need performance, don't want root and don't want to interfere with
        #  other wiringpi instances -> sysfs
        wiringpi2.wiringPiSetupSys()

        # Define the reset pin as output
        wiringpi2.pinMode(self.RstPin, wiringpi2.GPIO.OUTPUT)
        # Create a reset impulse
        wiringpi2.digitalWrite(self.RstPin, wiringpi2.GPIO.LOW)
        # wait for 50 ms
        time.sleep(.050)
        wiringpi2.digitalWrite(self.RstPin, wiringpi2.GPIO.HIGH)
