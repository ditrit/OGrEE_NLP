import json
import re

from tools import *
from solver.Rack import *
from solver.Room import *

def createRoomFromTemplate(name :str, position : list, rotation : int, filename : str) -> str:
    """Creates a Room instance from a json file with a template"""
    filename = "demo/rooms/" + filename + ".json"
    with open(filename, "r") as room:
        roomDescription = json.load(room)
    r = roomDescription
    return r

def readFileOCLI(filename : str, searched : str) -> (int,str):
    """Reads an OCLI file and returns a string"""
    k = 0
    with open(filename, "r") as commands:
        line = commands.readline()
        while line and line.find(searched) == -1:
            line = commands.readline()
            k += 1
        if not line:
            raise ValueError("There is no element named {} in {}".format(searched,filename))
    return k, line

def readCommandOCLI(command : str) -> list:
    """Reads an OCLI command and converts it"""
    #a command is always separated from its paramaters by a semicolon
    parts = command.split(":")
    typeOfCommand = parts[0]
    parameters = parts[1].split("@")
    return typeOfCommand, parameters
    
def executeCommandOCLI(command : str, parameters : list):
    #return TERRORIST[command](parameters)
    pass

def terrorist(parameters : list):
    reifiedParameters = []
    for parameter in parameters:
        try:

            reifiedParameters.append(json.loads(parameter))
        except json.decoder.JSONDecodeError:
            reifiedParameters.append(parameter)
    return reifiedParameters


def createRoom(parameters : list):
    """Creates a room from given parameters"""
    if len(parameters) != 4:
        raise TypeError("An incorrect number of arguments was given")
    name = parameters[0]
    position = json.loads(parameters[1])
    rotation = json.loads(parameters[2])
    template = json.loads(parameters[3])
    return [name,position,rotation,template]

def getTypeFromName(filename : str, name : str):
    """This function is supposed to return the type of an object thanks to its name, but it might be ineffective
    in case a name is used for different objects"""
    k, line = readFileOCLI(filename, name)
    typeOfCommand, parameters = readCommandOCLI(line)
    return TYPES[typeOfCommand] if typeOfCommand in TYPES.keys() else ""

def getAllNames(file_name : str) -> list:
    """Returns all the names present in the ocli files"""
    with open(file_name, "r") as file:
        text = file.read()
        pattern = re.compile(r'^[+].*', re.MULTILINE)
        commands = pattern.findall(text)
    names = [re.split('@',re.split(':',c)[1])[0] for c in commands]
    return names

def objects_in(obj : str, file_name : str) -> list:
    """Given an object 'obj', returns every object that are contained in this one"""
    objects = []
    names = getAllNames(file_name)
    level = nbOccurences('/',obj)
    for name in names:
        if(nbOccurences('/',name)==level+1 and re.search(obj,name)):
            objects.append(name)
    return objects

def getParametersFromName(name : str, file_name : str) -> dict:
    """Get the parameters of an object from his name"""
    nbSlash = nbOccurences('/',name)
    with open(file_name, "r") as file:
        text = file.read()
        pattern = re.compile(fr'.*{re.escape(name)}.*', re.MULTILINE)
        commands = pattern.findall(text)
        
    copy_cmds = [cmd for cmd in commands if nbOccurences('/',cmd)==nbSlash]
    object_type = getTypeFromName(file_name,name)
    creation_cmd = copy_cmds[0] #we suppose that the commaand to create an object is always the first command to appear
    commandOcli = readCommandOCLI(creation_cmd)
    if(len(commandOcli) > 1):
        params = terrorist(readCommandOCLI(creation_cmd)[1])
    else:
        params = terrorist(readCommandOCLI(creation_cmd))
    match object_type:
        case "Building":
            if(hasTemplate(object_type,creation_cmd)):
                params[3] = json.loads(params[3] + ".json")
            if(len(copy_cmds)>1):
                modifications = search_modifs(copy_cmds[1:])
        case "Room" :
            if(hasTemplate(object_type,creation_cmd)):
                params[3] = json.loads(params[3] + ".json")
        case "Site" :
            return params
        case "Rack" :
            if(hasTemplate(object_type,creation_cmd)):
                params[4] = json.loads(params[4] + ".json")
        case _:
            params = []
    return params

def search_modifs(commands : list) -> list:
    """Search the modification made on a object"""
    return [(re.split("=",re.split(":",command)[1])[0],re.split("=",re.split(":",command)[1])[1]) for command in commands]


def modifyAttributesSelection(names : list, attributeName : str, attributeArgument : str) -> str:
    selection = "={" + ",".join(names) + "}" + "\n"
    return selection + "selection.{}={}".format(attributeName, attributeArgument)  
    
def getAllElementParameters(room_name : str, path : str) -> list:
    entity_in_room = objects_in('/P/BASIC/A/R1',path)
    list_entity_parameter =[]
    for entity in entity_in_room:
        list_param = getParametersFromName(entity,path)
        list_entity_parameter.append(list_param)
    return list_entity_parameter

def createListObject(room_name : str, path : str) -> list:
    list_entity = getAllElementParameters(room_name, path)
    list_object = []
    for entity in list_entity:
        #All the entities are Racks so we should always have 4 parameters
        if len(entity) == 5:
            if type(entity[4]) !=str:
                new_object = Rack(entity[0],entity[1], entity[2],entity[3],entity[4])
            else:
                new_object = Rack.createFromTemplate(entity[0],entity[1], entity[2],entity[3],entity[4])
        list_object.append(new_object)
    return list_object






TYPES = {"+ro" : "Room", "+si" : "Site", "+bd" : "Building", "+room" : "Room", "+site" : "Site", "+building" : "Building", "+rk" : "Rack", "+rack" : "Rack", "+gr" : "Group", "+corridor" : "Corridor", "+co" : "Corridor"}    
    
# TERRORIST = {"+ro" : createRoomFromCommand, "+si" : createSiteFromCommand, "+bd" : createBuidlingFromCommand}

if __name__ == "__main__":
    testCommand = "+bd:/P/BASIC/A@[0,0]@0@[24,30,1]"
    #print(readFileOCLI("demo/simu1.ocli", "/P/BASIC/A/R1"))
    # print(getTypeFromName("demo/simu1.ocli","/P/BASIC"))
  #  path = "C:\\Users\\lemoi\\Documents\\Cours\\Commande_Entreprise\\GitHub\\OGrEE_NLP\\DEMO.BASIC.ocli"
    path = r"C:\Users\Admin\Desktop\dossier\DEMO_BASIC.ocli"
    commands = getAllNames(path)
    # for command in commands:
    #     print("objet : ",command,"\t| parent : ", getParentName(command))
    objects = objects_in('/P/BASIC/A/R1',path)
    # for obj in objects:
    #     print(obj)
    cmds = getParametersFromName('/P/BASIC/A/R1/B07',path)
    print(getAllElementParameters('/P/BASIC/A/R1',path))
   # for cmd in cmds :
   #     print(cmd)