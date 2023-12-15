from Component import Component

class Tag(Component):

    #I don't know if a color can be a rgb
    def __init__(self, slug : str, color : str | list =None):
        if slug !=None:
            self.slug = slug.lower
        else:
            self.slug = slug
        if type(color) !=str:
            self.color = color
        else:
            self.color = color.lower
    
    def isConform(self):
        boolean = True
        boolean = boolean and self.slug !=None
        #If the input is a rgb color, the components of color should an int between 0 and 255
        if self.color !=None and isinstance(self.color,list):
            boolean = boolean and len(self.color) == 3

            for component in self.color:
                boolean = boolean and type(component) == int
                boolean = boolean and component > -1 and component < 256
        
        return boolean

