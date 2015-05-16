from unittest import TestCase
from datetime import timedelta
from garden_lighting.light_scheduler import LightScheduler


class TestLightScheduler(TestCase):
    def setUp(self):
        self.scheduler = LightScheduler(timedelta(seconds=2), 1)

    def test_can(self):
        self.assertTrue(self.scheduler.can_switch(0))
        self.scheduler.update_switched(0)
        self.assertFalse(self.scheduler.can_switch(0))

    def test_schedule(self):
        self.scheduler.start_scheduler_thread()

        self.scheduler.schedule_switch(3, 1)
