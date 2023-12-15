"""This module provides methods to create commands from parameters for rooms"""

import re
from tools import isListOfNumbers, isNameConform, isPositionConform, isRotationConform, isAxisOrientationConform, isSizeConform, isFloorUnitConform, isConform

ROOM_PARAMETERS = ["name","position","rotation","axisOrientation","size","floorUnit"]
CONFORMITY_CHECK = {"name" : isNameConform, "position" : isPositionConform, "rotation" : isRotationConform,
                    "axisOrientation" : isAxisOrientationConform, "size" : isSizeConform, "floorUnit" : isFloorUnitConform}

def createRoom(parameters : dict) -> str:
    """Creates a room from given parameters"""
    if not isConform(parameters, ROOM_PARAMETERS, CONFORMITY_CHECK):
        raise ValueError("The parameters given are invalid for a room")
    if "template" in parameters:
        raise NotImplementedError("This case has not been dealed with yet !")
    return "+bd:" + "@".join([str(parameters[key]) for key in ROOM_PARAMETERS])
    
def setName(self, newName : str) -> None:
    """If it is a complete new name, with the same parent name, then it is set as the new name. If the parent name is not the same,
    it is added to keep it coherent."""
    if (self.getParentName(newName) == self.getParentName()):
        self.name = newName
    else:
        self.name = "/".join([self.getParentName(),newName])

def setPosition(name : str, newPosition : list) -> str:
    """Changes the position of a room"""
    if not isPositionConform(newPosition):
        raise ValueError("The position is invalid")
    #I'm still not sure about the format of the command, for now I use a dot between the name and the attribute but it might be changed
    return "{}.position={}".format(name, newPosition)
     
def setRotation(name : str, newRotation : float) -> str:
    """Changes the rotation of a room"""
    if not isRotationConform(newRotation):
        raise ValueError("The rotation format is invalid")
    #I'm still not sure about the format of the command, for now I use a dot between the name and the attribute but it might be changed
    return "{}.rotation={}".format(name, newRotation)
    
def setSize(name : str, newSize : float) -> str:
    """Changes the size of a room"""
    if not isSizeConform(newSize):
        raise ValueError("The size format is invalid")
    #I'm still not sure about the format of the command, for now I use a dot between the name and the attribute but it might be changed
    return "{}.size={}".format(name, newSize)

def setAxisOrientation(name : str, newAxisOrientation : str) -> str:
    """Changes the axis orientation of a room"""
    if not isAxisOrientationConform(newAxisOrientation):
        raise ValueError("The axis orientation format is invalid")
    return "{}.axisOrientation={}".format(name,newAxisOrientation)
     
def setFloorUnit(name : str, newFloorUnit : str) -> None:
    """Changes the floor unit of a room"""
    if not isFloorUnitConform(newFloorUnit):
        raise ValueError("The floor unit format is invalid")
    return "{}.floorUnit={}".format(name,newFloorUnit)



if __name__ == "__main__":
    print(createRoom({"name" : "P/BASIC/ALPHA/R1", "position" : [2,6], "rotation" : 0, "axisOrientation" : "+x-y",
                      "size" : [5,8,2.4], "floorUnit" : "m"}))