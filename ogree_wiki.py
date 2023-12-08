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
                                                        "len" : 2,
                                                        "type_value" : [float, int]
                                                        },
                                        "rotation" : {
                                                        "description" : "rotation of the building from its lower left corner in degrees",
                                                        "type" : [float, int]
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
    for entry in entry_list : 
        boolean = boolean and (type(entry) in dictio_conformity["type_value"])
    return boolean

class Site :
    def __init__(self, name : str) :
        self.name = name

    def makeCLI(self) :
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


