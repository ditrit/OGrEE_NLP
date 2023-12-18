import json
import re
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_directory, '..', 'tools'))

from tools import nbOccurences, terrorist
from Rack import *
from Room import *
from Corridor import *

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

def hasTemplate(obtype : str, command : str) -> bool:
    """Returns true if the given command uses a template"""
    tuple_command = readCommandOCLI(command)
    params = terrorist(tuple_command[1])
    match obtype:
        case "Building":
            if(type(params[3])==str):
                return True
            else : return False
        case "Room" :
            if(type(params[3])==str):
                return True
            else : return False
        case "Site" :
            return False
        case "Rack" :
            if(type(params[4])==str):
                return True
            else : return False

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
    if type(commandOcli) ==tuple:
        params = terrorist(commandOcli[1])
    else:
        Exception("ReadCommandOcli should return a tuple")
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
            return object_type,params
        case "Rack" :
            if(hasTemplate(object_type,creation_cmd)):
                params[4] = json.loads(params[4] + ".json")
        case "Corridor":
            return object_type, params
        case "Pillar":
            return object_type, params
        case "Separator":
            return object_type,params
        case _:
            params = []
    return object_type ,params

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
        command_ocli , list_param = getParametersFromName(entity,path)
        list_entity_parameter.append((command_ocli,list_param))
    return list_entity_parameter

def createListObject(room_name : str, path : str) -> list:
    list_entity = getAllElementParameters(room_name, path)
    object_type, room = getParametersFromName(room_name, path)
    #We create the object room
    #A room have at least 4 parameters
    if len(room) > 3:
            if type(room[3]) != str:
                obj_room = Room(room[0],room[1],room[2],room[3])
            else:
                obj_room = Room.create_from_template(room[0],room[1],room[2],room[3])
    else:
        raise Exception("A room should have at least 4 parameters")
    list_object = []
    for entity_command_ocli,entity_list in list_entity:
        #All the entities are Racks so we should always have 5 parameters
        print(entity_command_ocli,entity_list)
        match entity_command_ocli:
            case "Rack":
                if len(entity_list) == 5:
                    if type(entity_list[4]) !=str:
                        new_object = Rack(entity_list[0],entity_list[1], entity_list[2],entity_list[3],entity_list[4])
                    else:
                        new_object = Rack.createFromTemplate(entity_list[0],entity_list[1], entity_list[2],entity_list[3],entity_list[4])
                    list_object.append(new_object)
                else:
                    raise Exception( "A rack should have 5 arguments")
            case "Corridor":
                if len(entity_list) == 6:
                        new_object = Corridor(entity_list[0],entity_list[1], entity_list[2],entity_list[3],entity_list[4],entity_list[5])
                        list_object.append(new_object)       
                else:
                    raise Exception( "A corridor should have 6 arguments")
    #Commands to create a separator and a pillar are a bit special so we have to treat them separetly
    list_pillars_sepa = getAllParametersSeparatorsPillarsInRoom(room_name, path)
    print(list_pillars_sepa)
    for command in list_pillars_sepa:
        entity_type = TYPES[command[0]] if command[0] in TYPES.keys() else ""
        parameters = terrorist(command[1])
        match entity_type:
            case "Pillar":
                if len(parameters) ==4:
                    obj_room.addPillar(parameters[0],parameters[1],parameters[2],parameters[3])
                else:
                    raise Exception("A pillar should have 4 parameters")
            case "Separator":
                if len(parameters) ==4:
                    obj_room.addSeparator(parameters[0],parameters[1],parameters[2],parameters[3])
                else:
                    raise Exception("A separator should have 4 parameters")
    return obj_room, list_object


def getNameSeparator(name :str) -> str:
    return texte.split('=')[1]

def getAllSeparatorsPillars(path : str) -> list:
    """Returns all the pillars and Separators present in the ocli files"""
    with open(path, "r") as file:
        text = file.read()
        pattern = re.compile(r'.*separators[+]=.*|.*pillars[+]=.*', re.MULTILINE)
        commands = pattern.findall(text)
    #names = [re.split('@',re.split(':',c)[1])[0] for c in commands]
    return commands

def getAllSeparatorsPillarsInRoom(room : str, path : str) -> list:
    """Return all the pillars and separators in the room room"""
    commands = getAllSeparatorsPillars(path)
    in_room = []
    for command in commands:
        name_room = re.split(':',command)[0]
        if re.search(name_room,room):
                in_room.append(command)
    return in_room

def getAllParametersSeparatorsPillarsInRoom(room : str, path : str) -> list:
    """Return all the parameters of the pillars and separators in the room room"""
    commands = getAllSeparatorsPillarsInRoom(room, path)
    in_room = []
    for command in commands:
        type_command, params = re.split('=',command)[0], re.split('=',command)[1]
        list_param = []
        for parameter in re.split('@',params):
            list_param.append(parameter)
        in_room.append((re.split(':',type_command)[1],list_param))
    return in_room



TYPES = {"+ro" : "Room", "+si" : "Site", "+bd" : "Building", "+room" : "Room", "+site" : "Site", "+building" : "Building", "+rk" : "Rack", "+rack" : "Rack",
 "+gr" : "Group", "+corridor" : "Corridor", "+co" : "Corridor", "pillars+" : "Pillar", "separators+" : "Separator" }    
    
# TERRORIST = {"+ro" : createRoomFromCommand, "+si" : createSiteFromCommand, "+bd" : createBuidlingFromCommand}

if __name__ == "__main__":
    testCommand = "+bd:/P/BASIC/A@[0,0]@0@[24,30,1]"
    testCommand2 = "/P/BASIC/A/R1:separator+=SEPA1@[0,51]@[51,87]@plain"
    #print(readFileOCLI("demo/simu1.ocli", "/P/BASIC/A/R1"))
    # print(getTypeFromName("demo/simu1.ocli","/P/BASIC"))
  #  path = "C:\\Users\\lemoi\\Documents\\Cours\\Commande_Entreprise\\GitHub\\OGrEE_NLP\\DEMO.BASIC.ocli"
    path = r"C:\Users\Admin\Desktop\dossier\DEMO_BASIC.ocli"
    #print("getName : ",getTypeFromName(path,"SEPA1"))
    #print(getAllParametersSeparatorsPillarsInRoom("/P/BASIC/A/R1",path))
    #print(getAllSeparatorsPillars(path))
    #commands = getAllNames(path)
    #print(commands)
    # for command in commands:
    #     print("objet : ",command,"\t| parent : ", getParentName(command))
    #objects = objects_in('/P/BASIC/A/R1',path)
    #print(objects)
    #for obj in objects:
     #    print(obj)
   # cmds = getParametersFromName('/P/BASIC/A/R1/B07',path)
   # print(getAllElementParameters('/P/BASIC/A/R1',path))
    room, list_object_Ocli = createListObject('/P/BASIC/A/R1',path)
    print(list_object_Ocli)
    print("Separators : ", room.separators)
    print("Pillar : ", room.pillars) 
   # for cmd in cmds :
   #     print(cmd)