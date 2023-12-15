from items.Component import Component
import json
# from items.tools import *
# from items.ogree_adapter import *

class Room(Component) :
    def __init__(self,name,position,rotation,size):
        super().__init__(name,position,rotation,size)
    
    @classmethod
    def create_room_from_template(Room,name : str,position : list,rotation : list,template):
        with open(template) as json_file :
            try:

                template = json.loads(json_file.read().strip())
                size = template['sizeWDHmm']
                return Room(name,position,rotation,size)
            except BaseException as e:
                print('The file contains invalid JSON')
            

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name},position={self.position},rotation={self.rotation},size={self.size})"