

class Component:
    def __init__(self, name : str, position : list, size : list, rotation : list):
        self.name = name
        self.position = position
        self.size = size
        self.rotation = rotation
    def __eq__(self, __value: object) -> bool:
        if (type(__value) != Component):
            raise TypeError("A component is exepcted.")
        return self.name == __value.name