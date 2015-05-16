from datetime import datetime
from time import sleep
from threading import Thread
from garden_lighting.light_control import calculate_bit_pattern


class LightScheduler:
    def __init__(self, max_switch, delay, control=None):
        self.control = control
        self.delay = delay
        self.last_switched = {}
        self.max_switch = max_switch
        self.schedules = {}

        self.running = False

    def run(self):
        now = datetime.now()

        a = self.control.ControlUnitA.read_byte_port_a()
        b = self.control.ControlUnitB.read_byte_port_a()

        for light, value in self.schedules.items():

            time = value[0]
            mode = value[1]
            if time < now:  # todo: check if somebody already updated again
                print("Switch light %s" % light)

                if (light <= 7) and (light >= 0):  # between 0 and 7
                    a = calculate_bit_pattern(mode, light, a)
                elif (light >= 8) and (light <= 15):  # between 8 and 15
                    b = calculate_bit_pattern(mode, light, b)

        self.control.ControlUnitA.write_byte_port_a(a)
        self.control.ControlUnitB.write_byte_port_a(b)

        self.schedules = {light: value for light, value in self.schedules.items() if value[0] > now}

    def can_switch(self, light):
        if light not in self.last_switched:
            return True
        return self.last_switched[light] < datetime.now() - self.max_switch

    def update_switched(self, light):
        self.last_switched[light] = datetime.now()
        pass

    def schedule_switch(self, light, mode):
        self.schedules[light] = (datetime.now() + self.max_switch, mode)

    def start_scheduler(self):
        while self.running:
            self.run()
            sleep(self.delay)

    def stop_scheduler(self):
        self.running = False

    def start_scheduler_thread(self):
        self.running = True
        thread = Thread(target=self.start_scheduler)
        thread.start()