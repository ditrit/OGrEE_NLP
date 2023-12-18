"""This module contains methods to create commands from parameters for racks"""

import json
from solver.Component import Component
from solver.Device import Device
from tools import isConform
from math import *

RACK_PARAMETERS = []
CONFORMITY_CHECK = {}


def createRack(parameters : dict) -> str:
    """Creates a rack from given parameters"""
    if not isConform(parameters, RACK_PARAMETERS, CONFORMITY_CHECK):
        raise ValueError("The parameters given are invalid for a rack")
    return "+rk:" + "@".join([str(parameters[key]) for key in RACK_PARAMETERS])


class Rack(Component):
    rotation_possible = {"LEFT" : [0,90,0], "RIGHT": [0,-90,0], "FRONT" : [0,0,180], "REAR": [0,0,0] , "TOP": [90,0,0],
    "BOTTOM": [-90,0,0]}
    possible_units = ['t','m','f']

    def __init__(self, name : str, position : list, rack_rotation : str | list, size : list, unit : str = 't', components : list = [], clearance = [0, 0, 0, 0, 0, 0]):
        self.unit = unit
        self.components = components
        self.clearance = clearance
        super.__init__(name,position,rack_rotation,size)

    @classmethod
    def create_from_template(Rack,name,position,rack_rotation,template,unit = 't',components : list = [],clearance = [0, 0, 0, 0, 0, 0]):
        size = super().set_param_from_template(template,'size')
        return Rack(name, position,rack_rotation,size,unit,components,clearance)

    def set_clearance_from_template(template):
        with open(template) as json_file :
            try:
                template = json.load(json_file)
                if 'clearance' in template:
                    clearance = template['clearance']
                    return clearance
                else:
                    print("Couldn't find clearance parameter in the file")
            except BaseException as e:
                print('The file contains invalid JSON')
                print(e)

    def get_vertices(self):
        """Returns the vertices of the rectangle taking the clearance into account"""
        x0,y0 = self.position
        L, l = self.getFloorDimensions()
        alpha = self.rotation[2]
        cFr, cRe, cLe, cRi = self.clearance[0], self.clearance[1], self.clearance[2], self.clearance[3]
        right_front = [x0 + cos(alpha)*(L + cRi) + sin(alpha)*cRe,       y0 - cos(alpha)*cRe + sin(alpha)*(L + cRi)]
        right_rear =  [x0 + cos(alpha)*(L + cRi) - sin(alpha)*(l + cFr), y0 + cos(alpha)*(l + cFr) + sin(alpha)*(L + cRi)]
        left_front =  [x0 - cos(alpha)*cLe - sin(alpha)*(l + cFr),       y0 + cos(alpha)*(l + cFr) - sin(alpha)*cLe]
        left_rear =   [x0 - cos(alpha)*cLe + sin(alpha)*cRe,             y0 - cos(alpha)*cRe - sin(alpha)*cLe]
        return [right_front,right_rear,left_front,left_rear]
    
    def isConform(self):
        boolean = super().isConform()     

        #We verify that we have at least 2 coordinate in position
        boolean = boolean and (len(self.position) ==2 or len(self.position) ==3)
        
        #We check the unit. It should be m, t or f
        boolean = boolean and (self.unit.replace(" ","").lower() in ["t","f","m"])

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

    #This method create a group which contains all the components in comp
    def createGroup(self,name : str, *comp: Component):
        if type(comp[0]) != Device:
            pass
        else:
            group = Group(self.name + "." + name)
            for compo in comp:
                group.addComponent(compo)
                self.components.append(group)

    def getFloorDimensions(self):
        """Returns the floor area of a given component."""
        if(self.rotation == "rear" or self.rotation == "front"):
            return self.size[0],self.size[1]
        elif(self.rotation == "top" or self.rotation == "bottom"):
            return self.size[0],self.size[2]
        elif(self.rotation == "left" or self.rotation == "right"):
            return self.size[1],self.size[2]
            
    def possible_next_to(self):
        positions = []
        if(self.rotation == "rear" or self.rotation == "front"):
            width = self.size[0]
            length = self.size[1]
        elif(self.rotation == "top" or self.rotation == "bottom"):
            width = self.size[0]
            length = self.size[2]
        elif(self.rotation == "left" or self.rotation == "right"):
            width = self.size[1]
            length = self.size[2]
                