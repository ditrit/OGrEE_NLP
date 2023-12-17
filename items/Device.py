from Component import Component

class Device(Component):
    
    def __init__(self, name : str, posU : int | float, sizeU : int | float, slot : str, template : str, side : str):
        self.name = name
        self.posU = posU
        self.sizeU = sizeU
        if slot !=None:
            self.slot = slot.lower
        else:
            self.slot = slot
        if template !=None:
            self.template = template.lower
        else :
            self.template = template
        self.side = side
    
    def isConform(self) -> bool:
        boolean = True

        #We verify that name !=None 
        boolean = boolean and self.name !=None 

        #We check that pos is [int,float]
        if self.posU !=None:
            boolean = boolean and type(self.posU) in [int,float]
        

        #We check that a posU XOR a slot
        if self.posU !=None and self.slot !=None:
            boolean = False
        #We check that we have a sizu XOR a template
        if self.sizeU !=None and self.template !=None:
            boolean = False
      
        if self.sizeU != None:
            boolean = boolean and type(self.sizeU) in [int, float]
        
        #side can only be !=None if slot !=None
        if self.slot == None and self.side !=None:
            boolean = False
        
        #If slot !=None, side can only be a special string
        if self.slot !=None:
            boolean = boolean and self.side.replace(" ", "") in ["front","rear","frontflipped","rearflipped"]
        
        #If slot !=None and side !=None, we have to use template and not size
        if self.slot !=None and self.side !=None:
            boolean = boolean and self.template !=None

        return boolean


