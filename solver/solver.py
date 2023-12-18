import re, json, sys
from Room import Room
from Rack import Rack
from pulp import LpVariable, LpProblem, LpBinary

######################################## Methods to place an object next to a sibling ###################################################
def get_line_coeff(p1,p2):
    """ return a and b for an equation ax+b = y knowing two solutions of the equation"""
    if p1[0] == p2[0] and p1[1] == p2[1]:
        raise ValueError("Same point given two times")
    else:
        if p1[0] == p2[0]:
            return 'vertical line'
        else:
            return (float((p2[1]-p1[1])/(p2[0]-p1[0])) , float((p1[1]*p2[0]-p1[0]*p2[1])/(p2[0]-p1[0])))

class Problem():
    def __init__(self,rack,room):
        self.rack=rack
        self.room=room
        self.problem = LpProblem("Positionning", sense=LpMinimize)
        self.upperBound = 1000000 * max([vertex[1] for vertex in self.room.vertices]) #arbitrary, just needs to be big enough
        if(self.room.vertices):
            self.x = LpVariable("x",lowBound = min([vertex[0] for vertex in self.room.vertices]),upBound = max([vertex[0] for vertex in self.room.vertices]))
            self.y = LpVariable("y",lowBound = min([vertex[1] for vertex in self.room.vertices]),upBound = max([vertex[1] for vertex in self.room.vertices]))
            self.vertices = [(LpVariable("x"+str(i),lowBound = min([vertex[0] for vertex in self.room.vertices]),upBound = max([vertex[0] for vertex in self.room.vertices]))
            ,LpVariable("y"+str(i),lowBound = min([vertex[1] for vertex in self.room.vertices]),upBound = max([vertex[1] for vertex in self.room.vertices])))
            for i in range(1,5)]
        else:
            self.x = LpVariable("x",lowBound = self.room.position[0]-max(self.room.size),upBound = self.room.position[0]+max(self.room.size))
            self.y = LpVariable("y",lowBound = self.room.position[1]-max(self.room.size),upBound = self.room.position[1]+max(self.room.size))
            self.vertices = [(LpVariable("x"+str(i),lowBound = self.room.position[0]-max(self.room.size),upBound = self.room.position[0]+max(self.room.size))
            ,LpVariable("y"+str(i),lowBound = self.room.position[1]-max(self.room.size),upBound = self.room.position[1]+max(self.room.size)))
            for i in range(1,5)]

    def set_vertices():
        L, l = self.rack.getFloorDimensions()
        alpha = self.rack.rotation[2]
        cFr, cRe, cLe, cRi = self.rack.clearance[0], self.rack.clearance[1], self.rack.clearance[2], self.rack.clearance[3]
        self.problem += (self.vertices[2][0] == self.x + cos(alpha)*(L + cRi) + sin(alpha)*cRe)
        self.problem += (self.vertices[2][1] == self.y - cos(alpha)*cRe + sin(alpha)*(L + cRi))
        self.problem += (self.vertices[1][0] == self.x + cos(alpha)*(L + cRi) - sin(alpha)*(l + cFr)) 
        self.problem += (self.vertices[1][1] == self.y + cos(alpha)*(l + cFr) + sin(alpha)*(L + cRi))
        self.problem += (self.vertices[3][0] == self.x - cos(alpha)*cLe - sin(alpha)*(l + cFr))
        self.problem += (self.vertices[3][1] == self.y + cos(alpha)*(l + cFr) - sin(alpha)*cLe)
        self.problem += (self.vertices[0][0] == self.x - cos(alpha)*cLe + sin(alpha)*cRe)            
        self.problem += (self.vertices[0][1] == self.y - cos(alpha)*cRe - sin(alpha)*cLe)
    
    def is_x_between(self,x1,x2):
        """creates a variable equal to 1 if x is between x1 and x2 """
        c = LpVariable("between" + str(x1) + "," + str(x2), cat=LpBinary) #equals 1 if self.x is between x1 and x2 0 else
        # c = 1 if x<=x2 else 0 ############################
        self.problem += (self.x - x2 <= (1-c)*self.upperBound)
        self.problem += (x2 - self.x <= c*self.upperBound)
        ####################################################
        # c = 1 if x>=x1 else 0 ############################
        self.problem += (self.x - x1 <= c*self.upperBound)
        self.problem += (self.x1 - x <= (1-c)*self.upperBound)
        ####################################################

    def is_y_between(self,y1,y2):
        """creates a variable equal to 1 if y is between y1 and y2 """
        self.index += 1
        c = LpVariable("between" + str(y1) + "," + str(y2), cat=LpBinary) #equals 1 if self.x is between x1 and x2 0 else
        # c = 1 if y<=y2 else 0 ############################
        self.problem += (self.y - y2 <= (1-c)*self.upperBound)
        self.problem += (y2 - self.y <= c*self.upperBound)
        ####################################################

        # c = 1 if y>=y1 else 0 ############################
        self.problem += (self.y - y1 <= c*self.upperBound)
        self.problem += (self.y1 - y <= (1-c)*self.upperBound)
        ####################################################

    def ifThen_y_and_x(self, x1, x2, y1, y2):
        """If x is between x1 and x2 and y is between y1 and y2 then, the position is such that y = ax+b 
        (with a and b in terms of x1, x2, y1, y2)"""
        a,b = get_line_coeff((x1,y1),(x2,y2))
        cx = self.problem.variablesDict()["between" + str(x1) + "," + str(x2)]
        cy = self.problem.variablesDict()["between" + str(y1) + "," + str(y2)]
        d = LpVariable("andBetween" + str(x1) + "," + str(x2) + "," + str(y1) + "," + str(y2), cat=LpBinary) #equals 1 if cx and cy are equal to 1
        self.problem += (d >= cx + cy - 1)
        self.problem += (-self.upperBound*(1-d)<=a*self.x+b-self.y)
        self.problem += (a*self.x+b-self.y<=self.upperBound*(1-d))
    
    def aim_point(p):
        """Defines the point we want to be the closest to"""
        # we want to minimize the distance between the two points
        distx = LpVariable("distx", lowBound = 0)
        disty = LpVariable("disty", lowBound = 0)
        problem += (distx >= self.x-p[0])
        problem += (distx >= p[0]-self.x)
        problem += (disty >= self.y-p[1])
        problem += (disty >= p[1]-self.y)
        self.problem.setObjective(distx+disty)
    
    def showSolution():
        """Prints the solution for x and y"""
        return self.x.value(), self.y.value()

