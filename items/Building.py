from Room import Room
from Component import Component

class Building :
    def __init__(self, name : str, position : list, rotation, size : list, template : str, rooms : list[Room] = []) :
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
            raise Exception("Missing argument",["name","position","rotation"][attributes_list.index(None)])
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
    
    def addRoom(self, name : str, position : list, rotation, size : list = None, axisOrientation : str = None, floorUnit : str = None, template : str = None, components : list[Component] = []) -> None:
        """Adds a Room instance with specified parameters to the building."""
        self.rooms.append(Room(".".join([self.name,name]), position, rotation, size, axisOrientation, floorUnit, template, components))
    
    def getIndexRoom(self, name : str) -> int:
        """Returns the index of a room thanks to its name in the list of roomss in the building. A ValueError is raised if there
        is no room with such name"""
        k = 0
        n = len(self.rooms) - 1
        if n < 0:
            raise IndexError("There is no building in this site.")
        while k < n or (name != self.rooms[k].name and ".".join([self.name,name]) != self.rooms[k].name):
            k += 1
        if k == n + 1:
            raise ValueError("The room {} does not exist.".format(name))
        return k

    def getRoom(self,name : str) -> Room:
        """Returns a Room instance from the building thanks to its name. A ValueError is raised if there is no room with such name."""
        return self.rooms[self.getIndexRoom(name)]
    
    def removeRoom(self, name : str) -> None:
        """Removes a Room instance from the building thanks to its name. A ValueError is raised if there is no room with such name.
        This operation is final and means that the Room instance is permanently deleted."""
        del self.rooms[self.getIndexRoom(name)]
        