__author__ = 'holzi'
from MCP23017 import MCP23017


Chip2 = MCP23017(0x21)

Chip2.initDevice()
status = Chip2.set_io_direction_port_a(0x00)   #PortA is completeley Output
print(status)
#Do a write check
status = Chip2.write_byte_port_a(0x0A)
print(status)

if Chip2.read_byte_port_a() == 0x0A:
    print("PASS")
else:
    print("FAIL ")