def set_positionning_problem(rack1,rack2,room,point):
    """set up the problem with all variables and constraints having rack1 and rack2 in room 
    where rack1 is already set in the room and we try to stick rack2 to it"""
    problem = Problem(rack1,room)
    rack1_vertices = rack1.get_vertices()
    n = len(rack1_vertices)
    for i in range(n):
        problem.is_x_between(rack1_vertices[i%n][0],rack1_vertices[(i+1)%n][0])
        problem.is_y_between(rack1_vertices[i%n][1],rack1_vertices[(i+1)%n][1])
        problem.ifThen_y_and_x(rack1_vertices[i%n][0],rack1_vertices[(i+1)%n][0],rack1_vertices[i%n][1],rack1_vertices[(i+1)%n][1])
    problem.aim_point(point)
    return problem.showSolution()



if __name__ == "main":
    # print(name_to_object("/P/BASIC/A/R1/A01",'DEMO.BASIC.ocli'))
    #path = 'C:\\Users\\lemoi\\Documents\\Cours\\Commande_Entreprise\\GitHub\\OGrEE_NLP\\items\\schneider-ns1000n.json'
    path = 'C:\\Users\\lemoi\\Documents\\Cours\\Commande_Entreprise\\GitHub\\OGrEE_NLP\\items\\2crsi-dryzone-debug.json'

    struct = {}

    with open(path, encoding = 'utf-8') as json_file:
        try:
            # print(json_file.read())
            template = json.load(json_file)  # 👈️ parse the JSON with load()
            print(template)
            size = template['sizeWDHmm']
            print(size)
        except BaseException as e:
            print('The file contains invalid JSON')
            print(e)

    room = Room.create_from_template('AAA',[0,0,0],[0,90,0],path)
    print(room)



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
