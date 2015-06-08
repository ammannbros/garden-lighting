class LightControl:
    def __init__(self, max_switch, delay, logger, a_address, a_rst_pin, b_address, b_rst_pin):
        pass

    def run(self):
        pass

    def init(self):
        pass

    def can_switch(self, light):
        pass

    def update_switched(self, light):
        pass

    def schedule_switch(self, light, mode, time):
        pass

    def get_lights(self, state):
        return []

    def set_lights(self, state, lights):
        pass