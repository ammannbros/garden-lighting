__author__ = 'holzi'

from MCP23017.MCP23017 import MCP23017

#Global constants
TRUE = 1
FALSE = 0

class LightControl:

    ControlUnitA = 0x00
    ControlUnitB = 0x00

    pin_number_mapping = {
      0  : 0b00000001,
      1  : 0b00000010,
      2  : 0b00000100,
      3  : 0b00001000,
      4  : 0b00010000,
      5  : 0b00100000,
      6  : 0b01000000,
      7  : 0b10000000,
      8  : 0b00000001,
      9  : 0b00000010,
      10 : 0b00000100,
      11 : 0b00001000,
      12 : 0b00010000,
      13 : 0b00100000,
      14 : 0b01000000,
      15 : 0b10000000,
    }

    def __init__(self):
        self.ControlUnitA = MCP23017(0x20, 7)
        self.ControlUnitB = MCP23017(0x21, 11)

    def init_LightControl(self):

        #First do a reset to init the devices
        self.ControlUnitA.initDevice()
        self.ControlUnitB.initDevice()

        #Set Port A to Output
        self.ControlUnitA.set_io_direction_port_a(0x00)
        self.ControlUnitB.set_io_direction_port_a(0x00)

        #Set Port B to Input
        self.ControlUnitA.set_io_direction_port_b(0xFF)
        self.ControlUnitB.set_io_direction_port_b(0xFF)

        #TODO interrups pullups.....

    def calculate_bit_pattern(self, mode, light_number, current_bit_pattern):
        if mode == 1:
            return current_bit_pattern | self.pin_number_mapping[light_number]
        elif mode == 0:
            return current_bit_pattern & ~self.pin_number_mapping[light_number]
        else:
            assert "You entered an invalid mode!"

    def set_light(self, mode, light_number):
        if (light_number <= 7) and (light_number >= 0):         #between 0 and 7
            #Use unit A
            current_bit_pattern = self.ControlUnitA.read_byte_port_a()
            current_bit_pattern = self.calculate_bit_pattern(mode, light_number, current_bit_pattern)
            self.ControlUnitA.write_byte_port_a(current_bit_pattern)

        elif (light_number >= 8) and (light_number <= 15):      #between 8 and 15
            #Use Unit B
            current_bit_pattern = self.ControlUnitB.read_byte_port_a()
            current_bit_pattern = self.calculate_bit_pattern(mode, light_number, current_bit_pattern)
            self.ControlUnitB.write_byte_port_a(current_bit_pattern)
        else:
            assert 0, "You entered an invalid Pin Number!"
            return -1
        return 0

    def set_multiple_lights(self, mode, lights):

        current_bit_patternA = self.ControlUnitA.read_byte_port_a()
        current_bit_patternB = self.ControlUnitB.read_byte_port_a()

        for i in lights:
            if (i <= 7) and (i >= 0):         #between 0 and 7
                #Use unit A
                current_bit_patternA = self.calculate_bit_pattern(mode, i, current_bit_patternA)

            elif (i >= 8) and (i <= 15):      #between 8 and 15
                current_bit_patternB = self.calculate_bit_pattern(mode, i, current_bit_patternB)
            else:
                assert 0, "You entered an invalid Pin Number!"
                return -1

        self.ControlUnitA.write_byte_port_a(current_bit_patternA)
        self.ControlUnitB.write_byte_port_a(current_bit_patternB)
        return 0

    def set_all(self, mode):
        if mode == 1:
            self.ControlUnitA.write_byte_port_a(0xFF)
            self.ControlUnitB.write_byte_port_a(0xFF)
        elif mode == 0:
            self.ControlUnitA.write_byte_port_a(0x00)
            self.ControlUnitB.write_byte_port_a(0x00)
        else:
            assert 0, "You entered an invalid Pin Number!"
            return -1
        return 0

    def read_light(self, light_number):
        if (light_number <= 7) and (light_number >= 0):         #between 0 and 7
            #Use unit A
            current_bit_pattern = self.ControlUnitA.read_byte_port_a()
            result = current_bit_pattern & self.pin_number_mapping[light_number]
            if result == 0:
                return 0
            else:
                return 1

        elif (light_number >= 8) and (light_number <= 15):      #between 8 and 15
            current_bit_pattern = self.ControlUnitB.read_byte_port_a()
            result =  current_bit_pattern & self.pin_number_mapping[light_number]
            if result == 0:
                return 0
            else:
                return 1
        else:
            assert 0, "You entered an invalid Pin Number!"
            return -1

    def read_multiple_lights(self, part):
        #Lights 0-7
        if part == 0:
            return self.ControlUnitA.read_byte_port_a()
        #Lights 8-15
        elif part == 1:
            return self.ControlUnitB.read_byte_port_a()
        else:
            assert 0, "You entered an invalid mode. '0' for Pins 0-7; '1' for pins 8-15"
            return -1