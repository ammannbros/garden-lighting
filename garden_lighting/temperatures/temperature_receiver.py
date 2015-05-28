import time

import garden_lighting.temperatures.virtual_wire as virtual_wire
import pigpio


class TemperatureReceiver:
    def __init__(self, rx_pin, bps):
        self.senders = {}

        self.rx = virtual_wire.rx(pigpio.pi(), rx_pin, bps)

    def start(self):
        while True:
            if not self.rx.ready():
                time.sleep(0.1)
            else:
                msg = self.rx.get()
                id = msg[0]
                devices = msg[1]

                if id not in self.senders:
                    self.senders[id] = TemperatureSender()

                sender = self.senders[id]

                for i in range(2, 2 + devices, 2):
                    sender.temperatures[i - 2] = (msg[i] | msg[i + 1] << 8)
                    # print("Device Temp.: %d" % (msg[i] | msg[i + 1] << 8))

    def get_sender(self, sender):
        return self.senders[sender]

    def senders(self):
        return len(self.senders)

class TemperatureSender:
    def __init__(self):
        self.temperatures = {}

    def get_temperature(self, device):
        return self.temperatures[device]

    def temperatures(self):
        return len(self.temperatures)




