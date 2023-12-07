import re
from Component import Component
from Pillar import Pillar



class Room :
    def __init__(self, name : str, position : list, rotation, size : list = None, axisOrientation : str = None, floorUnit : str = None, template : str = None, components : list[Component] = []):
        self.name = name.replace(" ","")
        self.position = position
        self.rotation = rotation%360
        self.template = template
        self.size = size
        self.axisOrientation = axisOrientation
        self.floorUnit = floorUnit
        self.components = components

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

        return boolean
    def addPillar(self, name : str, center : list, size : list, rotation : int) -> None:
        self.components.append(Pillar(".".join([self.name,name]),center,size,rotation))
        
    def getPillar(self, name : str) -> Pillar:
        """Returns a Pillar instance from a Room thanks to its name. A ValueError is raised if there is no pillar with such name."""
        k = 0
        n = len(self.components) - 1
        while k < n or name != self.components[k].name:
            k += 1
        if k == n + 1:
            raise ValueError("The pillar does not exist.")
        return self.components[k]
    
    def getParentName(self, name = "") -> str:
        """This method returns the name of the parent object. It reverses the name, then splits it using dot as separator, and only
        gets the first part of the name, which is put back in order."""
        if (name == ""):
            name = self.name
        return "".join(reversed(name)).split(".",1)[-1][::-1]
    
    def setName(self, newName : str) -> None:
        """If it is a complete new name, with the same parent name, then it is set as the new name. If the parent name is not the same,
        it is added to keep it coherent."""
        if (self.getParentName(newName) == self.getParentName()):
            self.name = newName
        else:
            self.name = ".".join([self.getParentName(),newName])