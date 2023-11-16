class Rack:
    rotation_possible = {"LEFT" : [0,90,0], "RIGHT": [0,-90,0], "FRONT" : [0,0,180], "REAR": [0,0,0] , "TOP": [90,0,0],
    "BOTTOM": [-90,0,0]}

    def __init__(self, position : list, unit : str, rack_rotation : str | list, size : list = None, template : str = None):
        self.position = position
        self.unit = unit
        self.rack_rotation = rack_rotation
        self.size = size
        self.template = template
    
    def isConform(self):
        boolean = True
        
        #We verify that we have at least 2 coordinate in position
        boolean = boolean and (len(self.position) ==2 or len(self.position) ==3)
        
        #We verify that each coordinate are a float or an int
        for coor in self.position:
            boolean = boolean and (type(coor) in [float,int])
        #We check the rotation. It should be a str which is a key of rotation_possible or a list in the values
        # of rotation_possible
        boolean = boolean and (self.rack_rotation in list(self.rotation_possible.keys()) or self.rack_rotation in list(self.rotation_possible.values()))

        #We should have a size XOR a template
        if (self.size != None or self.template !=None) and not(self.size !=None and self.template !=None) :

            #If size != None, the size of a rack should be a length 3 vector
            if(self.size !=None):
                boolean = boolean and len(self.size) ==3
                #Each elements of size should be an int or a float
                for elem in self.size:
                  boolean = boolean and type(elem) in [float, int] 
                  boolean = boolean and elem >=0
            
            #A rack can have a template
            if(self.template !=None):
                boolean = boolean and type(self.template) == str

        else: 
            boolean = False
        
        return boolean

