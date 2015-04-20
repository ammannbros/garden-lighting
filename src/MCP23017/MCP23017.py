__author__ = 'holzi'

# !/usr/bin/python
import smbus

# Defines
IODIRA   = 0x00
IODIRB   = 0x01
IPOLA    = 0x02
IPOLB    = 0x03
GPINTENA = 0x04
GPINTENB = 0x05
DEFVALA  = 0x06
DEFVALB  = 0x07
INTCONA  = 0x08
INTCONB  = 0x09
IOCON    = 0x0A     # 0x0B points to the same register
GPPUA    = 0x0C
GPPUB    = 0x0D
INTFA    = 0x0E
INTFB    = 0x0F
INTCAPA  = 0x10
INTCAPB  = 0x11
GPIOA    = 0x12
GPIOB    = 0x13
OLATA    = 0x14
OLATB    = 0x15

OUT = 0
IN = 1
LOW = 0
HIGH = 1
TRUE = 1
FALSE = 0

class MCP23017:
    # constans


    I2CPort = 0x00                  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
    bus = 0x00                      # SMBUS-Object
    devAddr = 0x00
    devRegMode = 0x00

    def __init__(self, devaddr, i2cport = 1):

        self.I2CPort = i2cport
        self.bus = smbus.SMBus(self.I2CPort)
        self.devAddr = devaddr
        self.devRegMode = 0x00      # Only Byte mode supported so far

    def initDevice(self):
        pass
        #TODO Reset ausfuehren

    @staticmethod
    def check_uint8(self, bit_pattern):
        #check if bit_pattern accords to uint8
        if (bit_pattern >= 0) and (bit_pattern <= 0xFF):
            return TRUE
        else:
            assert 0, "Invalid Data, expected a one byte pattern"
            return FALSE

    def set_io_direction_port_a(self, bit_pattern):
        '''Controls the direction of the data I/O. [0 - Output] [1 - Input]: PortA.'''
        if check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, IODIRA, bit_pattern)
        else:
            return -1

    def set_io_direction_port_b(self, bit_pattern):
        '''Controls the direction of the data I/O. [0 - Output] [1 - Input]: PortB.'''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, IODIRB, bit_pattern)
        else:
            return -1

    def set_input_polarity_port_a(self, bit_pattern):
        '''If a bit is set, the corresponding GPIO register bit will
        reflect the inverted value on the pin: PortA.'''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, IPOLA, bit_pattern)
        else:
            return -1

    def set_input_polarity_port_b(self, bit_pattern):
        '''If a bit is set, the corresponding GPIO register bit will
        reflect the inverted value on the pin: PortB.'''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, IPOLB, bit_pattern)
        else:
            return -1

    def write_byte_port_a(self, bit_pattern):
        '''A write to this register modifies the output latches that modifies
        the pins configured as outputs: PortA'''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, OLATA, bit_pattern)
        else:
            return -1

    def write_byte_port_b(self, bit_pattern):
        '''A write to this register modifies the output latches that modifies
        the pins configured as outputs: PortB'''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, OLATB, bit_pattern)
        else:
            return -1

    def read_byte_port_a(self):
        #Read from bus
        return self.bus.read_byte_data(self.devAddr, GPIOA)

    def read_byte_port_b(self):
        #Read from bus
        return self.bus.read_byte_data(self.devAddr, GPIOB)

