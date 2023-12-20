import json
import re
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_directory, '..', 'tools'))

from tools import nbOccurences, terrorist, transformStringParameters, convertUnity, getParametersFromTemplate
from Rack import *
from Room import *
from Corridor import *
import numpy as np 

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
    entity_in_room = objects_in(room_name,path)
    list_entity_parameter =[]
    for entity in entity_in_room:
        command_ocli , list_param = getParametersFromName(entity,path)
        list_entity_parameter.append((command_ocli,list_param))
    return list_entity_parameter

def createListObject(room_name : str, path : str) -> list:
    list_entity = getAllElementParameters(room_name, path)
    #We get the room
    object_type, room = getParametersFromName(room_name, path)
    list_entity_changed = (listeItemInRoomToChange(room_name,path,objects_in(room_name,path)))
    liste_entity_correct = correctEntityParameters(room_name,path,list_entity_changed)
    #We create the object room
    #A room have at least 4 parameters
    if len(room) > 3:
            list_changes_room = {}
            #We seek all the changes made for the room
            for elem, parameter in liste_entity_correct:
                if elem == room[0]:
                    list_changes_room[parameter[0]] = parameter[1]
            position = list_changes_room['pos'] if 'pos' in list_changes_room.keys() else room[1]
            rotation = list_changes_room['rotation'] if 'rotation' in list_changes_room.keys() else room[2]
            size = list_changes_room['size'] if 'size' in list_changes_room.keys() else room[3]
            technical = list_changes_room['technical'] if 'technical' in list_changes_room.keys() else [0,0,0,0]
            reserved = list_changes_room['reserved'] if 'reserved' in list_changes_room.keys() else [0,0,0,0]
            if type(room[3]) != str:
                obj_room = Room(room[0],position,rotation,size,reserved,technical)
            else:
                template = list_changes_room['template'] if 'template' in list_changes_room.keys() else room[3]
                obj_room = Room.create_from_template(room[0],position,rotation,template,reserved,technical)
    else:
        raise Exception("A room should have at least 4 parameters")
    list_object = []
    for entity_command_ocli,entity_list in list_entity:
        #All the entities are Racks so we should always have 5 parameters
        list_changes_room = {}
        #We seek all the changes made for the room
        for elem, parameter in liste_entity_correct:
                if len(entity_list) > 0 and elem == entity_list[0]:
                    list_changes_room[parameter[0]] = parameter[1]
        match entity_command_ocli:
            case "Rack":
                if len(entity_list) == 5:
                    position = list_changes_room['pos'] if 'pos' in list_changes_room.keys() else entity_list[1]
                    unit = list_changes_room['unit'] if 'unit' in list_changes_room.keys() else entity_list[1]
                    rotation = list_changes_room['rotation'] if 'rotation' in list_changes_room.keys() else entity_list[3]
                    size = list_changes_room['size'] if 'size' in list_changes_room.keys() else entity_list[4]
                    if type(entity_list[4]) !=str:
                        new_object = Rack(entity_list[0],position, unit,rotation,size)
                    else:
                        template = list_changes_room['template'] if 'template' in list_changes_room.keys() else entity_list[4]
                        new_object = Rack.createFromTemplate(entity_list[0],position, unit,rotation,template)
                    list_object.append(new_object)
                else:
                    raise Exception( "A rack should have 5 arguments")
            case "Corridor":
                if len(entity_list) == 6:
                    position = list_changes_room['pos'] if 'pos' in list_changes_room.keys() else entity_list[1]
                    unit = list_changes_room['unit'] if 'unit' in list_changes_room.keys() else entity_list[1]
                    rotation = list_changes_room['rotation'] if 'rotation' in list_changes_room.keys() else entity_list[3]
                    size = list_changes_room['size'] if 'size' in list_changes_room.keys() else entity_list[4]
                    new_object = Corridor(entity_list[0],position,unit,rotation,size,entity_list[5])
                    list_object.append(new_object)       
                else:
                    raise Exception( "A corridor should have 6 arguments")
    #Commands to create a separator and a pillar are a bit special so we have to treat them separetly
    list_pillars_sepa = getAllParametersSeparatorsPillarsInRoom(room_name, path)
    list_separator_pillar_changed = listSeparatorPillarChanged(room_name,path,getAllParametersSeparatorsPillarsInRoom(room_name,path))
    list_separator_pillar_correct = correctEntityParameters(room_name,path,list_separator_pillar_changed) 
    for command in list_pillars_sepa:
        entity_type = TYPES[command[0]] if command[0] in TYPES.keys() else ""
        parameters = terrorist(command[1])
        dict_changes = {}
        for elem, param in list_separator_pillar_correct:
            if elem == parameters[0]:
                dict_changes[param[0]] = param[1]
        match entity_type:
            case "Pillar":
                if len(parameters) ==4:
                    center = dict_changes['centerXY'] if 'centerXY' in dict_changes.keys() else parameters[1]
                    size = dict_changes['sizeXY'] if 'sizeXY' in dict_changes.keys() else parameters[2]
                    rotation = dict_changes['rotation'] if 'rotation' in dict_changes.keys() else parameters[3]
                    obj_room.addPillar(parameters[0],center,size,rotation)
                else:
                    raise Exception("A pillar should have 4 parameters")
            case "Separator":
                if len(parameters) ==4:
                    startPos = dict_changes['startPos'] if 'startPos' in dict_changes.keys() else parameters[1]
                    endPos = dict_changes['endPos'] if 'endPos' in dict_changes.keys() else parameters[2]
                    obj_room.addSeparator(parameters[0],startPos,endPos,parameters[3])
                else:
                    raise Exception("A separator should have 4 parameters")
    return obj_room, list_object


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

