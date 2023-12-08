import re

from Component import Component
from Pillar import Pillar
from Group import Group
from Rack import Rack

from tools import isListOfNumbers


class Room :
    def __init__(self, name : str, position : list, rotation, size : list = None, axisOrientation : str = None, floorUnit : str = None, template : str = None, components : list[Component] = []):
        self.name = name.replace(" ","")
        self.position = position
        self.rotation = rotation%360
        self.size = size
        self.axisOrientation = axisOrientation
        self.floorUnit = floorUnit
        self.template = template
        self.components = components
    
    def positionConform(self, testPosition : list) -> bool:
        return len(testPosition) == 2 and isListOfNumbers(testPosition)
    
    def rotationConform(self, testRotation : float) -> bool:
        return type(testRotation) in [float,int]
    
    def sizeConform(self, testSize : list) -> bool:
        return len(testSize) == 3 and isListOfNumbers(testSize)
    
    def axisOrientationConform(self, testAxis : str) -> bool:
        return re.search("[+-]x[+-]y", self.axisOrientation.replace(" ","")) == None
    
    def floorUnitConform(self, testFloorUnit : str) -> bool:
        return self.floorUnit.replace(" ","") in ["t","f","m"]
    
    def templateConform(self, testTemplate : str) -> bool:
        return type(testTemplate) == str
    

    def isConform(self) : # TODO : complete template or not
        boolean = True
        boolean = boolean and self.positionConform(self.position)
        boolean = boolean and self.rotationConform(self.rotation)
        if self.size != None :
            boolean = boolean and self.sizeConform(self.size)
        if self.axisOrientation != None :
            boolean = boolean and self.axisOrientationConform(self.axisOrientation)
        if self.floorUnit != None :
            boolean = boolean and self.floorUnitConform(self.floorUnit)
        if self.template != None:
            boolean = boolean and self.templateConform(self.template)

        return boolean
    
    def addComponent(self, component : Component) -> None:
        if not (component in self.components):
            self.components.append(component)
        else:
            raise Exception("There is already the same component in this room.")

    def addPillar(self, name : str, center : list, size : list, rotation : int) -> None:
        pillar = Pillar("/".join([self.name,name]),center,size,rotation)
        self.addComponent(pillar)
        
    def getIndexComponent(self, name : str) -> int:
        """Returns the index of a Component thanks to its name in the list of components in the room. A ValueError is raised if there
        is no component with such name."""
        k = 0
        n = len(self.components) - 1
        if n < 0:
            raise IndexError("There is no component in this room.")
        while k < n or (name != self.components[k].name and "/".join([self.name, name]) != self.components[k].name):
            k += 1
        if k == n + 1:
            raise ValueError("The component {} does not exist.".format(name))
        return k

    def getComponent(self, name : str) -> Component:
        """Returns a Component instance from a Room thanks to its name. A ValueError is raised if there is no component with such name."""
        return self.components[self.getIndexComponent(name)]

    #This method creates a group of rack
    def createGroup(self, name : str, *comp : Rack):
        if len(comp) != 0 : 
            group = Group(self.name + "/" + name)
            for compo in comp:
               group.addComponent(compo)
            self.components.append(group)
    
    def getParentName(self, name = "") -> str:
        """This method returns the name of the parent object. It reverses the name, then splits it using dot as separator, and only
        gets the first part of the name, which is put back in order."""
        if (name == ""):
            name = self.name
        return "".join(reversed(name)).split("/",1)[-1][::-1]
    
    def setName(self, newName : str) -> None:
        """If it is a complete new name, with the same parent name, then it is set as the new name. If the parent name is not the same,
        it is added to keep it coherent."""
        if (self.getParentName(newName) == self.getParentName()):
            self.name = newName
        else:
            self.name = "/".join([self.getParentName(),newName])
    
    def setPosition(self, newPosition : list) -> None:
        """This sets a new position for the room"""
        if self.positionConform(newPosition):
            self.position = newPosition
        else:
            raise ValueError("The position format is invalid.")
     
    def setRotation(self, newRotation : float) -> None:
        """This sets a new rotation for the room"""
        if self.rotationConform(newRotation):
            self.rotation = newRotation
        else:
            raise ValueError("The rotation format is invalid.")
    
    def setSize(self, newSize: list) -> None:
        """This sets a new size for the room"""
        if self.sizeConform(newSize):
            self.size = newSize
        else:
            raise ValueError("The size format is invalid.")
    def setAxisOrientation(self, newAxisOrientation : str) -> None:
        """This sets a new axis orientation for the room"""
        if self.axisOrientationConform(newAxisOrientation):
            self.axisOrientation = newAxisOrientation
        else:
            raise ValueError("The axis orientation format is invalid.")
     
    def setFloorUnit(self, newFloorUnit : str) -> None:
        """This sets a new floor unit for the room"""
        if self.floorUnitConform(newFloorUnit):
            self.floorUnit = newFloorUnit
        else:
            raise ValueError("The floor unit format is invalid.")
    
    def setTemplate(self, newTemplate : str) -> None:
        """This sets a new template for the room"""
        if self.templateConform(newTemplate):
            self.template = newTemplate
        else:
            raise ValueError("The template format is invalid")
    
    def removeComponent(self, name : str) -> None:
        """Removes a Component instance from the room thanks to its name. A ValueError is raised if there is no component with such name.
        This operation is final and means that the Component instance is permanently deleted."""
        del self.components[self.getIndexComponent(name)]
