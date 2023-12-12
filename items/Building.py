"""This module contains methods to create commands from parameters for buildings"""

from items.tools import isConform, isNameConform, isPositionConform, isRotationConform, isSizeConform
from tools import isListOfNumbers, getParentName

BUILDING_PARAMETERS = ["name","position","rotation","size"]
CONFORMITY_CHECK = {"name" : isNameConform, "position" : isPositionConform, "rotation" : isRotationConform, "size" : isSizeConform}

def createBuilding(parameters : dict) -> str:
    """Creates a building from given parameters"""
    if isConform(parameters, BUILDING_PARAMETERS, CONFORMITY_CHECK):
        raise ValueError("The parameters given are invalid for a building")
    return "+bd:" + "@".join([str(parameters[key]) for key in BUILDING_PARAMETERS])

def setName(oldName, newName : str) -> str:
    """Changes the name of an object, and ensures to keep it coherent"""
    if getParentName(oldName) != getParentName(newName) or not isNameConform(newName):
        raise ValueError("The new name is invalid because it does not respect the convention of the parent name")
    return "{}:name={}".format(oldName, newName)

def setPosition(name : str, newPosition : list) -> str:
    """Changes the position of a building"""
    if not isPositionConform(newPosition):
        raise ValueError("The position is invalid")
    #I'm still not sure about the format of the command, for now I use a dot between the name and the attribute but it might be changed
    return "{}.position={}".format(name, newPosition)
     
def setRotation(name : str, newRotation : float) -> str:
    """Changes the rotation of a building"""
    if not isRotationConform(newRotation):
        raise ValueError("The rotation format is invalid")
    #I'm still not sure about the format of the command, for now I use a dot between the name and the attribute but it might be changed
    return "{}.rotation={}".format(name, newRotation)
    
def setSize(name : str, newSize : float) -> str:
    """Changes the size of a building"""
    if not isSizeConform(newSize):
        raise ValueError("The size format is invalid")
    #I'm still not sure about the format of the command, for now I use a dot between the name and the attribute but it might be changed
    return "{}.size={}".format(name, newSize)