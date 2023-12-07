import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_directory, '..', 'items'))

from Device import Device

device = Device(None, 10, 15, None, None,None)

if device.isConform():
    print("It doesn't work")
else:
    print("False : it needs a name")

device = Device("d1", 10, None, "slot", "template",None)

if device.isConform():
    print("It doesn't work")
else:
    print("False : it has a posU and a Slot")

device = Device("d1", None, 10, "slot", "template",None)

if device.isConform():
    print("It doesn't work")
else:
    print("False : it has a sizeU and a template")

device = Device("d1", 10, 10, None, "template","rear")

if device.isConform():
    print("It doesn't work")
else:
    print("False : it has a side while not having a slot")

device = Device("d1", None, None, "slot", "template"," evczevzar")

if device.isConform():
    print("It doesn't work")
else:
    print("False : this side doesn't exist")

device = Device("d1", None, 10, "slot", None," evczevzar")

if device.isConform():
    print("It doesn't work")
else:
    print("False : it has a slot but also a size")

device = Device("d1", None, None, "slot", "template","rear")

if device.isConform():
    print("It works")
else:
    print("It doesn't work")

