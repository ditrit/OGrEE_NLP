"""This module contains static tools for the different classes"""
from ctypes.wintypes import BOOL
import re


def isListOfNumbers(lst : list) -> bool:
    """Verifies that the list given in argument only contains numbers"""
    n = len(lst)
    k = 0
    verified = True
    while verified and k < n:
        verified = verified and (type(lst[k]) in [float, int])
        k += 1
    return verified

def isConform(parameters : dict, standardParameters : list, conformityCheck : dict) -> bool:
    """Verifies that the parameters given are conform to a standard given by standardParameters and conformityCheck"""
    print("The given parameters :")
    print([conformityCheck[attribute](parameters[attribute]) for attribute in standardParameters])
    print(all([conformityCheck[attribute](parameters[attribute]) for attribute in standardParameters]))
    return all([conformityCheck[attribute](parameters[attribute]) for attribute in standardParameters])

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
    
def isSizeConform(size : list) -> bool:
    """Verifies that the list given in argument represents a size"""
    return len(size) == 3 and isListOfNumbers(size)

def isAxisOrientationConform(axis : str) -> bool:
    """Verifies that the axis orientation is conform"""
    return bool(re.compile(r"[+-]x[+-]y").match(axis))
    
def isFloorUnitConform(floorUnit : str) -> bool:
    """Verifies that the floor unit is conform"""
    return floorUnit.replace(" ","") in ["t","f","m"]

def isUnitConform(unit : str) ->bool:
    """Verifies that the floor unit is conform"""
    return floorUnit.replace(" ","") in ["t","f","m","u"]

def isColorConform(color : str) -> bool:
    """Verifies that the string given in argument is an hexadecimal color"""
    return bool(re.compile(r"[0-9A-F]{6}").match(color))

def isOrientationConform(orientation : str) -> bool:
    """Verifies that the string given in argument is a valid orientation"""
    return orientation in ["N","S","W","E","NW","NE","SW","SE","ESE"
                           "WNW","NNW","NNE","ENE","WSW","SSW","SSE"]

def parametersToString(parameters : list) -> list:
    """Returns a list with the type of the parameters in the list changed to string"""
    return [str(parameter) for parameter in parameters]

def getParentName(completeName : str) -> str:
    """Returns the name of the parent object. It reverses the name, then splits it using dot as separator, and only
    gets the first part of the name, which is put back in order."""
    return "".join(reversed(completeName)).split("/",1)[-1][::-1]

if __name__ == "__main__":
    #print(parametersToString(["name", [3,5], 54, "WSW"]))
    #print(isAxisOrientationConform("+x+y"))
    print(getParentName("P/BASIC/ALPHA/R1/B0"))


