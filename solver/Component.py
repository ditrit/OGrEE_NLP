import json
class Component:
    def __init__(self, name : str, position : list, rotation : list, size : list):
        self.name = name
        self.position = position
        self.size = size
        self.rotation = rotation

    @classmethod
    def create_from_template(Component,name : str,position : list,rotation : list,template):
        with open(template) as json_file :
            try:
                template = json.loads(json_file.read().strip())
                size = template['sizeWDHmm']
                return Component(name,position,rotation,size)
            except BaseException as e:
                print('The file contains invalid JSON')

    def __eq__(self, __value: object) -> bool:
        if (type(__value) != Component):
            raise TypeError("A component is exepcted.")
        return self.name == __value.name

    def getFloorArea(self):
        """Returns the floor area of a given component."""
        return self.size[0]*self.size[1]

    def set_param_from_template(template,param):
        with open(template) as json_file :
            try:
                template = json.load(json_file)
                parameter = template[param]
                return parameter
            except BaseException as e:
                print('The file contains invalid JSON')
                print(e)