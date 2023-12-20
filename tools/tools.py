"""This module contains static tools for the different classes"""
import re
import json
from textblob import TextBlob, Word


def create(typeOfObject : str, parameters : dict) -> str:
    """Creates an object from given parameters"""
    if not isConform(parameters):
        raise ValueError("The parameters given are invalid for the object of type :" + typeOfObject)
    return "+{}:".format(typeOfObject) + "@".join([str(parameters[key]) for key in parameters.keys()])

def terrorist(parameters : list):
    reifiedParameters = []
    for parameter in parameters:
        try:
            reifiedParameters.append(json.loads(parameter))
        except json.decoder.JSONDecodeError:
            reifiedParameters.append(parameter)
    return reifiedParameters

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
def nbOccurences(item : str, text : str) -> int:
    """Count how many times item appears in text"""
    return len(re.findall(item,text))

def transformStringParameters(param:str) -> list:
    """This function transform param in a list or a number if it is possible"""
    numbers = re.findall(r'-?\d+(?:\.\d+)?', param)
    if re.findall(r'[A-Za-z]+',param):
        numbers = []
    if len(numbers) == 1:
        return int(numbers[0])
    if len(numbers)>1:
        return [int(c) for c in numbers]
    return param

def getParametersFromTemplate(name : str) -> dict:
    """Get the parameters from a template file"""
    with open(name + ".json",'r') as template:
        content = json.loads(template)
    return content

def number_of_parameters(command : str):
    """Returns the number of parameters in a command"""
    parameters = re.split(":",command)[1]
    return len(re.split('@',parameters))

def getParentName(completeName : str) -> str:
    """Returns the name of the parent object. It reverses the name, then splits it using dot as separator, and only
    gets the first part of the name, which is put back in order."""
    return "".join(reversed(completeName)).split("/",1)[-1][::-1]

def correctorSpellingMistakes(text : str) -> str:
    sentence = re.findall(r'[^ ]+',text)
    sentence = [transformStringParameters(word) for word in sentence]
    corrected_word = []
    for word in sentence:
        #The word in cap are name
        if type(word) == str and re.findall(r'[A-Za-z0-1][a-z]+$',word) !=[]:
            corrected_word.append(str(TextBlob(word).correct()))
        else:
            corrected_word.append(word)
    
    string = ""
    for word in corrected_word:
        string+= str(word) + " "
    return string

def convertPrefix(value : float, unit : str) -> float:
    #Return this unit in the international unit system
    if len(unit) == 1:
        return value
    prefix = unit[0]
    match prefix:
        case "m":
            return value/1000
        case "c":
            return value/100 
        case "d":
            return value/10
        case _:
            raise Exception("Unit not reconised")

def convertUnity(valueChanged : int, unityD : str, unityChanged : str) -> float:
    if unityD[len(unityD)-1] == unityChanged[len(unityChanged)-1]:
        #They are in the same unity
        return convertPrefix(valueChanged, unityD)
    else:
        if unityD[len(unityD)-1] == 'm' and unityChanged[len(unityChanged)-1] == 'f':
            return convertPrefix(convertPrefix(valueChanged, unityChanged)/3.281,unityD)
        elif unityD[len(unityD)-1] == 'f' and unityChanged[len(unityChanged)-1] == 'm':
            return convertPrefix(convertPrefix(valueChanged, unityChanged)*3.281,unityD)
        else:
            #Don't know how to convert the tilde
            return valueChanged


#endregion

CONFORMITY_CHECK = {"name" : isNameConform, "orientation" : isOrientationConform, "position" : isPositionConform,
                    "rotation" : isRotationConform, "size" : isSizeConform, "axisOrientation" : isAxisOrientationConform,
                    "floorUnit" : isFloorUnitConform, "color" : isColorConform}

if __name__ == "__main__":
    print(convertUnity(10,"f", "cm"))
#     print(create("site",{"name" : "P/BASIC", "orientation":"WSW"}))
#     print(setAttribute("P/BASIC","position","WSW"))

    # print(correctorSpellingMistakes("I em curently tetsing Textblog [5412,1254,4521] 9 FUCKER"))
    # print(correctorSpellingMistakes("Plase at the psitio [0,10,20] the rack caleleed R1"))


