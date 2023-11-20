from Building import Building
from Room import Room

class Site :
    def __init__(self, name : str, buildings : list[Building] = []) :
        self.name = name
        self.buildings = buildings
        
    def makeCLI(self) -> str:
        return str(self.name)
    
    def addBuilding(self, name : str, position : list, rotation, size : list, template : str, rooms : list[Room] = []) -> None:
        """Adds a Building instance with specified parameters to the site."""
        self.buildings.append(Building(".".join([self.name,name]), position, rotation, size, template, rooms))
    
    def getIndexBuilding(self, name : str) -> int:
        """Returns the index of a Building thanks to its name in the list of buildings located on the site. A ValueError is raised if there
        is no building with such name."""
        k = 0
        n = len(self.buildings) - 1
        if n < 0:
            raise IndexError("There is no building in this site.")
        while k < n or (name != self.buildings[k].name and ".".join([self.name, name]) != self.buildings[k].name):
            k += 1
        if k == n + 1:
            raise ValueError("The building {} does not exist.".format(name))
        return k

    def getBuilding(self,name : str) -> Building:
        """Returns a Building instance from the site thanks to its name. A ValueError is raised if there is no building with such name."""
        return self.buildings[self.getIndexBuilding(name)]
    
    def removeBuilding(self, name : str) -> None:
        """Removes a Building instance from the site thanks to its name. A ValueError is raised if there is no building with such name.
        This operation is final and means that the Building instance is permanently deleted."""
        del self.buildings[self.getIndexBuilding(name)]
        
if __name__ == "__main__":
    site = Site("S1")
    site.addBuilding("B1", [2,5], 0, [8,9,2], "")
    print(site.buildings)
    print(site.getBuilding("S1.B1"))
    print(site.getBuilding("B1"))
    site.removeBuilding("S1.B1")
    print(site.buildings)
    print(site.getBuilding("S1.B1"))