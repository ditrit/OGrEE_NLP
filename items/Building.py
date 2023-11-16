from Room import Room
from ogree_wiki import PARAMETERS_NAME

class Building :
    def __init__(self, name : str, position : list, rotation, size : list, template : str, *rooms : Room) :
        self.name = name.replace(" ","")
        self.position = position
        self.rotation = rotation%360 if rotation != None else 0
        self.size = size
        self.template = template
        self.rooms = rooms

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