import re, json, sys
from Room import Room
from Rack import Rack
from pulp import *
from math import *

######################################## Methods to place an object next to a sibling ###################################################
def get_line_coeff(p1,p2):
    """ return a and b for an equation ax+b = y knowing two solutions of the equation"""
    # print(p1,p2)
    if p1[0] == p2[0] and p1[1] == p2[1]:
        raise ValueError("Same point given two times")
    else:
        if p1[0] == p2[0]:
            return 'vertical'
        else:
            return (float((p2[1]-p1[1])/(p2[0]-p1[0])) , float((p1[1]*p2[0]-p1[0]*p2[1])/(p2[0]-p1[0])))

class Problem():
    def __init__(self,rack,room):
        self.rack=rack
        self.room=room
        self.problem = LpProblem(name = "Positionning", sense=LpMinimize)
        if(self.room.vertices):
            self.upperBound = 1000000 * max([vertex[1] for vertex in self.room.vertices]) #arbitrary, just needs to be big enough
            self.x = LpVariable("x",lowBound = min([vertex[0] for vertex in self.room.vertices]),upBound = max([vertex[0] for vertex in self.room.vertices]))
            self.y = LpVariable("y",lowBound = min([vertex[1] for vertex in self.room.vertices]),upBound = max([vertex[1] for vertex in self.room.vertices]))
            self.vertices = [(LpVariable("x"+str(i),lowBound = min([vertex[0] for vertex in self.room.vertices]),upBound = max([vertex[0] for vertex in self.room.vertices]))
            ,LpVariable("y"+str(i),lowBound = min([vertex[1] for vertex in self.room.vertices]),upBound = max([vertex[1] for vertex in self.room.vertices])))
            for i in range(1,5)]
        else:
            self.upperBound = 1000000 * (max(self.room.size)+max(self.room.position)) #arbitrary, just needs to be big enough
            self.x = LpVariable("x",lowBound = self.room.position[0]-max(self.room.size),upBound = self.room.position[0]+max(self.room.size))
            self.y = LpVariable("y",lowBound = self.room.position[1]-max(self.room.size),upBound = self.room.position[1]+max(self.room.size))
            self.vertices = [(LpVariable("x"+str(i),lowBound = self.room.position[0]-max(self.room.size),upBound = self.room.position[0]+max(self.room.size))
            ,LpVariable("y"+str(i),lowBound = self.room.position[1]-max(self.room.size),upBound = self.room.position[1]+max(self.room.size)))
            for i in range(1,5)]
        self.set_vertices()

    def set_vertices(self):
        L, l = self.rack.getFloorDimensions()
        alpha = self.rack.rotation[2]
        cFr, cRe, cLe, cRi = self.rack.clearance[0], self.rack.clearance[1], self.rack.clearance[2], self.rack.clearance[3]
        self.problem += (self.vertices[0][0] == self.x - cos(alpha)*cLe + sin(alpha)*cRe)
        self.problem += (self.vertices[0][1] == self.y - cos(alpha)*cRe - sin(alpha)*cLe)
        self.problem += (self.vertices[1][0] == self.x + cos(alpha)*(L + cRi) - sin(alpha)*(l + cFr)) 
        self.problem += (self.vertices[1][1] == self.y + cos(alpha)*(l + cFr) + sin(alpha)*(L + cRi))
        self.problem += (self.vertices[2][0] == self.x + cos(alpha)*(L + cRi) + sin(alpha)*cRe)
        self.problem += (self.vertices[2][1] == self.y - cos(alpha)*cRe + sin(alpha)*(L + cRi))
        self.problem += (self.vertices[3][0] == self.x - cos(alpha)*cLe - sin(alpha)*(l + cFr))
        self.problem += (self.vertices[3][1] == self.y + cos(alpha)*(l + cFr) - sin(alpha)*cLe)
    
    def is_param_between(self,x1,x2,letter : str, number : 1|2|3|4 ):
        """creates a variable equal to 1 if the given parameter is between x1 and x2 """
        c = LpVariable(letter + str(number)+"_between(" + str(x1) + "," + str(x2) + ")", cat=LpBinary) #equals 1 if self.x is between x1 and x2 0 else
        print(c)
        print()
        index = 0 if letter == 'x' else 1

        # c = 1 if parameter<=x2 else 0 ############################
        self.problem += (self.vertices[number-1][index] - x2 <= (1-c)*self.upperBound)
        self.problem += (x2 - self.vertices[number-1][index] <= c*self.upperBound)
        ####################################################

        # c = 1 if parameter>=x1 else 0 ############################
        self.problem += (self.vertices[number-1][index] - x1 <= c*self.upperBound)
        self.problem += (x1 - self.vertices[number-1][index] <= (1-c)*self.upperBound)
        ####################################################

    def ifThen_y_and_x_eq(self,number : 1|2|3|4, x1, x2, y1, y2):
        """If x_number is between x1 and x2 and y_number is between y1 and y2 then, the position is such that y = ax+b 
        (with a and b in terms of x1, x2, y1, y2)"""
        # print(x1,y1,x2,y2)
        print(get_line_coeff((x1,y1),(x2,y2)))
        if(get_line_coeff((x1,y1),(x2,y2))) == 'vertical':
            cy = self.problem.variablesDict()['y' + str(number)+"_between(" + str(y1) + "," + str(y2) +")"]
            print(cy)
            self.problem += (self.vertices[number-1][0]>=x1-self.upperBound*(1-cy))
            self.problem += (self.vertices[number-1][0]<=x2+self.upperBound*(1-cy))
        elif(get_line_coeff((x1,y1),(x2,y2))[0]) == 0:
            cx = self.problem.variablesDict()["x"+str(number)+"_between(" + str(x1) + "," + str(x2)+")"]
            print(cx)
            self.problem += (self.vertices[number-1][1]>=y1-self.upperBound*(1-cx))
            self.problem += (self.vertices[number-1][1]<=y2+self.upperBound*(1-cx))
        else:
            param = get_line_coeff((x1,y1),(x2,y2))
            cx = self.is_param_between(x1,x2,'x',number)
            cy = self.is_param_between(y1,y2,'y',number)
            d = LpVariable('x' + str(number)+',y' + str(number)+"andBetween" + str(x1) + "," + str(x2) + "," + str(y1) + "," + str(y2), cat=LpBinary) #equals 1 if cx and cy are equal to 1
            ### d = cx and cy ###
            self.problem += (d >= cx + cy - 1)
            ##################### d = 1 (i.e cx and cy =1) implies y = ax+b
            self.problem += (-self.upperBound*(1-d)<=param[0]*self.vertices[number-1][0]+param[1]-self.vertices[number-1][1])
            self.problem += (param[0]*self.vertices[number-1][0]+param[1]-self.vertices[number-1][1]<=self.upperBound*(1-d))
    
    def constraintWithin(self):
        "adds constraints so that rack vertices are within the dimensions of the room"
        ## TO DO : lowerbounds not workin =)
        vertices = self.room.get_vertices()
        n = len(vertices)
        # if vertices[0][1]<vertices[1][1]:
        #     rotation = 'clockwise'
        #     going_up = True
        # if vertices[0][1]==vertices[1][1]:
        #     if vertices[0][0]>=vertices[1][0]:
        #         rotation = 'clockwise'
        #         going_up = True
        #     else :
        #         rotation = 'counterclockwise'
        #         going_up = False
        # else:
        #     rotation = 'counterclockwise'
        #     going_up = False
        # if rotation == 'clockwise':
        #     for i in range(n):
        #         if vertices[i%n][1]<vertices[(i+1)%n][1]:
        #             going_up = True
        #             if get_line_coeff(vertices[i%n],vertices[(i+1)%n])=='vertical':
        #                 for vertex in self.vertices:
        #                     self.problem += (vertex[0]>=vertices[i][0])
        #             else:
        #                 for vertex in self.vertices:
        #                     self.problem += (vertex[1]<=get_line_coeff(vertices[i%n],vertices[(i+1)%n])[0]*vertex[0]+get_line_coeff(vertices[i%n],vertices[(i+1)%n])[1])
        #         if vertices[i%n][1]>vertices[(i+1)%n][1]:
        #             going_up = False
        #             if get_line_coeff(vertices[i%n],vertices[(i+1)%n])=='vertical':
        #                 for vertex in self.vertices:
        #                     self.problem += (vertex[0]<=vertices[i][0])
        #             else:
        #                 for vertex in self.vertices:
        #                     self.problem += (vertex[1]>=get_line_coeff(vertices[i%n],vertices[(i+1)%n])[0]*vertex[0]+get_line_coeff(vertices[i%n],vertices[(i+1)%n])[1])
        #         else:
        #             if going_up:
        #                 for vertex in self.vertices:
        #                     self.problem += (vertex[1]<=vertices[i][1])
        #             else:
        #                 for vertex in self.vertices:
        #                     self.problem += (vertex[1]>=vertices[i][1])
        for i in range(n):
            for vertex in self.vertices:
                self.problem += (
                    ((vertex[1]-vertices[i][1])*(vertices[(i+1)%n][0]-vertices[i][0]))-
                    ((vertex[0]-vertices[i][0])*(vertices[(i+1)%n][1]-vertices[i][1]))
                )

    def aim_point(self,p):
        """Defines the point we want to be the closest to"""
        # we want to minimize the distance between the two points
        distx = LpVariable("distx", lowBound = 0)
        disty = LpVariable("disty", lowBound = 0)
        #distx = |x-x0|
        self.problem += (distx >= self.x-p[0])
        self.problem += (distx >= p[0]-self.x)
        #disty = |y-y0|
        self.problem += (disty >= self.y-p[1])
        self.problem += (disty >= p[1]-self.y)
        #minimize |x-x0|+|y-y0|
        self.problem.setObjective(distx+disty)
    
    def showSolution(self):
        # LpSolverDefault.msg = 1
        self.problem.solve()
        """Prints the solution for x and y"""
        return self.x.value(), self.y.value()

