from Component import Component

class Group(Component):

    @staticmethod
    def changeName(compName : str) -> str: 
        indexLastPoint = compName.rfind(".")
        if(indexLastPoint) ==-1 :
            return compName
        return compName[indexLastPoint+1:]


    def __init__(self, name : str,*components : Component | str):
        self.name = name
        self.components = []
        #We need to change the name of the components if the components aren't a string
        for comp in components:
            if type(comp) != str:
                #We need to add a name
                self.components.append(self.changeName(comp.name))
            else:
                self.components.append(self.changeName(comp))
    
    def isConform(self):
        return True #The fact that the name is a string and the list of component is composed with components is always true with
                    #the init
    
    def addComponent(self, comp : Component):
        self.components.append(self.changeName(comp.name))