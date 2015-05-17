__author__ = 'holzi'

from garden_lighting.MCP23017.raspberry import RaspberryMCP23017

pin_number_mapping = {
    0: 0b00000001,
    1: 0b00000010,
    2: 0b00000100,
    3: 0b00001000,
    4: 0b00010000,
    5: 0b00100000,
    6: 0b01000000,
    7: 0b10000000,
    8: 0b00000001,
    9: 0b00000010,
    10: 0b00000100,
    11: 0b00001000,
    12: 0b00010000,
    13: 0b00100000,
    14: 0b01000000,
    15: 0b10000000,
}


def calculate_bit_pattern(mode, light_number, current_bit_pattern):
    """
    This function calculates a 8Bit pattern to switch a desired light number
    on or off regarding an existing bit_pattern.

    :param mode: choose [mode = '1' for 'ON'] and [mode = '0' for 'OFF']
    :param light_number: Determines the light number (0 to 15) to switch
    :param current_bit_pattern: 8Bit input bit pattern to modify
    :return: The updated bit_pattern
    """
    if mode == 1:
        return current_bit_pattern | pin_number_mapping[light_number]
    elif mode == 0:
        return current_bit_pattern & ~pin_number_mapping[light_number]
    else:
        assert "You entered an invalid mode!"