def findChangesObjects(path : str) -> list:

    list_selection = []
    find_selection_changed = False
    currentSelection = None
    with open(path,'r') as file:
        for line in file:
            current_line = line.strip()
            #We check if a reserved area and a technical area are added
            reserved_tech = re.findall(r'^[^@+:{}-]+:areas=\[[0-9,]{7}\]@\[[0-9,]{7}\]',current_line)
            if reserved_tech !=[]:
                list_selection.append((re.split(':',current_line)[0],['reserved',re.split(r'=',re.split(r'@',current_line)[0])[1]]))
                list_selection.append((re.split(':',current_line)[0],['technical',re.split(r'@',current_line)[1]]))
            if currentSelection != None:
                #We huess that all variable put in a file .ocli are conform
                #A modification is done only if something was selected and the modification if always related the the selection just before
                pattern_change =  re.findall(r'^[^@+:{}-]+:(pos|size|startPos|endPos|centerXY|sizeXY|rotation|axisOrientation|template|unit|floorUnit)[\s]*', current_line)
                if pattern_change !=[]:
                    #I found a change
                    list_selection.append((currentSelection,re.split('=',re.split(':',current_line)[1])))

            #I only want to find selection which were changed
            pattern = re.findall(r'^=\{[^}=:-@+]+\}$|^=[^@+:{}-]+$', current_line)
            if pattern !=[]:
                currentSelection = pattern
    return list_selection

def listItemsToChange(path : str):
    """This functions will break the selection of several entities in unitary entitities"""
    list_changes = findChangesObjects(path)
    #This list will contain all the items which will be changed and the changes
    list_changes_final = []
    for elem, paramaters in list_changes:
        if re.findall(r'=\{', elem[0]) !=[]:
            #We get all the entities of the selection 
            list_entity_changed = re.split(r',',re.split(r'\{', re.split(r'\}',elem[0])[0])[1])
            for entities in list_entity_changed:
                list_changes_final.append((entities,paramaters))
        if re.findall(r'=', elem[0]) !=[]:
            #We only get the name of the entity, not the parent
            list_changes_final.append((re.split(r'=',elem[0])[1],paramaters))
        else:
            #Same here
            list_changes_final.append((elem,paramaters))
    return list_changes_final

def listeItemInRoomToChange(room : str, path : str, liste_elem_in_room : list) -> list:
    """This function will check if the element are in the room room"""
    list_potential_entity = listItemsToChange(path)
    list_entity = []
    for elem, parameter in list_potential_entity:
        #We check if elem is in the room
        if elem in  liste_elem_in_room:
            list_entity.append((elem,[parameter[0],parameter[1]]))
        #We check if the room is a parent of elem
        potential_name = room + "/" + elem
        if potential_name in liste_elem_in_room:
            #room is a parent of elem
            list_entity.append((potential_name,[parameter[0],parameter[1]]))
        #We check if the room have been modified
        if elem == room:
            list_entity.append((elem,[parameter[0],parameter[1]]))
    return list_entity

def listSeparatorPillarChanged(room : str, path : str, liste_elem_in_room : list) -> list:
    """This function will check if the element are in the room room"""
    list_potential_entity = listItemsToChange(path)
    list_entity = []
    for elem, parameter in list_potential_entity:
        #We check if elem is in the room
        if elem in liste_elem_in_room[0][1] or elem in liste_elem_in_room[1][1]:
            #A separator or a pillar is in the room
            list_entity.append((elem, parameter))
    return list_entity

def correctEntityParameters(room:str,path:str, liste_elem_in_room : list) -> list:
    """This function change the type of the parameters if it is possible"""
    list_final = []
    for elem, param in liste_elem_in_room:
        list_final.append((elem,[param[0],transformStringParameters(param[1])]))
    return list_final


