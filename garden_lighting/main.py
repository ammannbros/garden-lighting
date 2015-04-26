#!/usr/bin/python

#Remote Debug configuration
import sys
sys.path.append('/home/pi/garden-lighting/garden_lighting/MCP23017/pycharm-debug.egg')
import pydevd
pydevd.settrace('holziVirtualBox', port=12000, stdoutToServer=True, stderrToServer=True)

from lightControl import LightControl

ControlUnit  = LightControl()

ControlUnit.init()
ControlUnit.set_multiple_lights(1 , (8,9,10,11))