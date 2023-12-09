from Building import Building
from Room import Room
from tools import isHexColor,isOrientation, isListOfNumbers

class Site :
    def __init__(self, name : str, orientation : str = "") :
        self.name = name
        self.orientation = orientation
        
    def createCLI(self) -> str:
        return "+si:{}".format(self.name)
    
    def getParentName(self, name = "") -> str:
        """This method returns the name of the parent object. It reverses the name, then splits it using dot as separator, and only
        gets the first part of the name, which is put back in order."""
        if (name == ""):
            name = self.name
        return "".join(reversed(name)).split("/",1)[-1][::-1]
    
    def setName(self, newName : str) -> str:
        self.name = newName
        return "{}:name={}".format(self.name, newName)
    
    def setOrientation(self, newOrientation : str) -> str:
        if not isOrientation(newOrientation):
            raise ValueError("The orientation is invalid")
        self.orientation = newOrientation
        return "{}:orientation={}".format(self.orientation, newOrientation)

    def createAttribute(self, attributeName : str, attributeArgument):
        return self.name + ".{}={}".format(attributeName,attributeArgument)
    
    def setAttribute(self, attributeName : str, attributeArgument):
        return self.name + ":{}={}".format(attributeName,attributeArgument)
    
    def setUsableColor(self, color : str) -> str:
        if not isHexColor(color):
            raise ValueError("The color format is invalid")
        return self.name + ":usableColor={}".format(color)
    
    def setReservedColor(self, color : str) -> str:
        if not isHexColor(color):
            raise ValueError("The color format is invalid")
        return self.name + ":reservedColor={}".format(color)
    
    def setTechnicalColor(self, color : str) -> str:
        if not isHexColor(color):
            raise ValueError("The color format is invalid")
        return self.name + ":technicalColor={}".format(color)
    
    def getIndexBuilding(self, name : str) -> int:
        """Returns the index of a Building thanks to its name in the list of buildings located on the site. A ValueError is raised if there
        is no building with such name."""
        k = 0
        n = len(self.buildings) - 1
        if n < 0:
            raise IndexError("There is no building in this site.")
        while k < n or (name != self.buildings[k].name and "/".join([self.name, name]) != self.buildings[k].name):
            k += 1
        if k == n + 1:
            raise ValueError("The building {} does not exist.".format(name))
        return k

    def getBuilding(self, name : str) -> Building:
        """Returns a Building instance from the site thanks to its name. A ValueError is raised if there is no building with such name."""
        return self.buildings[self.getIndexBuilding(name)]
    
    def removeBuilding(self, name : str) -> None:
        """Removes a Building instance from the site thanks to its name. A ValueError is raised if there is no building with such name.
        This operation is final and means that the Building instance is permanently deleted."""
        del self.buildings[self.getIndexBuilding(name)]
        
if __name__ == "__main__":
    pass