class LightControl:
    """
    Implements access to all fuctions of the LightController
    (Combines 2 RelaisArray modules)

    Interrupt is Configured as following:

    PortA disable
    PortB enable
    PortB IOPol = negative (so active = value 1 on the Port)
    Interrput Active High
    Compare against DEVAL register (val = 0x00) (interrupt if differ)

    Please regard the documentation of the methods
    """
    ControlUnitA = 0x00
    ControlUnitB = 0x00

    def __init__(self, light_scheduler):
        self.light_scheduler = light_scheduler
        self.ControlUnitA = RaspberryMCP23017(0x20, 7)
        self.ControlUnitB = RaspberryMCP23017(0x21, 11)

    def init(self):
        """
        This function initializes the light controller.
        Configures it for interrupts, sets io-directions etc.
        """
        # First do a reset to init the devices
        self.ControlUnitA.initDevice()
        self.ControlUnitB.initDevice()

        # I/O EXPANDER CONFIGURATION REGISTER
        # Bit 7 = BANK 0 ->0
        # Bit 6 = MIRROR disable -> 0
        # Bit 5 = SEQOP enable -> 0 (does not matter)
        # Bit 4 = DISSLW enable -> 0
        # Bit 3 = HAEN always on -> 0
        # Bit 2 = ODR active output -> 0
        # Bit 1 = INTPOL active high -> 1
        # Bit 0 = unimplemented
        # --> 0x02
        self.ControlUnitA.set_configuration_reg(0x02)
        self.ControlUnitB.set_configuration_reg(0x02)

        # Set Port A to Output
        self.ControlUnitA.set_io_direction_port_a(0x00)
        self.ControlUnitB.set_io_direction_port_a(0x00)

        # Set Port B to Input
        self.ControlUnitA.set_io_direction_port_b(0xFF)
        self.ControlUnitB.set_io_direction_port_b(0xFF)

        # Set Pull up resistors (PortB Enabled)
        # PortA
        self.ControlUnitA.set_pull_up_resistor_port_a(0x00)
        self.ControlUnitB.set_pull_up_resistor_port_a(0x00)
        # PortB
        self.ControlUnitA.set_pull_up_resistor_port_b(0xFF)
        self.ControlUnitB.set_pull_up_resistor_port_b(0xFF)

        # Set Input Polarity
        # PortA (Output ->not negated)
        self.ControlUnitA.set_input_polarity_port_a(0x00)
        self.ControlUnitB.set_input_polarity_port_a(0x00)
        # PortB  (Input with pullups -> negated)
        # (Pin 6,7 are grounded -> do not negate)
        self.ControlUnitA.set_input_polarity_port_b(0x3F)
        self.ControlUnitB.set_input_polarity_port_b(0x3F)

        # Set Interrupt on Change
        # PortA disable interrupt
        self.ControlUnitA.set_interrupt_on_change_port_a(0x00)
        self.ControlUnitB.set_interrupt_on_change_port_a(0x00)
        # PortB enable interrupts Pin 6,7 are grounded -> not enable)
        self.ControlUnitA.set_interrupt_on_change_port_b(0x3F)
        self.ControlUnitB.set_interrupt_on_change_port_b(0x3F)

        # Set Default Compare Register
        self.ControlUnitA.set_default_compare_port_b(0x00)
        self.ControlUnitB.set_default_compare_port_b(0x00)

        # Set Interrupt Control register (use DEFVAL)
        self.ControlUnitA.set_interrupt_control_port_b(0xFF)
        self.ControlUnitB.set_interrupt_control_port_b(0xFF)

    def set_multiple_lights(self, mode, lights):
        """
        This function sets or clears a list of light numbers of the controller
        Note: 2 reads, 2 writes are done via I2C
              (one write and read for each device)

        :param mode: choose [mode = '1' for 'ON'] and [mode = '0' for 'OFF']
        :param lights:  A 'list' element containing the desired light_numbers to switch
        :return: Represents success: ['-1' if Pin number invalid]
        """
        current_bit_patternA = self.ControlUnitA.read_byte_port_a()
        current_bit_patternB = self.ControlUnitB.read_byte_port_a()

        # calculate bit pattern for every light number
        for light in lights:

            if not self.light_scheduler.can_switch(light):
                self.light_scheduler.schedule_switch(light, mode)
                print("Switching scheduled")
                continue

            self.light_scheduler.update_switched(light)
            print("Switching direct")

            if (light <= 7) and (light >= 0):  # between 0 and 7
                # Use unit A
                current_bit_patternA = calculate_bit_pattern(mode, light, current_bit_patternA)

            elif (light >= 8) and (light <= 15):  # between 8 and 15
                # Use unit B
                current_bit_patternB = calculate_bit_pattern(mode, light, current_bit_patternB)
            else:
                assert 0, "You entered an invalid Pin Number!"
                return False

        # Do only one Bus access or each device to avoid spamming the bus
        self.ControlUnitA.write_byte_port_a(current_bit_patternA)
        self.ControlUnitB.write_byte_port_a(current_bit_patternB)
        return True

    def get_lights(self, state):
        """
            :param state False for off, True for on
            :return: The lights which have the specified state
        """
        lights_pattern = self.ControlUnitA.read_byte_port_a() | self.ControlUnitB.read_byte_port_a() << 8

        lights = []

        for i in range(0, 16):
            # lights_pattern & (1 << i)) == 0 -> OFF
            # lights_pattern & (1 << i)) != 0 -> ON
            result = lights_pattern & (1 << i)
            if (state and result != 0) or (not state and result == 0):
                lights.append(i)

        return lights

    def read_interrupt_capture(self):
        """
        This function returns the 16Bit input-interrupt value of the controller
        Note: 2 reads are done via I2C (one for each device)

        Caution not tested

        :return: 16Bit input bit_pattern
        """
        # TODO NOT TESTED!

        bit_patternA = self.ControlUnitA.read_interrupt_capture_reg_port_b()
        bit_patternB = self.ControlUnitB.read_interrupt_capture_reg_port_b()

        return (bit_patternB << 8) | bit_patternA

    def read_interrupt_flags(self, part):
        """
        his function reads the values ( '1' for 'ON', '0' for 'OFF)
        of the input-interrupt flags 0-7 or 8-15 as an 8Bit value

        Choose:  part = 0 for inputs 0-7
                 part = 1 for inputs 8-15

        Note: 1 read is done via I2C

        caution not tested

        :param part: ['0' for inputs 0-7], ['1' for inputs 8-15]
        :return: An 8 Bit value representing part1 or part0
        """
        # TODO NOT TESTED!
        # Inputs 0-7
        if part == 0:
            return self.ControlUnitA.read_interrupt_flag_reg_port_b()
        # Inputs 8-15
        elif part == 1:
            return self.ControlUnitB.read_interrupt_flag_reg_port_b()
        else:
            assert 0, "You entered an invalid mode. '0' for Pins 0-7; '1' for pins 8-15"
            return -1