def set_positionning_problem(rack1,rack2,room,point):
    """set up the problem with all variables and constraints having rack1 and rack2 in room 
    where rack1 is already set in the room and we try to stick rack2 to it"""
    problem = Problem(rack2,room)
    vertices = rack1.get_vertices()
    # print(vertices)
    x,y = [],[]
    for i in range(len(vertices)):
        x.append(vertices[i][0])
        y.append(vertices[i][1])
    for i in range(len(vertices)):
        problem.is_param_between(x[0],x[1],'x',i+1)
        problem.is_param_between(y[0],y[3],'y',i+1)
    # stick x1
    problem.ifThen_y_and_x_eq(1,min(x[2],x[3]),max(x[2],x[3]),min(y[2],y[3]),max(y[2],y[3]))
    problem.ifThen_y_and_x_eq(1,min(x[1],x[2]),max(x[1],x[2]),min(y[1],y[2]),max(y[1],y[2]))
    # stick x2
    problem.ifThen_y_and_x_eq(2,min(x[3],x[0]),max(x[3],x[0]),min(y[3],y[0]),max(y[3],y[0]))
    problem.ifThen_y_and_x_eq(2,min(x[2],x[3]),max(x[2],x[3]),min(y[2],y[3]),max(y[2],y[3]))
    # stick x3
    problem.ifThen_y_and_x_eq(3,min(x[1],x[0]),max(x[1],x[0]),min(y[1],y[0]),max(y[1],y[0]))
    problem.ifThen_y_and_x_eq(3,min(x[0],x[3]),max(x[0],x[3]),min(y[0],y[3]),max(y[0],y[3]))
    # stick x4
    problem.ifThen_y_and_x_eq(4,min(x[1],x[2]),max(x[1],x[2]),min(y[1],y[2]),max(y[1],y[2]))
    problem.ifThen_y_and_x_eq(4,min(x[1],x[0]),max(x[1],x[0]),min(y[1],y[0]),max(y[1],y[0]))
    # the rack has to stay in the room
    # print(room.isConvex())
    if room.isConvex():
        problem.constraintWithin()
    else:
        print("Couldn't perform constraint within. The room isn't convex")
    #set the objective
    problem.aim_point(point)
    return problem.showSolution()

