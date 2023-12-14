import re

ENTITIES = {
            "site" : "si",
            "building" : "bd",
            "room" : "ro",
            "rack" : "rk",
            "device" : "dv",
            "group" : "gr",
            "corridor" : "co",
            "tag" : "tag"
            }

PARAMETERS_NAME = {
                "site" : {  "mandatory" : ["name"], 
                            "optional" : []
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
                            "mandatory" : ["name","color"],
                            "optional" : []
                            }
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
                                        #  "len" : 2, Ici c'est 2 ou 3 et de la manière dont ça a été codé il vaut mieux
                                        #rien mettre
                                        "type_value" : [float, int]
                                        },
                        "rotation" : {
                                        "description" : "rotation of the building from its lower left corner in degrees",
                                        "type" : [list, str],
                                        "len"  : [3],
                                        "type_value" : [float,int]
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

