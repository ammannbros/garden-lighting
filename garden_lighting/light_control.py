from datetime import datetime
from threading import Lock
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

    def __init__(self, max_switch, delay, logger):
        self.logger = logger
        self.ControlUnitA = RaspberryMCP23017(0x20, 7)
        self.ControlUnitB = RaspberryMCP23017(0x21, 11)

        self.delay = delay
        self.last_switched = {}
        self.max_switch = max_switch
        self.schedules = {}

        self.last_a = 0
        self.last_b = 0

        self.lock = Lock()
        self.switch_lock = Lock()

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

    def set_lights(self, state, lights):
        if not lights:
            return

        for light in lights:

            if not self.can_switch(light):
                self.schedule_switch(light, state, datetime.now() + self.max_switch)
            else:
                self.schedule_switch(light, state, datetime.now())

    def build_lights(self, state, a, b):
        """
            :param state False for off, True for on
            :return: The lights which have the specified state
        """
        lights_pattern = a | b << 8

        lights = []

        for i in range(0, 16):
            # lights_pattern & (1 << i)) == 0 -> OFF
            # lights_pattern & (1 << i)) != 0 -> ON
            result = lights_pattern & (1 << i)
            if (state and result != 0) or (not state and result == 0):
                lights.append(i)

        return lights

    def get_lights(self, state):
        """
            :param state False for off, True for on
            :return: The lights which have the specified state
        """

        return self.build_lights(state, self.last_a, self.last_b)

    def run(self):
        self.lock.acquire()

        try:
            now = datetime.now()

            self.last_a = a = self.ControlUnitA.read_byte_port_a()
            self.last_b = b = self.ControlUnitB.read_byte_port_a()

            for light, value in self.schedules.items():

                time = value[0]
                mode = value[1]
                if time < now:
                    self.logger.info("Switching light %s %s" % (light, mode))

                    self.update_switched(light)

                    if (light <= 7) and (light >= 0):  # between 0 and 7
                        a = calculate_bit_pattern(mode, light, a)
                    elif (light >= 8) and (light <= 15):  # between 8 and 15
                        b = calculate_bit_pattern(mode, light, b)

            if a != self.last_a:
                self.ControlUnitA.write_byte_port_a(a)
            if b != self.last_b:
                self.ControlUnitB.write_byte_port_a(b)

            self.last_a = a
            self.last_b = b

            self.schedules = {light: value for light, value in self.schedules.items() if value[0] > now}
        finally:
            self.lock.release()

    def can_switch(self, light):
        self.switch_lock.acquire()
        try:
            if light not in self.last_switched:
                return True
            ret = self.last_switched[light] < datetime.now() - self.max_switch
        finally:
            self.switch_lock.release()
        return ret

    def update_switched(self, light):
        self.switch_lock.acquire()
        try:
            self.last_switched[light] = datetime.now()
        finally:
            self.switch_lock.release()

    def schedule_switch(self, light, mode, time):
        self.lock.acquire()
        try:
            is_on = self.build_lights(True, self.last_a, self.last_b)

            if light in is_on and mode:
                return
            if light not in is_on and not mode:
                return

            if light in self.schedules:
                self.schedules[light] = (self.schedules[light][0], mode)
                self.logger.info("Updated %s %s" % (light, mode))
            else:
                self.schedules[light] = (time, mode)
                self.logger.info("Set scheduler for %s %s" % (light, mode))
        finally:
            self.lock.release()

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
