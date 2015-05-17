from unittest import TestCase
from datetime import timedelta
from garden_lighting.light_control import LightControl


class TestLightScheduler(TestCase):
    def setUp(self):
        self.scheduler = LightControl(timedelta(seconds=2), 1, None)

    def test_can(self):
        self.assertTrue(self.scheduler.can_switch(0))
        self.scheduler.update_switched(0)
        self.assertFalse(self.scheduler.can_switch(0))