if __name__ == "__main__":
    room = Room('A01',(0,0),0,(500,500))
    rack1 = Rack('R1',(100,100),'t',[0,0,0],[2,1,3])
    vertices = rack1.get_vertices()
    # print(get_line_coeff(vertices[0],vertices[1]))
    rack2 = Rack('R2',(300,300),'t',[0,0,0],[2,1,3])
    point = (-610,-5000)
    # print(rack1.get_vertices())
    print(set_positionning_problem(rack1,rack2,room,point))


### OLD #############################################################################################################################
# def find_commands(file_name):
#     file = open(file_name, "r")
#     text = file.read()
#     pattern = re.compile(r'^[+.].*', re.MULTILINE)
#     return pattern.findall(text)
# print(find_commands('DEMO.BASIC.ocli'))
# def name_to_object(name : str, file_name : str):
#     text = open(file_name,'r').read()
#     pattern = re.compile(fr'.*{re.escape(name)}.*', flags=re.MULTILINE)
#     commands_with_object = pattern.findall(text)
#     for command in commands_with_object :
#         print(command)
#         if(re.search(r'^[+].*',command)):
#             obj,params = re.split(":",command)
#             if(re.search("bd",obj) or re.search("building",obj)):
#                 name,pos,rot,size = re.split("@",params)
#                 pos = re.split(",",pos.replace("[","").replace("]",""))
#                 size = re.split(",",size.replace("[","").replace("]",""))
#                 return ['Building',name,[float(coord) for coord in pos],float(rot),[float(dim) for dim in size]]
#             if(re.search("tn",obj) or re.search("tenant",obj)):
#                 name,color = re.split("@",params)
#                 return ['Tenant',name,color]
#             if(re.search("si",obj) or re.search("site",obj)):
#                 return ['Site',name]
#             if(re.search("ro",obj) or re.search("room",obj)):
#                 params = re.split("@",params)
#                 pos = re.split(",",params[1].replace("[","").replace("]",""))
#                 size = re.split(",",params[3].replace("[","").replace("]",""))
#                 if(len(params)==6):
#                     return ['Room',name,[float(coord) for coord in pos],float(rot),[float(dim) for dim in size],params[4],params[5]]
#                 else : 
#                     return ['Room',name,[float(coord) for coord in pos],float(params[2]),[float(dim) for dim in size],params[4]]
#             if(re.search("rk",obj) or re.search("rack",obj)):
#                 name,pos,unit,rot,size = re.split("@",params)
#                 pos = re.split(",",pos.replace("[","").replace("]",""))
#                 rot = convert_to_angles(rot)
#                 size = re.split(",",size.replace("[","").replace("]",""))
#                 return ['Rack',name,[float(coord) for coord in pos],unit,rot,[float(dim) for dim in size]]

# def convert_to_angles(rot : str):
#     if(not re.findall("\d", rot)):
#         """
#         "front": [0, 0, 180]
#         "rear": [0, 0, 0]
#         "left": [0, 90, 0]
#         "right": [0, -90, 0]
#         "top": [90, 0, 0]
#         "bottom": [-90, 0, 0]
#         """
#         match rot:
#             case "front":
#                 return [0,0,180]
#             case "rear":
#                 return [0, 0, 0]
#             case "left": 
#                 return [0, 90, 0]
#             case "right": 
#                 return [0, -90, 0]
#             case "top": 
#                 return [90, 0, 0]
#             case "bottom": 
#                 return [-90, 0, 0]
#     else :
#         return [float(angle) for angle in re.split(",",rot.replace("[","").replace("]",""))]