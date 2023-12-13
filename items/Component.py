from tools import isListOfNumbers

class Component:
    def __init__(self, name : str, position : list, rotation : list, size : list):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.size = size
    
    def isConform(self) -> bool:
        boolean = True
        boolean = boolean and self.positionConform(self.position)
        boolean = boolean and self.rotationConform(self.rotation)
        boolean = boolean and self.sizeConform(self.size)

        return boolean
        
    def positionConform(self, testPosition : list) -> bool:
        return (len(testPosition) == 2 or len(testPosition) == 3) and isListOfNumbers(testPosition)
    
    def rotationConform(self, testRotation : float) -> bool:
        return type(testRotation) in [float,int]
    
    def sizeConform(self, testSize : list) -> bool:
        return len(testSize) == 3 and isListOfNumbers(testSize)
    
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
    
    def setPosition(self, newPosition : list) -> None:
        """This sets a new position for the component"""
        if self.positionConform(newPosition):
            self.position = newPosition
        else:
            raise ValueError("The position format is invalid.")
     
    def setRotation(self, newRotation : float) -> None:
        """This sets a new rotation for the component"""
        if self.rotationConform(newRotation):
            self.rotation = newRotation
        else:
            raise ValueError("The rotation format is invalid.")
    
    def __eq__(self, __value: object) -> bool:
        if (type(__value) != Component):
            raise TypeError("A component is expected.")
        return self.name == __value.name