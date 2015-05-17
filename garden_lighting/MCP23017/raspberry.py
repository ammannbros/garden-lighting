
import time
from garden_lighting.MCP23017.MCP23017 import MCP23017

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Maybe you are not root?")


class RaspberryMCP23017(MCP23017):

    def __init__(self, dev_addr, rst_pin=0xFF, i2cport=1):
        super().__init__(dev_addr, rst_pin, i2cport)

    def __del__(self):
        #needed to clear the RPi.GPIO channel
        GPIO.cleanup(self.RstPin)

    def initDevice(self):
        '''
        Does a reset to put all registers in initial state
        '''
        #Set pin numbering mode
        GPIO.setmode(GPIO.BOARD)

        #Define the reset pin as output
        GPIO.setup(self.RstPin, GPIO.OUT)
        #Create a reset impulse
        GPIO.output(self.RstPin, GPIO.LOW)
        #wait for 50 ms
        time.sleep(.050)
        GPIO.output(self.RstPin, GPIO.HIGH)