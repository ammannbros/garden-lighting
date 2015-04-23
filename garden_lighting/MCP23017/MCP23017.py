# coding=utf-8
__author__ = 'holzi'

import smbus
import time
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! Maybe you are not root?")

# global constans
OUT = 0
IN = 1
LOW = 0
HIGH = 1
TRUE = 1
FALSE = 0

class MCP23017:
    '''
    Implements access functions for the MCP2017 via I2C

    please regard the documentation of the methods

    The Class uses the smbus interface to access the chip.
    Refers to Datasheet: http://ww1.microchip.com/downloads/en/DeviceDoc/21952b.pdf

    Attributes:
    (meets the shortcuts of the datasheet)
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
    '''

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

    I2CPort = 0x00                  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
    bus = 0x00                      # SMBUS-Object
    devAddr = 0x00
    devRegMode = 0x00
    RstPin = 0xFF

    def __init__(self, dev_addr, rst_pin = 0xFF ,  i2cport = 1):
        '''
        Initialises the Class. You have to specify the I2C-address of your device
        and the I2C-port your raspberry uses

        If you want to use the initDevice function you have to connect the reset
        of the MCP23017 to a GPIO Pin. (optional)
        Please use the pin numbers used by raspberry-gpio-python and mode BOARD.
        [GPIO.setmode(GPIO.BOARD)]

        Note: Device i2cport = 1 is predefined

        :param devaddr: The Address of the Device as uint8
        :param rst_pin: The aspberry-gpio-python pin number which is connected to the reset pin
        :param i2cport: The i2cPort of your Rasperry (1[newer devices] or 0[older devicers])
        '''

        self.I2CPort = i2cport
        self.bus = smbus.SMBus(self.I2CPort)
        self.devAddr = dev_addr
        self.devRegMode = 0x00      # Only Byte mode supported so far
        self.RstPin = rst_pin

    def initDevice(self):
        '''
        Does a reset to put all registers in inital state
        '''
        #Set pin numbering mode
        GPIO.setmode(GPIO.BOARD)

        #Define the teset pin as output
        GPIO.setup(self.RstPin, GPIO.OUT)

        #Create a reset impulse
        GPIO.output(self.RstPin, GPIO.LOW)
        #wait for 50 ms
        time.sleep(.050)
        GPIO.output(self.RstPin, GPIO.HIGH)


    @staticmethod
    def check_uint8(bit_pattern):
        '''
        Checks if the input bit_pattern is a valid uint8

        :param bit_pattern: bit pattern to check if uint8
        :return: TRUE if valid , FALSE if invalid
        '''
        if (bit_pattern >= 0) and (bit_pattern <= 0xFF):
            return TRUE
        else:
            assert 0, "Invalid Data, expected a one byte pattern"
            return FALSE

    def set_io_direction_port_a(self, bit_pattern):
        '''
        I/O DIRECTION REGISTER
        Controls the direction of the data I/O.

        If a bit is set, the corresponding pin becomes an
        input. When a bit is clear, the corresponding pin
        becomes an output.

        1 = Pin is configured as an input.
        0 = Pin is configured as an output.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''

        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, IODIRA, bit_pattern)
        else:
            return -1

    def set_io_direction_port_b(self, bit_pattern):
        '''
        I/O DIRECTION REGISTER
        Controls the direction of the data I/O.

        If a bit is set, the corresponding pin becomes an
        input. When a bit is clear, the corresponding pin
        becomes an output.

        1 = Pin is configured as an input.
        0 = Pin is configured as an output.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''

        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, IODIRB, bit_pattern)
        else:
            return -1

    def set_input_polarity_port_a(self, bit_pattern):
        '''
        INPUT POLARITY REGISTER
        This register allows the user to configure the polarity on
        the corresponding GPIO port bits.

        If a bit is set, the corresponding GPIO register bit will
        reflect the inverted value on the pin.

        1 = GPIO register bit will reflect the opposite logic state of the input pin.
        0 = GPIO register bit will reflect the same logic state of the input pin.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, IPOLA, bit_pattern)
        else:
            return -1

    def set_input_polarity_port_b(self, bit_pattern):
        '''
        INPUT POLARITY REGISTER
        This register allows the user to configure the polarity on
        the corresponding GPIO port bits.

        If a bit is set, the corresponding GPIO register bit will
        reflect the inverted value on the pin.

        1 = GPIO register bit will reflect the opposite logic state of the input pin.
        0 = GPIO register bit will reflect the same logic state of the input pin.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, IPOLB, bit_pattern)
        else:
            return -1

    def set_interrupt_on_change_port_a(self, bit_pattern):
        '''
        INTERRUPT-ON-CHANGE CONTROL REGISTER
        The GPINTEN register controls the interrupt-onchange
        feature for each pin.

        If a bit is set, the corresponding pin is enabled for
        interrupt-on-change. The DEFVAL and INTCON
        registers must also be configured if any pins are
        enabled for interrupt-on-change.

        1 = Enable GPIO input pin for interrupt-on-change event.
        0 = Disable GPIO input pin for interrupt-on-change event.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, GPINTENA, bit_pattern)
        else:
            return -1


    def set_interrupt_on_change_port_b(self, bit_pattern):
        '''
        INTERRUPT-ON-CHANGE CONTROL REGISTER
        The GPINTEN register controls the interrupt-onchange
        feature for each pin.

        If a bit is set, the corresponding pin is enabled for
        interrupt-on-change. The DEFVAL and INTCON
        registers must also be configured if any pins are
        enabled for interrupt-on-change.

        1 = Enable GPIO input pin for interrupt-on-change event.
        0 = Disable GPIO input pin for interrupt-on-change event.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, GPINTENB, bit_pattern)
        else:
            return -1


    def set_default_compare_port_a(self, bit_pattern):
        '''
        DEFAULT COMPARE REGISTERFOR INTERRUPT-ON-CHANGE
        The default comparison value is configured in the
        DEFVAL register.

        If enabled (via GPINTEN and INTCON) to compare against
        the DEFVAL register, an opposite value on the associated
        pin will cause an interrupt to occur.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, DEFVALA, bit_pattern)
        else:
            return -1

    def set_default_compare_port_b(self, bit_pattern):
        '''
        DEFAULT COMPARE REGISTERFOR INTERRUPT-ON-CHANGE
        The default comparison value is configured in the
        DEFVAL register.

        If enabled (via GPINTEN and INTCON) to compare against
        the DEFVAL register, an opposite value on the associated
        pin will cause an interrupt to occur.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, DEFVALB, bit_pattern)
        else:
            return -1

    def set_interrupt_control_port_a(self, bit_pattern):
        '''
        INTERRUPT CONTROL REGISTER
        The INTCON register controls how the associated pin
        value is compared for the interrupt-on-change feature.

        If a bit is set, the corresponding I/O pin is compared
        against the associated bit in the DEFVAL register. If a
        bit value is clear, the corresponding I/O pin is compared
        against the previous value.

        1 = Controls how the associated pin value is compared for interrupt-on-change.
        0 = Pin value is compared against the previous pin value.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, INTCONA, bit_pattern)
        else:
            return -1

    def set_interrupt_control_port_b(self, bit_pattern):
        '''
        INTERRUPT CONTROL REGISTER
        The INTCON register controls how the associated pin
        value is compared for the interrupt-on-change feature.

        If a bit is set, the corresponding I/O pin is compared
        against the associated bit in the DEFVAL register. If a
        bit value is clear, the corresponding I/O pin is compared
        against the previous value.

        1 = Controls how the associated pin value is compared for interrupt-on-change.
        0 = Pin value is compared against the previous pin value.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, INTCONB, bit_pattern)
        else:
            return -1

    def set_pull_up_resistor_port_a(self, bit_pattern):
        '''
        PULL-UP RESISTOR CONFIGURATION REGISTER
        The GPPU register controls the pull-up resistors for the
        port pins.

        If a bit is set and the corresponding pin is
        configured as an input, the corresponding port pin is
        internally pulled up with a 100 kΩ resistor.

        1 = Pull-up enabled.
        0 = Pull-up disabled.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, GPPUA, bit_pattern)
        else:
            return -1

    def set_pull_up_resistor_port_b(self, bit_pattern):
        '''
        PULL-UP RESISTOR CONFIGURATION REGISTER
        The GPPU register controls the pull-up resistors for the
        port pins.

        If a bit is set and the corresponding pin is
        configured as an input, the corresponding port pin is
        internally pulled up with a 100 kΩ resistor.

        1 = Pull-up enabled.
        0 = Pull-up disabled.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, GPPUB, bit_pattern)
        else:
            return -1

    def read_interrupt_flag_reg_port_a(self):
        '''
        INTERRUPT FLAG REGISTER
        The INTF register reflects the interrupt condition on the
        port pins of any pin that is enabled for interrupts via the
        GPINTEN register.

        A ‘set’ bit indicates that the associated pin caused the interrupt.

        This register is ‘read-only’. Writes to this register will be
        ignored.

        1 = Pin caused interrupt.
        0 = Interrupt not pending.

        :return: The value of the specified register as 8-Bit-word
        '''
        return self.bus.write_byte_data(self.devAddr, INTFA, bit_pattern)

    def read_interrupt_flag_reg_port_b(self):
        '''
        INTERRUPT FLAG REGISTER
        The INTF register reflects the interrupt condition on the
        port pins of any pin that is enabled for interrupts via the
        GPINTEN register.

        A ‘set’ bit indicates that the associated pin caused the interrupt.

        This register is ‘read-only’. Writes to this register will be
        ignored.

        1 = Pin caused interrupt.
        0 = Interrupt not pending.

        :return: The value of the specified register as 8-Bit-word
        '''
        return self.bus.write_byte_data(self.devAddr, INTFB, bit_pattern)

    def read_interrupt_capture_reg_port_a(self):
        '''
        INTERRUPT CAPTURE REGISTER
        The INTCAP register captures the GPIO port value at
        the time the interrupt occurred. The register is ‘read
        only’ and is updated only when an interrupt occurs.

        The register will remain unchanged until the interrupt is
        cleared via a read of INTCAP or GPIO.

        1 = Logic-high.
        0 = Logic-low.

        :return: The value of the specified register as 8-Bit-word
        '''
        return self.bus.write_byte_data(self.devAddr, INTCAPA, bit_pattern)

    def read_interrupt_capture_reg_port_b(self, bit_pattern):
        '''
        INTERRUPT CAPTURE REGISTER
        The INTCAP register captures the GPIO port value at
        the time the interrupt occurred. The register is ‘read
        only’ and is updated only when an interrupt occurs.

        The register will remain unchanged until the interrupt is
        cleared via a read of INTCAP or GPIO.

        1 = Logic-high.
        0 = Logic-low.

        :return: The value of the specified register as 8-Bit-word
        '''
        return self.bus.write_byte_data(self.devAddr, INTCAPB, bit_pattern)

    def read_byte_port_a(self):
        '''
        PORT REGISTER
        The GPIO register reflects the value on the port.
        Reading from this register reads the port. Writing to this
        register modifies the Output Latch (OLAT) register.

        Note: set the output registers is done via the output latches (OLAT)

        :return: The value of the specified register as 8-Bit-word
        '''
        return self.bus.read_byte_data(self.devAddr, GPIOA)

    def read_byte_port_b(self):
        '''
        PORT REGISTER
        The GPIO register reflects the value on the port.
        Reading from this register reads the port. Writing to this
        register modifies the Output Latch (OLAT) register.

        Note: set the output registers is done via the output latches (OLAT)

        :return: The value of the specified register as 8-Bit-word
        '''
        return self.bus.read_byte_data(self.devAddr, GPIOB)

    def write_byte_port_a(self, bit_pattern):
        '''
        OUTPUT LATCH REGISTER (OLAT)
        The OLAT register provides access to the output
        latches. A write to this register
        modifies the output latches that modifies the pins
        configured as outputs.

        1 = Logic-high.
        0 = Logic-low.

        Note: Reading the output registers is done via the port registers (GPIO)

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, OLATA, bit_pattern)
        else:
            return -1

    def write_byte_port_b(self, bit_pattern):
        '''
        OUTPUT LATCH REGISTER (OLAT)
        The OLAT register provides access to the output
        latches. A write to this register
        modifies the output latches that modifies the pins
        configured as outputs.

        1 = Logic-high.
        0 = Logic-low.

        Note: Reading the output registers is done via the port registers (GPIO)

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, OLATB, bit_pattern)
        else:
            return -1

    def set_configuration_reg(self, bit_pattern):
        '''
        CONFIGURATION REGISTER
        The IOCON register contains several bits for
        configuring the device:

        The BANK bit changes how the registers are mapped
        •   If BANK = 1, the registers associated with each
            port are segregated. Registers associated with
            PORTA are mapped from address 00h - 0Ah and
            registers associated with PORTB are mapped
            from 10h - 1Ah.
        •   If BANK = 0, the A/B registers are paired. For
            example, IODIRA is mapped to address 00h and
            IODIRB is mapped to the next address (address
            01h). The mapping for all registers is from 00h -
            15h.

        When MIRROR = 1, the INTn pins are functionally
        OR’ed so that an interrupt on either port will cause
        both pins to activate.
        When MIRROR = 0, the INT pins are separated.
        Interrupt conditions on a port will cause its
        respective INT pin to activate.

        The Sequential Operation (SEQOP) controls the
        incrementing function of the Address Pointer. If the
        address pointer is disabled, the Address Pointer does
        not automatically increment after each byte is clocked
        during a serial transfer. This feature is useful when it is
        desired to continuously poll (read) or modify (write) a
        register.

        The Slew Rate (DISSLW) bit controls the slew rate
        function on the SDA pin. If enabled, the SDA slew rate
        will be controlled when driving from a high to low.

        The Hardware Address Enable (HAEN) bit enables/
        disables hardware addressing on the MCP23S17 only.
        The address pins (A2, A1 and A0) must be externally
        biased, regardless of the HAEN bit value.
        If enabled (HAEN = 1), the device’s hardware address
        matches the address pins.
        If disabled (HAEN = 0), the device’s hardware address
        is A2 = A1 = A0 = 0.

        The Open-Drain (ODR) control bit enables/disables the
        INT pin for open-drain configuration. Erasing this bit
        overrides the INTPOL bit.

        The Interrupt Polarity (INTPOL) sets the polarity of the
        INT pin. This bit is functional only when the ODR bit is
        cleared, configuring the INT pin as active push-pull.


        bit 7 BANK: Controls how the registers are addressed
                1 = The registers associated with each port are separated into different banks
                0 = The registers are in the same bank (addresses are sequential)
        bit 6 MIRROR: INT Pins Mirror bit
                1 = The INT pins are internally connected
                0 = The INT pins are not connected. INTA is associated with PortA and INTB is associated with PortB
        bit 5 SEQOP: Sequential Operation mode bit.
                1 = Sequential operation disabled, address pointer does not increment.
                0 = Sequential operation enabled, address pointer increments.
        bit 4 DISSLW: Slew Rate control bit for SDA output.
                1 = Slew rate disabled.
                0 = Slew rate enabled.
        bit 3 HAEN: Hardware Address Enable bit (MCP23S17 only). Address pins are always enabled on MCP23017.
                1 = Enables the MCP23S17 address pins.
                0 = Disables the MCP23S17 address pins.
        bit 2 ODR: This bit configures the INT pin as an open-drain output.
                1 = Open-drain output (overrides the INTPOL bit).
                0 = Active driver output (INTPOL bit sets the polarity).
        bit 1 INTPOL: This bit sets the polarity of the INT output pin.
                1 = Active-high.
                0 = Active-low.
        bit 0 Unimplemented: Read as ‘0’.

        :param bit_pattern: A 8 bit word to write into the specified register
        :return: Represents success: ['-1' if unsuccessful]
        '''
        if self.check_uint8(bit_pattern):
            #Write to bus
            return self.bus.write_byte_data(self.devAddr, IOCON, bit_pattern)
        else:
            return -1

    def read_byte_gen_register(self, reg_addr):
        '''
        Use this function to read from any configuration register.

        The register adresses are defined as public variables of the class
        which meets the definition in the data sheet.
        (e.g read_byte_gen_register(self, self.IODIRA) to read from IODIRA)

        :param reg_addr: Determines the address of the Register to read
        :return: The value of the specified register as 8-Bit-word
        '''
        if self.check_uint8(reg_addr):
            return self.bus.read_byte_data(self.devAddr, reg_addr)
        else:
            return -1
