import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_directory, '..', 'items'))

from Group import Group
from Rack import Rack
#from Room import Room

rack = Rack("name1",[0,10], "m", [0,90,0], None, "template")
rack1 = Rack("rm.name2",[0,10], "m", [0,90,0], None, "template")
print("Rack name", rack.name)
print("Rack1 name", rack1.name)
group = Group("gr1",rack, "tn.b.r.A01")
print(group.components)
group.addComponent(rack1)
print(group.components)