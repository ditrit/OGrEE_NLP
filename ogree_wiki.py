import re

ENTITIES = {
            "tenant" : "tn",
            "site" : "si",
            "building" : "bd",
            "room" : "ro",
            "rack" : "rk",
            "device" : "dv",
            "group" : "gr",
            "corridor" : "co",
            "tag" : "tag",
            "pillar" : "pillars",
            "label" : "label",
            "separator" : "separators"
            }

PARAMETERS_NAME = {
                "tenant" : {"mandatory" : ["name","color"],
                            "optional" : []
                            },
                "site" : {  "mandatory" : ["name"], 
                            "optional" : ["orientation"]
                            },
                "building" : {  "mandatory" : ["name","position","rotation"], 
                                "optional" : ["size","template"]
                                },
                "room" : {  "mandatory" : ["name","position","rotation"], 
                            "optional" : ["size", "axisOrientation", "floorUnit"]
                            },
                "rack" : {  "mandatory" : ["name", "position", "unit","rotation"],
                            "optional" : ["size","template"]
                            },
                "device" : {
                            "mandatory" : ["name"],
                            "optional" : ["position","size","template","slot","side"]
                            },
                "corridor" : {
                            "mandatory" : ["name", "position", "unit","rotation","size","temperature"],
                            "optional" : []
                            },
                "tag" :     {
                            "mandatory" : ["template","color"],
                            "optional" : []
                            },
                "pillar" :  {
                            "mandatory" : ["name", "position", "size","rotation"],
                            "optional"  : []
                },
                "label" :  {
                            "mandatory" : [],
                            "optional"  : ["attribute","font","background","name"]
                },
                "separator" : {
                            "mandatory" : ["name","startPosition","endPosition","type"],
                            "optional"  :[]
                }
                }

COLORS_HEX_BASIC = {
    'red': '#FF0000',
    'green': '#00FF00',
    'blue': '#0000FF',
    'white': '#FFFFFF',
    'black': '#000000',
    'yellow': '#FFFF00',
    'purple': '#800080',
    'orange': '#FFA500',
    'pink': '#FFC0CB',
    'brown': '#A52A2A',
    'cyan': '#00FFFF',
    'gray': '#808080',
    'grey': '#808080'
}

PARAMETERS_FORMAT = {
                "tenant" : {
                    "name" : {
                        "description" : "name of the tenant without blankspaces",
                        "type" : [str]
                    },
                    "color" : {
                        "description" : "hexadecimal color code for the tenant (e.g #ff0000)",
                        "type" : [str]
                    }

                },
                "site" : {
                            "name" : {
                                        "description" : "name of the site without blankspaces",
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
                        "rack" : {
                                        "name" : {
                                                    "description" : "name of the building without blankspaces",
                                                    "type" : [str],
                                                    },
                                        "position" : {
                                                        "description" : "vector [x,y] or [x,y,z] in m, float",
                                                        "type" : [list],
                                                        "len" : [2,3],
                                                        "type_value" : [float, int]
                                                        },
                                        "rotation" : {
                                                        "description" : "rotation of the building from its lower left corner in degrees",
                                                        "type" : [list, str],
                                                        "len"  : 3,
                                                        "type_value" : [float,int]
                                                        },
                                        "size" : {
                                                    "description" : "vector [width, length, height] in m",
                                                    "type" : [list],
                                                    "len" : 3,
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
                                "description" : "temperature of the corridor",
                                "type" : [str],
                                "value" : ["cold", "warm"],
                                },
                        },
                "tag" : {
                        "template" : {
                                "description" : "template of the tag. Replace slug",
                                "type" : [str]
                        },
                        "color" : {
                                "description" : "color of the tag",
                                "type" : [str]
                        }
                        },
                "pillar" : {
                    "name" : {
                                    "description" : "name of the pillar without blankspaces",
                                    "type" : [str],
                                    },
                        "position" : {
                                        "description" : "vector [x,y] in m, float",
                                        "type" : [list],
                                        "len" : [2],
                                        "type_value" : [float, int]
                                        },
                        "rotation" : {
                                        "description" : "rotation of the pillar",
                                        "type" : [float, int]
                                        },
                        "size" : {
                                    "description" : "vector [width,height] in m",
                                    "type" : [list],
                                    "len" : [2],
                                    "type_value" : [float, int]
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

"""
class Site :
    def __init__(self, name : str) :
        self.name = name

    def makeCLI(self):
        return str(self.name)

class Building :
    def __init__(self, name : str, position : list, rotation, size : list, template : str) :
        self.name = name.replace(" ","")
        self.position = position
        self.rotation = rotation%360 if rotation != None else 0
        self.size = size if size != None else [20,20,5]
        self.template = template

    def isConform(self) :
        boolean = True
        attributes_list = [self.name, self.position, self.rotation]
        if None in attributes_list :
            raise Exception("Missing argument",PARAMETERS_NAME["building"]["mandatory"][attributes_list.index(None)])
        boolean = boolean and len(self.position) == 2
        for coord in self.position :
            boolean = boolean and (type(coord) in [float,int])
        boolean = boolean and (type(self.rotation) in [float,int])
        for coord in self.size :
            boolean = boolean and (type(coord) in [float,int])
        return boolean
        # TODO : check template -> if not all optional parameters should be verified

    def makeCLI(self) :
        string = ""
        parameters_string = [self.name, str(self.position), str(self.rotation)]
        string += "@".join(parameters_string)
        # TODO : add the other parameters
        return string

class Room :
    def __init__(self, name : str, position : list, rotation, size : list = None, axisOrientation : str = None, floorUnit : str = None, template : str = None):
        self.name = name.replace(" ","")
        self.position = position
        self.rotation = rotation%360
        self.template = template
        self.size = size
        self.axisOrientation = axisOrientation
        self.floorUnit = floorUnit

    def isConform(self) : # TODO : complete template or not
        boolean = True

        boolean = boolean and len(self.position) == 2
        for coord in self.position :
            boolean = boolean and (type(coord) in [float,int])
        boolean = boolean and (type(self.rotation) in [float,int])
        
        if self.template != None :
            boolean = boolean and (type(self.template) == str)
        if self.size != None :
            boolean = boolean and (len(self.size) == 3)
            for value in self.size :
                boolean = boolean and (type(value) in [float,int])
        if self.axisOrientation != None :
            test = re.search("[+-]x[+-]y", self.axisOrientation.replace(" ",""))
            if test == None :
                boolean = False
        if self.floorUnit != None :
            boolean = boolean and (self.floorUnit.replace(" ","") in ["t","f","m"])
        #TO DO TEMPLATE OR (SIZE,....)
        return boolean
    def addPillar(self, name : str, center : list, size : list, rotation : int) -> None:
        #TO DO : Quentin
        pass
"""
"""
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
        boolean = boolean and (rack_rotation in rotation_possible.keys() or rack_rotatiotation_possible.values())
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
        
        return boolean"""


