"""This module contains methods to create commands from parameters for sites"""

from tools import isColorConform,isOrientationConform,getParentName, isNameConform, isConform

SITE_PARAMETERS = ["name","orientation"]
CONFORMITY_CHECK = {"name" : isNameConform, "orientation" : isOrientationConform}

def createSite(parameters : dict) -> str:
    """Creates a site from given parameters"""
    if not isConform(parameters, SITE_PARAMETERS, CONFORMITY_CHECK):
        raise ValueError("The parameters given are invalid for a site")
        #this precondition is currently incomplete
    return "+si:" + "@".join([str(parameters[key]) for key in SITE_PARAMETERS])

def setName(oldName, newName : str) -> str:
    """Changes the name of an object, and ensures to keep it coherent"""
    oldNameParent = getParentName(oldName)
    newNameParent = getParentName(newName)
    if oldNameParent != newNameParent:
        raise ValueError("The new name is invalid because it does not respect the convention of the parent name")
    return "{}:name={}".format(oldName, newName)
    
def setOrientation(oldOrientation : str, newOrientation : str) -> str:
    """Changes the orientation of an object"""
    if not isOrientationConform(newOrientation):
        raise ValueError("The orientation is invalid")
    return "{}:orientation={}".format(oldOrientation, newOrientation)

def createAttribute(name : str, attributeName : str, attributeArgument) -> str:
    """Adds an attribute to an object with a given argument"""
    return "{}.{}={}".format(name, attributeName,attributeArgument)
    
def setAttribute(name : str, attributeName : str, attributeArgument) -> str:
    """Modifies an attribute of an object with a given argument"""
    return "{}:{}={}".format(name,attributeName,attributeArgument)
    
def setUsableColor(name : str, color : str) -> str:
    """Modifies the usable color of a site"""
    if not isColorConform(color):
        raise ValueError("The color format is invalid")
    return "{}:usableColor={}".format(name, color)
    
def setReservedColor(name : str, color : str) -> str:
    """Modifies the reserved color of a site"""
    if not isColorConform(color):
        raise ValueError("The color format is invalid")
    return "{}:reservedColor={}".format(name, color)
    
def setTechnicalColor(name : str, color : str) -> str:
    """Modifies the technical color of a site"""
    if not isColorConform(color):
        raise ValueError("The color format is invalid")
    return "{}:technicalColor={}".format(name, color)
        
if __name__ == "__main__":
    print(createSite({"name" : "P/BASIC", "orientation":"WSW"}))