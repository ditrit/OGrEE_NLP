
from Component import Component

import json

# from items.tools import *
# from items.ogree_adapter import *

def produit_vectoriel(u, v):
        return u[0] * v[1] - u[1] * v[0]

class Room(Component) :
    def __init__(self,name,position,rotation,size,technical_area = [0,0,0,0],reserved_area = [0,0,0,0],separators = {},pillars = {},corridor = {}, vertices = []):
        super().__init__(name,position,rotation,size)
        self.technical_area = technical_area
        self.reserved_area = reserved_area
        self.separators = separators 
        self.pillars = pillars
        self.vertices = vertices
    
    @classmethod
    def create_from_template(Room,name : str,position : list,rotation : list,template,technical_area = [0,0,0,0],reserved_area = [0,0,0,0],separators = {},pillars = {},vertices = []):
        size = super().set_size_from_template(template)
        return Room(name,position,rotation,size,technical_area,reserved_area,separators,pillars,vertices) 

    def addPillar(self,name : str, centerXY : list, sizeXY : list, rotation : float):
        self.pillars[name] = {"centerXY" : centerXY, "sizeXY" : sizeXY, "rotation" : rotation}
    
    def addSeparator(self,name : str,startPos : list,endPos : list, typeOfSeparator):
        self.separators[name] = {"startPos" : startPos, "endPos" : endPos, "type" : typeOfSeparator}

    def addCorridor(self,name : str,pos : list,unit : list, rotation : str | list, size : list, temperature : str):
        pass


    def set_vertices_from_template(template):
        return super().set_param_from_template(template,'vertices')

    def isConvex(self):
        if not self.vertices:
            return True
        else :
            n = len(self.vertices)
            if n < 3:
                # Un polygone avec moins de 3 sommets n'est pas considéré comme convexe.
                return False
            for i in range(n):
                # Sélectionnez trois points consécutifs.
                A = self.vertices[i]
                B = self.vertices[(i + 1) % n]
                C = self.vertices[(i + 2) % n] 
                # Calculez le produit vectoriel pour chaque paire consécutive.
                produit = produit_vectoriel((B[0] - A[0], B[1] - A[1]), (C[0] - B[0], C[1] - B[1]))     
                # Vérifiez si le produit vectoriel change de signe.
                if produit <= 0:
                    return False

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name},position={self.position},rotation={self.rotation},size={self.size})"