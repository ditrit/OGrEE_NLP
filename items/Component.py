class Component:
    def __init__(self, name : str, position : list, rotation : list, size : list):
        self.name = name
        self.position = position
        self.size = size
        self.rotation = rotation

    def __eq__(self, __value: object) -> bool:
        if (type(__value) != Component):
            raise TypeError("A component is exepcted.")
        return self.name == __value.name

    def getFloorArea(self):
        """Returns the floor area of a given component."""
        return self.size[0]*self.size[1]