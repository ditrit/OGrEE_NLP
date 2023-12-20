import re, json, sys
from Room import Room
from Rack import Rack
from math import *

eps = 1e-5

def distance(point1, point2):
    return sqrt((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)
class Rectangle():
    def __init__(self,pos,rot,size,clearance = [0,0,0,0,0,0]):
        self.position = pos
        if type(rot) == list and len(rot) == 3: #If the rectangle is a Rack, we consider only rotation on the plane
            self.rotation = rot[2]
        else:
            self.rotation = rot
        self.size = size
        self.clearance = clearance

    def get_vertices(self):
        x0,y0 = self.position
        L, l = self.size[0], self.size[1]
        cFr, cRe, cLe, cRi = self.clearance[0], self.clearance[1], self.clearance[2], self.clearance[3]
        right_front = [x0 + cos(self.rotation)*(L + cRi) + sin(self.rotation)*cRe,       y0 - cos(self.rotation)*cRe + sin(self.rotation)*(L + cRi)]
        right_rear =  [x0 + cos(self.rotation)*(L + cRi) - sin(self.rotation)*(l + cFr), y0 + cos(self.rotation)*(l + cFr) + sin(self.rotation)*(L + cRi)]
        left_front =  [x0 - cos(self.rotation)*cLe - sin(self.rotation)*(l + cFr),       y0 + cos(self.rotation)*(l + cFr) - sin(self.rotation)*cLe]
        left_rear =   [x0 - cos(self.rotation)*cLe + sin(self.rotation)*cRe,             y0 - cos(self.rotation)*cRe - sin(self.rotation)*cLe]
        return [right_front,right_rear,left_front,left_rear]
    
    def isInside(self, rect):
        lstVertices = self.get_vertices()
        n = len(lstVertices)
        lstRoomVertices = rect.get_vertices()
        m = len(lstRoomVertices)
        for i in range(n):
            for j in range(m):
                #Vertices of the room for the test
                x1 = lstRoomVertices[j]
                x2 = lstRoomVertices[(j+1)%m]
                #Vertices of the rack for the test
                p1 = lstVertices[i]
                p2 = lstVertices[(i+1)%n]
                if ((p1[1]-x1[1])*(x2[0]-x1[0])-(p1[0]-x1[0])*(x2[1]-x1[1]))*((p2[1]-x1[1])*(x2[0]-x1[0])-(p2[0]-x1[0])*(x2[1]-x1[1])) < 0 :
                    return False 
        return True
    
    def setRotationSize(self, rack):
        L, l = self.size[0], self.size[1]
        L2, l2 = rack.size[0], rack.size[1]
        if ((L > l and L2 < l2) or (L < l and L2 > l2)):
            self.size = [l, L]
        self.rotation = rack.rotation

    def testCorner(self, room, rack):
        lstVertices = rack.get_vertices
        tempLst = []
        self.position = [lstVertices[0][0], lstVertices[0][1]-self.size[1]]
        if(not self.isInside(room)):
            tempLst.append(0)
        self.position = [lstVertices[1][0], lstVertices[1][1]]
        if(not self.isInside(room)):
            tempLst.append(1)
        self.position = [lstVertices[2][0]-self.size[0], lstVertices[2][1]]
        if(not self.isInside(room)):
            tempLst.append(2)
        self.position = [lstVertices[3][0]-self.size[0], lstVertices[3][1]-self.size[1]]
        if(not self.isInside(room)):
            tempLst.append(3)
        return tempLst
    
    def getCenter(self):
        lstVertices = self.get_vertices
        return [(lstVertices[0][0]+lstVertices[2][0])/2, (lstVertices[0][1]+lstVertices[2][1])/2]
    def setPosFromCenter(self, point):
        return [point.position[0]-self.size[0]*cos(self.rotation)/2+self.size[1]*sin(self.rotation)/2, point.position[1]-self.size[1]*cos(self.rotation)/2-self.size[0]*sin(self.rotation)/2]

    def placeNearWall(self, room, rack):
        centerPointRack = rack.getCenter()
        lstVerticesRoom = room.get_vertices()
        centerPoint1 = [centerPointRack[0] - (self.size[1]+rack.size[1])/2*sin(self.rotation), centerPointRack[1] + (self.size[1]+rack.size[1])/2*cos(self.rotation)]
        centerPoint2 = [centerPointRack[0] + (self.size[1]+rack.size[1])/2*sin(self.rotation), centerPointRack[1] - (self.size[1]+rack.size[1])/2*cos(self.rotation)]
        if sum([distance(centerPoint1, vertice) for vertice in lstVerticesRoom]) > sum([distance(centerPoint2, vertice) for vertice in lstVerticesRoom]): 
            self.position = self.setPosFromCenter(centerPoint2)
        else:
            self.position = self.setPosFromCenter(centerPoint1)

    def placeRack(self, room, rack):
        self.setRotationSize(rack)
        posIni = self.position
        testCorner = self.testCorner(room, rack)
        if(len(testCorner) > 0):
            if(testCorner == 2):
                pass
            else:
                pass
        else:
            self.placeNearWall(room, rack)

if __name__ == "__main__":
    room = Room('A01',(0,0),0,(500,500)) #Room in whick we want to put the rack
    rack1 = Rack('R1',(100,100),'t',[0,0,0],[2,1,3]) #Rack already fixed
    rack2 = Rack('R2',(300,300),'t',[0,0,0],[2,1,3]) #Rack we want to add
    roomRect = Rectangle(room.position, room.rotation, room.size)
    rackRect1 = Rectangle(rack1.position, rack1.rotation, rack1.size, rack1.clearance)
    rackRect2 = Rectangle(rack2.position, rack2.rotation, rack2.size, rack2.clearance)
    print(rack1.rotation)
    print(rackRect1.rotation)
    print(rackRect1.get_vertices())
    rackRect2.placeRack(roomRect, rackRect2)
