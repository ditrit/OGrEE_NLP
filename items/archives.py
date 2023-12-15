"""This module contains old code, which is potentially reusable but not fonctional at the moment"""

#region:site
"""This module contains methods to create commands from parameters for sites"""

from tools import isColorConform,isOrientationConform,getParentName, isNameConform, isConform

CONFORMITY_CHECK = {"name" : isNameConform, "orientation" : isOrientationConform}

def createSite(parameters : dict) -> str:
    """Creates a site from given parameters"""
    if not isConform(parameters, CONFORMITY_CHECK):
        raise ValueError("The parameters given are invalid for a site")
        #this precondition is currently incomplete
    return "+si:" + "@".join([str(parameters[key]) for key in parameters.keys()])

def setName(oldName, newName : str) -> str:
    """Changes the name of an object, and ensures to keep it coherent"""
    oldNameParent = getParentName(oldName)
    newNameParent = getParentName(newName)
    if oldNameParent != newNameParent:
        raise ValueError("The new name is invalid because it does not respect the convention of the parent name")
    return "{}:name={}".format(oldName, newName)
    
def setOrientation(oldOrientation : str, newOrientation : str) -> str:
    """Changes the orientation of an object"""
    if not isOrientationConform(newOrientation):
        raise ValueError("The orientation is invalid")
    return "{}:orientation={}".format(oldOrientation, newOrientation)

def createAttribute(name : str, attributeName : str, attributeArgument) -> str:
    """Adds an attribute to an object with a given argument"""
    return "{}.{}={}".format(name, attributeName,attributeArgument)
    
def setAttribute(name : str, attributeName : str, attributeArgument) -> str:
    """Modifies an attribute of an object with a given argument"""
    return "{}:{}={}".format(name,attributeName,attributeArgument)
    
def setUsableColor(name : str, color : str) -> str:
    """Modifies the usable color of a site"""
    if not isColorConform(color):
        raise ValueError("The color format is invalid")
    return "{}:usableColor={}".format(name, color)
    
def setReservedColor(name : str, color : str) -> str:
    """Modifies the reserved color of a site"""
    if not isColorConform(color):
        raise ValueError("The color format is invalid")
    return "{}:reservedColor={}".format(name, color)
    
def setTechnicalColor(name : str, color : str) -> str:
    """Modifies the technical color of a site"""
    if not isColorConform(color):
        raise ValueError("The color format is invalid")
    return "{}:technicalColor={}".format(name, color)
        
if __name__ == "__main__":
    print(createSite({"name" : "P/BASIC", "orientation":"WSW"}))

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
#endregion

#region:building
def isConform(self) :
    boolean = True
    attributes_list = [self.name, self.position, self.rotation]
    if None in attributes_list :
        raise Exception("Missing argument",["name","position","rotation"][attributes_list.index(None)])
    boolean = boolean and self.positionConform(self.position)
    boolean = boolean and self.rotationConform(self.rotation)
    boolean = boolean and self.sizeConform(self.size)
    boolean = boolean and self.templateConform(self.template)
    return boolean
    # TODO : check template -> if not all optional parameters should be verified

def getIndexRoom(self, name : str) -> int:
    """Returns the index of a room thanks to its name in the list of roomss in the building. A ValueError is raised if there
    is no room with such name"""
    k = 0
    n = len(self.rooms) - 1
    if n < 0:
        raise IndexError("There is no building in this site.")
    while k < n or (name != self.rooms[k].name and "/".join([self.name,name]) != self.rooms[k].name):
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
    
def __str__(self):
    """Returns a string representing the building"""
    return """Building : name = {}, position = {}, rotation = {},
                size = {}""".format(self.name,self.position,self.rotation, self.size)
#endregion

#region:Room
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

def getComponent(self, name : str):
    """Returns a Component instance from a Room thanks to its name. A ValueError is raised if there is no component with such name."""
    return self.components[self.getIndexComponent(name)]

#This method creates a group of rack
#def createGroup(self, name : str, *comp):
#    if len(comp) != 0 : 
#        group = Group(self.name + "/" + name)
#       for compo in comp:
#            group.addComponent(compo)
#        self.components.append(group)

def removeComponent(self, name : str) -> None:
    """Removes a Component instance from the room thanks to its name. A ValueError is raised if there is no component with such name.
    This operation is final and means that the Component instance is permanently deleted."""
    del self.components[self.getIndexComponent(name)]
    
def __str__(self):
    """Returns a string representing the room"""
    return """Room : name = {}, position = {}, rotation = {},
                axisOrientation = {}, size = {}, 
                floor unit = {}""".format(self.name,self.position,self.rotation, self.axisOrientation, self.size, self.floorUnit)
#endregion