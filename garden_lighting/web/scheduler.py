from time import sleep
from threading import Thread


class DeviceScheduler:
    def __init__(self, device_group, delay):
        self.deviceGroup = device_group
        self.delay = delay

    # todo Configure scheduling

    def run(self):
        for device in self.deviceGroup.devices:
            if device.is_overdue():
                device.run_action()

    def start_scheduler(self):
        while True:
            self.run()
            sleep(self.delay)

    def start_scheduler_thread(self):
            thread = Thread(target=self.start_scheduler)
            thread.start()