def calculatePositionObjectRoom(room : str, path : str, command_entry : tuple):
    """This function will calculate the position of the entity in command_entry whan the position depends on the room position"""
    pos = []
    #command_entry = entity, dict[right,left,...] = (value,unit)
    pos = []
    room_param = getParametersFromName(room,path)
    if len(command_entry) == 2 and type(command_entry[1]) == dict: #TO DO: check the format of entity
        if command_entry[0] not in ["Separator","Device"]:
            #If we have more than 3 parameters, it means we have a size
            if len(room_param[1]) > 4 :
                size_room = room_param[1][3]
            
            #A template has been used so we need to get the size of the room
            elif len(size_room) == 4:
                template = getParametersFromTemplate(size_room[3])
                size_room = template["size"]
            for key in command_entry[1].keys():
                
                #We can calculate the x
                if key == "front" and size_room[0] - command_entry[1]["front"][0] > 0: 
                    floorUnit = room_param[5] if len(room_param[1]) > 6 else "t"        
                    pos.append(convertUnity(size_room[0] - command_entry[1]["front"][0], floorUnit, command_entry[1]["front"][1]))
                elif key == "rear" and size_room[0] > command_entry[1]["rear"][0] > 0: 
                    floorUnit = room_param[5] if len(room_param[1]) > 6 else "t"   
                    pos.append(convertUnity(command_entry[1]["rear"][0], floorUnit, command_entry[1]["rear"][1]))
                
                #We can calculate the y
                if key == "right" and size_room[1] - command_entry[1]["right"][0] > 0: 
                    floorUnit = room_param[5] if len(room_param[1]) > 6 else "t"        
                    pos.append(convertUnity(size_room[1] - command_entry[1]["right"][0], floorUnit, command_entry[1]["right"][1]))
                elif key == "left" and  size_room[1] > command_entry[1]["left"][0] > 0: 
                    floorUnit = room_param[5] if len(room_param[1]) > 6 else "t"        
                    pos.append(convertUnity(command_entry[1]["left"][0], floorUnit, command_entry[1]["left"][1]))
                
                #If entity is a rack or a corridor, entity can also have a z
                if command_entry[0] == 'Rack' or command_entry[1] == 'Corridor':
                    #We can seek a z
                    if key == "top" and size_room[2] - command_entry[1]["top"][0] > 0:
                        floorUnit = room_param[5] if len(room_param[1]) > 6 else "t"        
                        pos.append(convertUnity(size_room[2] - command_entry[1]["top"][0], floorUnit, command_entry[1]["top"][1]))
                    elif key == "bottom" and size_room[2] > command_entry[1]["bottom"][0] > 0: 
                        floorUnit = room_param[5] if len(room_param[1]) > 6 else "t"        
                        pos.append(convertUnity(command_entry[1]["bottom"][0], floorUnit, command_entry[1]["bottom"][1]))
            

            if len(pos) < 1 :
                raise Exception("pos is too small")
        
        #A device only has posU as coordonate
        elif  command_entry[0] == "Device":
            if key == "top" and size_room[2] - command_entry[1]["top"][0] > 0:     
                            pos.append(size_room[2] - command_entry[1]["top"][0])
            elif key == "bottom" and size_room[2] > command_entry[1]["bottom"][0] > 0:      
                            pos.append(command_entry[1]["bottom"][0])
        return pos
    else:
        raise Exception("commmand_entry format false or the entity is a separator")

