"""This module contains static tools for the different classes"""

import re

def create(typeOfObject : str, parameters : dict) -> str:
    """Creates an object from given parameters"""
    if not isConform(parameters):
        raise ValueError("The parameters given are invalid for the object of type :" + typeOfObject)
    return "+{}:".format(typeOfObject) + "@".join([str(parameters[key]) for key in parameters.keys()])

def delete(typeOfObject : str, parameters : dict) -> str:
    """Deletes an object from given parameters
    We consider that the object exist with this name"""
    return "-{}".format(parameters["name"])

def setName(oldName, newName : str) -> str:
    """Changes the name of an object, and ensures to keep it coherent"""
    oldNameParent = getParentName(oldName)
    newNameParent = getParentName(newName)
    if oldNameParent != newNameParent:
        raise ValueError("The new name is invalid because it does not respect the convention of the parent name")
    return "{}:name={}".format(oldName, newName)

def setAttribute(name : str, attributeName : str, attributeArgument) -> str:
    """Modifies an attribute of an object with a given argument"""
    if attributeName in CONFORMITY_CHECK:
        if not CONFORMITY_CHECK[attributeName](attributeArgument):
            raise ValueError("The new {} is invalid because the value {} is incorrect".format(attributeName,attributeArgument))
    return "{}:{}={}".format(name,attributeName,attributeArgument)

def createAttribute(name : str, attributeName : str, attributeArgument) -> str:
    """Adds an attribute to an object with a given argument"""
    return "{}.{}={}".format(name, attributeName,attributeArgument)

def isConform(parameters : dict) -> bool:
    """Verifies that the parameters given are conform thanks to multiple verification
    functions, which are called if the parameter is in the parameters"""
    if (CONFORMITY_CHECK == {}):
        raise NotImplementedError("There are no implemented conformity checks")
    return all([CONFORMITY_CHECK[attribute](parameters[attribute]) for attribute in parameters.keys()])

#region:Tests
def isListOfNumbers(lst : list) -> bool:
    """Verifies that the list given in argument only contains numbers"""
    n = len(lst)
    k = 0
    verified = True
    while verified and k < n:
        verified = verified and (type(lst[k]) in [float, int])
        k += 1
    return verified

def isNameConform(name : str) -> bool:
    """Verifies that the argument is a string. This function will potentially be changed if there are more
    specifications for the name"""
    return type(name) == str

def isPositionConform(position : list) -> bool:
    """Verifies that the list given in argument represents a position"""
    return len(position) == 2 and isListOfNumbers(position)

def isPositionRackConform(position : list) -> bool:
    """Verifies that the list given in argument represents a position for a Rack"""
    return (len(position) == 2 or len(position) == 3) and isListOfNumbers(position)

def isRotationConform(rotation : float) -> bool:
    """Verifies that the argument is a number"""
    return type(rotation) in [float,int]

def isRotationRackConform(rotation : list) -> bool:
    """Verifies that the argument is a number"""
    return type(rotation) == list and len(rotation) == 3 and isListOfNumbers(rotation)


def isSizeConform(size : list) -> bool:
    """Verifies that the list given in argument represents a size"""
    return len(size) == 3 and isListOfNumbers(size)

def isAxisOrientationConform(axis : str) -> bool:
    """Verifies that the axis orientation is conform"""
    return bool(re.compile(r"[+-]x[+-]y").match(axis))
    
def isFloorUnitConform(floorUnit : str) -> bool:
    """Verifies that the floor unit is conform"""
    return floorUnit.replace(" ","") in ["t","f","m","u"]

def isUnitConform(floorUnit : str) ->bool:
    """Verifies that the floor unit is conform"""
    return floorUnit.replace(" ","") in ["t","f","m","u"]

def isColorConform(color : str) -> bool:
    """Verifies that the string given in argument is an hexadecimal color"""
    return bool(re.compile(r"[0-9A-F]{6}").match(color))

def isOrientationConform(orientation : str) -> bool:
    """Verifies that the string given in argument is a valid orientation"""
    return orientation in ["N","S","W","E","NW","NE","SW","SE","ESE"
                           "WNW","NNW","NNE","ENE","WSW","SSW","SSE"]

def isSlotConform(slot : str) -> bool:
    return type(slot) == str

def isSideConform(side : str) -> bool:
    return side in ["front", "rear", "frontflipped", "rearflipped"]

def isTemperatureConform(temperature : str) -> bool:
    return temperature in ["cold", "warm"]

#endregion

#region:Helpers
def parametersToString(parameters : list) -> list:
    """Returns a list with the type of the parameters in the list changed to string"""
    return [str(parameter) for parameter in parameters]

def getParentName(completeName : str) -> str:
    """Returns the name of the parent object. It reverses the name, then splits it using dot as separator, and only
    gets the first part of the name, which is put back in order."""
    return "".join(reversed(completeName)).split("/",1)[-1][::-1]
#endregion


CONFORMITY_CHECK = {"name" : isNameConform, "orientation" : isOrientationConform, "position" : isPositionConform,
                    "rotation" : isRotationConform, "size" : isSizeConform, "axisOrientation" : isAxisOrientationConform,
                    "floorUnit" : isFloorUnitConform, "color" : isColorConform}

if __name__ == "__main__":
    print(create("site",{"name" : "P/BASIC", "orientation":"WSW"}))
    print(setAttribute("P/BASIC","position","WSW"))


