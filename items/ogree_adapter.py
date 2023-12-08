import json
from Room import room


def getNameFromFile(fileDict : dict) -> str:
    """Returns the name of a room from the dict representing the room in json"""
    return fileDict.get("slug")


def createRoom(filename : str):
    """Creates a Room instance from a json file with a template"""
    with open(filename, "r") as room:
        roomDescription = json.load(room)
    

if __name__ == "__main__":
    print(createRoom("demo/rooms/room-square1.json"))