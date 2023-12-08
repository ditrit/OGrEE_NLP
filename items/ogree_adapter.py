import json
from Room import Room
from Site import Site
from Building import Building


def createRoomFromTemplate(name :str, position : list, rotation : int, filename : str) -> Room:
    """Creates a Room instance from a json file with a template"""
    filename = "demo/rooms/" + filename + ".json"
    with open(filename, "r") as room:
        roomDescription = json.load(room)
    r = Room(name,position,rotation,roomDescription)
    return r

def readFileOCLI(filename :str, searched : str) -> str:
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
    return TERRORIST[typeOfCommand](parameters)

def createSiteFromCommand(parameters : list) -> Site:
    """Creates a site from given parameters"""
    if len(parameters) != 1:
        raise TypeError("An incorrect number of arguments was given")
    name = parameters[0]
    return Site(name)

def createBuidlingFromCommand(parameters : list) -> Building:
    """Creates a building from given parameters"""
    if len(parameters) != 4:
        raise TypeError("An incorrect number of arguments was given")
    name = parameters[0]
    position = json.loads(parameters[1])
    rotation = json.loads(parameters[2])
    size = json.loads(parameters[3])
    return Building(name, position, rotation, size)

def createRoomFromCommand(parameters : list) -> Room:
    """Creates a room from given parameters"""
    if len(parameters) != 4:
        raise TypeError("An incorrect number of arguments was given")
    name = parameters[0]
    position = json.loads(parameters[1])
    rotation = json.loads(parameters[2])
    template = parameters[3]
    return createRoomFromTemplate(name,position,rotation,template)

    
    
TERRORIST = {"+ro" : createRoomFromCommand, "+si" : createSiteFromCommand, "+bd" : createBuidlingFromCommand}

if __name__ == "__main__":
    testCommand = "+bd:/P/BASIC/A@[0,0]@0@[24,30,1]"
    #print(createRoomFromTemplate("R1", [0,0], 0, "demo/rooms/room-square1.json"))
    #print(readFileOCLI("demo/simu1.ocli", "/P/BASIC/A/R1"))
    print(readCommandOCLI(testCommand))