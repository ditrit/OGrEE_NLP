
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_directory, '..', 'items'))

# Importation of the file Rack.py
from Rack import Rack

rack = Rack([0,0], "m", "LEFT", None, "nomtemplate")

#We test the method isConform of Rack 

#We try with a size and a template --> Should return False
rack = Rack([0,0], "m", "LEFT", [1,2,3], "nomtemplate")
if rack.isConform() :
    print("It doesn't work")
else:
    print("It works ! (Template & Size)")

#We try with neither a size neitheir a template
rack = Rack([0,0], "m", "LEFT", None, None)
if rack.isConform() :
    print("It doesn't work")
else:
    print("It works ! Without Template & Size")

#We try with a list of size 1 as a postion
rack = Rack([0], "m", "LEFT", None, "nom")
if rack.isConform() :
    print("It doesn't work")
else:
    print("It works ! With a position of [0] it fails")

#We try with a rotation which doesn't exist
rack = Rack([0,0], "m", "penihogrbilubuimo", None, "nom")
if rack.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With a rotation which doesn't exist)")

#We try with a rotation which doesn't exist
rack = Rack([0,0], "m", [10,21,45], None, "nom")
if rack.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With a rotation which doesn't exist (a vector))")

#We try with the vector size which don't have the good shape
rack = Rack([0,0], "m", "LEFT", [0,1,0,1], None)
if rack.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With size.length > 3)")

#We try with the vector size which doesn't have the good shape
rack = Rack([0,0], "m", "LEFT", [0], None)
if rack.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With size.length < 2)")

#We try with a size negative
rack = Rack([0,0], "m", "LEFT", [0,-10,1], None)
if rack.isConform() :
    print("It doesn't work")
else:
    print("It works ! (With a size <0)")

#We try now with few examples of racks which should be conform
rack = Rack([0,10], "m", "LEFT", [0,10,10], None)
if rack.isConform() :
    print("It works 1")
else:
    print("It doesn't works ! ")

#We try now with few examples of racks which should be conform
rack = Rack([0,10], "m", [0,90,0], [0,10,10], None)
if rack.isConform() :
    print("It works 2")
else:
    print("It doesn't works ! ")

#We try now with few examples of racks which should be conform
rack = Rack([0,10], "m", [0,90,0], None, "template")
if rack.isConform() :
    print("It works 3")
else:
    print("It doesn't works ! ")