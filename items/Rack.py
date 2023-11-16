class Rack:
    def __init__(self, position : list, unit : str, rack_rotation : str | list, size : list, template : str = None):
        self.position = position
        self.unit = unit
        self.rack_rotation = rack_rotation
        self.size = size
        self.template = template
    
    def isConform(self):
        boolean = True
