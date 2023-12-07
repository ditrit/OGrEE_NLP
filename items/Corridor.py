from Component import Component

class Corridor(Component):
    rotation_possible = {"LEFT" : [0,90,0], "RIGHT": [0,-90,0], "FRONT" : [0,0,180], "REAR": [0,0,0] , "TOP": [90,0,0],
    "BOTTOM": [-90,0,0]}

    def __init__(self, name : str, position : list, unit : str, corridor_rotation : str | list, size : list , temperature: str):
        self.name = name
        self.position = position
        self.unit = unit
        self.corridor_rotation = corridor_rotation
        self.size = size
        self.temperature = temperature

    def isConform(self):
        boolean = True
        
        #We verify that we have at least 2 coordinate in position
        boolean = boolean and (len(self.position) ==2 or len(self.position) ==3)
        
        #We check the unit. It should be m, t or f
        boolean = boolean and (self.unit.replace(" ","").lower() in ["t","f","m"])

        #We verify that each coordinate are a float or an int
        for coor in self.position:
            boolean = boolean and (type(coor) in [float,int])
        #We check the rotation. It should be a str which is a key of rotation_possible or a list in the values
        # of rotation_possible
        boolean = boolean and (self.corridor_rotation in list(self.rotation_possible.keys()) or self.corridor_rotation in list(self.rotation_possible.values()))

        #The size of a corridor should be a length 3 vector
        boolean = boolean and len(self.size) ==3
        
        #Each elements of size should be an int or a float and >=0
        for elem in self.size:
            boolean = boolean and type(elem) in [float, int] 
            boolean = boolean and elem >=0
        
        #We check the temperature
        boolean = boolean and (self.temperature.replace(" ","").lower() in ["cold","warm"])

        return boolean