def calculatePositionObjectRackCorri(entity_name : str, path : str, command_entry : tuple):
    """This function will calculate the position of the entity in command_entry whan the position depends on the room position"""
    #command_entry = entity, dict[right,left,...] = (value,unit)
    pos = []
    entity_param = getParametersFromName(entity_name,path)
    if len(command_entry) == 2 and type(command_entry[1]) == dict: #TO DO: check the format of entity
        if command_entry[0] not in ["Separator","Device"] and entity_param[0] in ["Rack","Corridor"]:
            #They both should have at least 5 parameters
            if len(entity_param[1]) > 4 :
                size_entity= entity_param[1][4] if type(entity_param[1][4]) == list else getParametersFromTemplate(entity_param[1][4])["size"]
            rotation = entity_param[3] #TO DO : Convert rotation in number
            factor_change_vector_y = np.cos(rotation)
            factor_change_vector_x = np.sin(rotation)
            
            for key in command_entry[1].keys():

                if key == "front": 
                    floorUnit = entity_param[3] 
                    valueX =   (size_entity[1] + command_entry[1]["front"][0])*factor_change_vector_x
                    valueY =  (size_entity[1] + command_entry[1]["front"][0])*factor_change_vector_y
                    pos[0] += convertUnity(valueX, floorUnit, command_entry[1]["front"][1])
                    pos[1] += convertUnity(valueY, floorUnit, command_entry[1]["front"][1])
                elif key == "rear": 
                    floorUnit = entity_param[3] 
                    valueX =   -(size_entity[1]["rear"][0])*factor_change_vector_x
                    valueY =  -(size_entity[1]["rear"][0])*factor_change_vector_y
                    pos[0] += convertUnity(valueX, floorUnit, command_entry[1]["rear"][1])
                    pos[1] += convertUnity(valueY, floorUnit, command_entry[1]["rear"][1])
                
                if key == "right": 
                    floorUnit = entity_param[3] 
                    valueX =   (size_entity[1]["right"][0] + size_entity[0])*factor_change_vector_x
                    valueY =  -(size_entity[1]["right"][0] + size_entity[0])*factor_change_vector_y
                    pos[0] += convertUnity(valueX, floorUnit, command_entry[1]["right"][1])
                    pos[1] += convertUnity(valueY, floorUnit, command_entry[1]["right"][1])
                elif key == "left": 
                    floorUnit = entity_param[3] 
                    valueX =   -(size_entity[1]["left"][0])*factor_change_vector_x
                    valueY =  (size_entity[1]["left"][0])*factor_change_vector_y
                    pos[0] += convertUnity(valueX, floorUnit, command_entry[1]["left"][1])
                    pos[1] += convertUnity(valueY, floorUnit, command_entry[1]["left"][1])
                
                #If entity is a rack or a corridor, entity can also have a z
                if command_entry[0] == 'Rack' or command_entry[1] == 'Corridor':
                    #We can seek a z
                    if key == "top":
                        floorUnit = entity_param[3]    
                        pos.append(convertUnity(size_entity[2] + command_entry[1]["top"][0], floorUnit, command_entry[1]["top"][1]))
                    elif key == "bottom" and size_entity[2] > command_entry[1]["bottom"][0] > 0: 
                        floorUnit = entity_param[3]    
                        pos.append(convertUnity(size_entity[2], floorUnit, command_entry[1]["bottom"][1]))
            
        #A device only has posU as coordonate
        elif  command_entry[0] == "Device":
            if key == "top":
                            pos.append(size_entity[2] + command_entry[1]["top"][0])
            elif key == "bottom": 
                            pos.append(size_entity[2])
        
    #TO DO : finish last case
        # elif entity_param[0] == "Device" and command_entry[0] =="Device":
            
        #     if key == "top":  
        #                 pos.append((size_entity[2] - command_entry[1]["top"][0], floorUnit, command_entry[1]["top"][1]))
        #     elif key == "bottom" and size_entity[2] > command_entry[1]["bottom"][0] > 0:  
        #                 pos.append(convertUnity(command_entry[1]["bottom"][0], floorUnit, command_entry[1]["bottom"][1]))

        return pos
    else:
        raise Exception("commmand_entry format false or the entity is a separator")

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
    # print(getAllParametersSeparatorsPillarsInRoom("/P/BASIC/A/R1",path))
    #print(getAllSeparatorsPillars(path))
    #commands = getAllNames(path)
    #print(commands)
    # for command in commands:
    #     print("objet : ",command,"\t| parent : ", getParentName(command))
    #objects = objects_in('/P/BASIC/A/R1',path)
    #print(objects)
    #for obj in objects:
     #    print(obj)
    cmds = getParametersFromName('/P/BASIC/A/R1',path)
    print(cmds)
   # print(getAllElementParameters('/P/BASIC/A/R1',path))
    # room, list_object_Ocli = createListObject('/P/BASIC/A/R1',path)
    # print(list_object_Ocli)
    # print(room)
    # print("Separators : ", room.separators)
    # print("Pillar : ", room.pillars) 
   # for cmd in cmds :
   #     print(cmd)
    # print(findChangesObjects(path))
    #print(listItemsToChange(path))
    # # # print(listeItemInRoomToChange('/P/BASIC/A/R1',path,objects_in('/P/BASIC/A/R1',path)))
    # print(listSeparatorPillarChanged('/P/BASIC/A/R1',path,getAllParametersSeparatorsPillarsInRoom("/P/BASIC/A/R1",path) ))
    # print(correctEntityParameters('/P/BASIC/A/R1',path, listSeparatorPillarChanged('/P/BASIC/A/R1',path,getAllParametersSeparatorsPillarsInRoom("/P/BASIC/A/R1",path) )))
    # # print(correctEntityParameters('/P/BASIC/A/R1',path,listeItemInRoomToChange('/P/BASIC/A/R1',path,objects_in('/P/BASIC/A/R1',path))))
    
    dictio = {}
    dictio["left"] = (7,"m")
    dictio["top"] = (0.3,"cm")
    dictio["front"] = (2,"f")
    entity = "Rack"
    print(calculatePositionObjectRoom('/P/BASIC/A/R1',path, (entity,dictio )))
