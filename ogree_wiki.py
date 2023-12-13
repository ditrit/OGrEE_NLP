import re

ENTITIES = {
            "site" : "si",
            "building" : "bd",
            "room" : "ro",
            "rack" : "rk",
            "device" : "dv",
            "group" : "gr",
            "corridor" : "co"
            }

PARAMETERS_NAME = {
                "site" : {  "mandatory" : ["name"], 
                            "optional" : []
                            },
                "building" : {  "mandatory" : ["name","position","rotation"], 
                                "optional" : ["size"]
                                },
                "room" : {  "mandatory" : ["name","position","rotation"], 
                            "optional" : ["size", "axisOrientation", "floorUnit"]
                            },
                }

PARAMETERS_FORMAT = {
                "site" : {
                        "name" : {
                                "description" : "name of the site without blankspaces",
                                "type" : [str],
                                },
                        "orientation" : {
                                "description" : "orientation of the site",
                                "type" : [str],
                                }            
                        },
                "building" : {
                        "name" : {
                                "description" : "name of the building without blankspaces",
                                "type" : [str],
                                },
                        "position" : {
                                "description" : "vector [x,y] in m, float",
                                "type" : [list],
                                "len" : [2],
                                "type_value" : [float, int]
                                },
                        "rotation" : {
                                "description" : "rotation of the building from its lower left corner in degrees",
                                "type" : [float, int]
                                },
                        "size" : {
                                "description" : "vector [width, length, height] in m",
                                "type" : [list],
                                "len" : [3],
                                "type_value" : [float, int]
                                },
                        "template" : {
                                "description" : "name of the template",
                                "type" : [str],
                                }
                        },
                "room" : {
                        "name" : {
                                "description" : "name of the room without blankspaces",
                                "type" : [str],
                                },
                        "position" : {
                                "description" : "vector [x,y] in m, float",
                                "type" : [list],
                                "len" : [2],
                                "type_value" : [float, int]
                                },
                        "rotation" : {
                                "description" : "rotation of the room from its lower left corner in degrees",
                                "type" : [float, int]
                                },
                        "size" : {
                                "description" : "vector [width, length, height] in m",
                                "type" : [list],
                                "len" : [3],
                                "type_value" : [float, int]
                                },
                        "axisOrientation" : {
                                "description" : "orientation of the rows and columns",
                                "type" : [str],
                                },
                        "floorUnit" : {
                                "description" : "unit type on the floor for the room",
                                "type" : [str],
                                "value" : ["t", "m", "f"]
                                },        
                        "template" : {
                                "description" : "name of the template",
                                "type" : [str],
                                }
                        },
                "device" : {
                        "name" : {
                                "description" : "name of the device without blankspaces",
                                "type" : [str],
                                },
                        "slot" : {

                                },
                        "side" : {

                                },
                        "posU" : {

                                },
                        "sizeU" : {

                                },     
                        "template" : {
                                "description" : "name of the template",
                                "type" : [str],
                                } 
                        },
                "group" : {
                        "name" : {
                                "description" : "name of the group without blankspaces",
                                "type" : [str],
                                },
                        "nameChildren" : {
                                "description" : "name of the children in the group",
                                "type" : [list],
                                "type_value" : [str],
                                },
                        },
                "corridor" : {
                        "name" : {
                                "description" : "name of the corridor without blankspaces",
                                "type" : [str],
                                },
                        "position" : {
                                "description" : "vector [x,y] or [x,y,z] in m, float",
                                "type" : [list],
                                "len" : [2, 3],
                                "type_value" : [float, int]
                                },
                        "rotation" : {
                                "description" : "rotation of the corridor from its lower left corner in degrees",
                                "type" : [list],
                                "len" : [3],
                                "type_value" : [float, int]
                                },
                        "size" : {
                                "description" : "vector [width, length, height] in m",
                                "type" : [list],
                                "len" : [3],
                                "type_value" : [float, int]
                                },
                        "temperature" : {
                                "description" : "temperature of teh corridor",
                                "type" : [str],
                                "value" : ["cold", "warm"],
                                },
                        }                
                }

def makeDictParam(entity : str) -> dict :
    dictio = {}
    for parameter in listAllParameter(entity) :
        dictio[parameter] = None
    return dictio

def listAllParameter(element : str) :
    full_liste = PARAMETERS_NAME[element]["mandatory"]
    full_liste.extend(PARAMETERS_NAME[element]["optional"])
    if element in ["building","room","rack","device"] :
        full_liste.append("template")
    return full_liste

def conformityParameter(element : str, parameter : str, entry) :

    dictio_conformity = PARAMETERS_FORMAT[element][parameter]
    if type(entry) in dictio_conformity["type"] :

        if dictio_conformity["type"][0] == str :
            return True
        elif dictio_conformity["type"][0] == list :
            return conformityList(dictio_conformity, entry)
        elif dictio_conformity["type"][0] == float :
            return True
        else :
            return False
            
    return Exception("Wrong type")


def conformityList(dictio_conformity : dict, entry_list) :
    boolean = True
    boolean = boolean and (len(entry_list) == dictio_conformity["len"])
    for entry in entry_list: 
        boolean = boolean and (type(entry) in dictio_conformity["type_value"])
    return boolean

class Rack:
    rotation_possible = {"LEFT" : [0,90,0], "RIGHT": [0,-90,0], "FRONT" : [0,0,180], "REAR": [0,0,0] , "TOP": [90,0,0],
    "BOTTOM": [-90,0,0]}

    def __init__(self, position : list, unit : str, rack_rotation : str | list, size : list = None, template : str = None):
        self.position = position
        self.unit = unit
        self.rack_rotation = rack_rotation
        self.size = size
        self.template = template
    
    def isConform(self):
        boolean = True
        
        #We verify that we have at least 2 coordinate in position
        boolean = boolean and (len(self.position) ==2 or len(self.position) ==3)
        
        #We verify that each coordinate are a float or an int
        for coor in self.postion:
            boolean = boolean and (type(coor) in [float,int])
        #We check the rotation. It should be a str which is a key of rotation_possible or a list in the values
        # of rotation_possible
        boolean = boolean and (rack_rotation in rotation_possible.keys() or rack_rotation in rotation_possible.values())

        #We should have a size XOR a template
        if (self.size != None or self.template !=None) and not(self.size !=None and self.template !=None) :

            #If size != None, the size of a rack should be a length 3 vector
            if(self.size !=None):
                boolean = boolean and len(self.size) ==3
                #Each elements of size should be an int or a float
                for elem in self.size:
                  boolean = boolean and type(elem) in [float, int]
            
            #A rack can have a template
            if(self.template !=None):
                boolean = boolean and type(self.template) == str

        else: 
            boolean = False
        
        return boolean


