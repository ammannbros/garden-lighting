import time
import wiringpi
from garden_lighting.MCP23017.MCP23017 import MCP23017


class RaspberryMCP23017(MCP23017):
    def __init__(self, dev_addr, rst_pin=0xFF, i2cport=1):
        super().__init__(dev_addr, rst_pin, i2cport)

    def initDevice(self):
        '''
        Does a reset to put all registers in initial state
        '''

        # Set pin numbering mode
        #  wiringPiSetupSys() did not work because pins were low after booting and running the write commands
        # This requires root!
        wiringpi.wiringPiSetupGpio()

        # Define the reset pin as output
        wiringpi.pinMode(self.RstPin, wiringpi.GPIO.OUTPUT)
        # Create a reset impulse
        wiringpi.digitalWrite(self.RstPin, wiringpi.GPIO.LOW)
        # wait for 50 ms
        time.sleep(.050)
        wiringpi.digitalWrite(self.RstPin, wiringpi.GPIO.HIGH)
