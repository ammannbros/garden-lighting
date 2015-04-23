rebo
__author__ = 'holzi'

import sys
from MCP23017 import MCP23017
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Maybe you are not root?")

#Remote Debug configuration

'''
import sys
sys.path.append('/home/pi/garden-lighting/garden_lighting/MCP23017/pycharm-debug.egg')
import pydevd
pydevd.settrace('holziVirtualBox', port=12000, stdoutToServer=True, stderrToServer=True)
'''


##Do a short test of the MCP2017 class

Chip2 = MCP23017(0x21, 11)
Chip2.initDevice()

print("Write a bit Pattern to Port a and read the value")
##Set Port A to Output
Chip2.set_io_direction_port_a(0x00)
Chip2.write_byte_port_a(0x0A)
if Chip2.read_byte_port_a() == 0x0A:
    print("PASS")
else:
    print("FAIL")

print("Write a bit Pattern to Port b and read the value")
##Set Port B to Output
Chip2.set_io_direction_port_b(0x00)
Chip2.write_byte_port_b(0x0A)
if Chip2.read_byte_port_b() == 0x0A:
    print("PASS")
else:
    print("FAIL")

print("Set port b to output and enable pullups -> read value should be 0x3f")
Chip2.set_io_direction_port_b(0xFF)
Chip2.set_pull_up_resistor_port_b(0xFF)
if Chip2.read_byte_port_b() == 0x3F:
    print("PASS")
else:
    print("FAIL")

print("When a reset is done port a should be in inital state")
Chip2.initDevice()
##Set Port A to Output
Chip2.set_io_direction_port_a(0x00)
if Chip2.read_byte_port_a() == 0x00:
    print("PASS")
else:
    print("FAIL")
