
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_directory, '..', 'items'))

# Importation of the file Rack.py
from Corridor import Corridor


#We test the method isConform of Rack 


#We try with a list of size 1 as a postion
corr = Corridor("name",[0], "m", "LEFT", [10,10,2], "cold")
if corr.isConform() :
    print("It doesn't work")
else:
    print("It works ! With a position of [0] it fails")

#We try with a rotation which doesn't exist
corr = Corridor("name",[0,0], "m", "penihogrbilubuimo",[10,10,2], "cold")
if corr.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With a rotation which doesn't exist)")

#We try with a rotation which doesn't exist
rack = Corridor("name",[0,0], "m", [10,21,45], [10,10,2], "cold")
if rack.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With a rotation which doesn't exist (a vector))")

#We try with the vector size which don't have the good shape
corr = Corridor("name",[0,0], "m", "LEFT", [0,1,0,1], "cold")
if corr.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With size.length > 3)")

#We try with the vector size which doesn't have the good shape
corr = Corridor("name",[0,0], "m", "LEFT", [0], "cold")
if corr.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With size.length < 2)")

#We try with a size negative
corr = Corridor("name",[0,0], "m", "LEFT", [0,-10,1], "cold")
if corr.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With a size <0)")

#We try with an unit which doesn't exist
corr = Corridor("name",[0,0], "y", "LEFT", [10,10,1], None)
if corr.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With y as unit)")

#We try with a temp which doesn't exist
corr = Corridor("name",[0,0], "y", "LEFT", [10,10,1], "Fucking hot!")
if corr.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With a wrong temp)")


#We try now with few examples of racks which should be conform
corr = Corridor("name",[0,10], "m", "LEFT", [0,10,10], "cold")
if corr.isConform() :
    print("It works 1")
else:
    print("It doesn't works ! ")

#We try now with few examples of racks which should be conform
rack = Corridor("name",[0,10], "m", [0,90,0], [0,10,10], " warm ")
if rack.isConform() :
    print("It works 2")
else:
    print("It doesn't works ! ")
