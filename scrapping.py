import re
import ogree_wiki as wiki
from items.tools import getParentName
from string import ascii_letters

def scrapAllName(filename : str) -> dict:
    # dictionnary with minimized entity type as keys and full entity type as value. Ex : "si" : "site"
    ENTITIES_FROM_MIN = {value: key for key, value in wiki.ENTITIES.items()}

    allCommand = []
    entityWithName = dict()

    with open(filename, "r") as commands:
        line = commands.readline()

        # read all line and search for a creation command
        while line:
            if line[:2] == "//":
                line = commands.readline()
                continue
            allCommand += re.findall("\+[A-Za-z]*:[\w/]*[@\n]", line)
            line = commands.readline()

    # for each command, cut the string and put the name as key and the entity type as value. Ex : "/P/BASIC" : "site"
    for command in allCommand:
        separatedCommand = command.split(":")
        if separatedCommand[0][1:] in ENTITIES_FROM_MIN.keys():
            separatedCommand[0] = separatedCommand[0][0] + ENTITIES_FROM_MIN[separatedCommand[0][1:]]
        entityWithName[separatedCommand[1][:-1]] = separatedCommand[0][1:]

    return entityWithName

def getSimilarityInName(name1 : str, name2 : str) -> str:
    l1, l2 = list(name1), list(name2)
    similarity = ""
    k = 0
    n = min(len(l1),len(l2))
    while k < n and l1[k] == l2[k] and not (l1[k].isnumeric() and l2[k].isnumeric()):
        similarity += l1[k]
        k +=1
    return similarity

def incrementNumber(nameToIncrement : str) -> str:
    """Returns an automatically incremented name with the format X(letters)0(n times)p where p is an integer"""
    a, b = re.match('(\\D*)(\\d+)', nameToIncrement).groups()
    return f"{a}{int(b)+1:0{len(b)}d}"

def incrementLetter(nameToIncrement : str) -> str:
    similarPart = nameToIncrement[:-1]
    letterToIncrement = nameToIncrement[-1]
    if letterToIncrement in ['z','Z']:
        raise ValueError("We cannot increment further than the last letter of the alphabet")
    return similarPart + ascii_letters[ascii_letters.index(letterToIncrement) + 1]


def increment(nameToIncrement : str) -> str:
    if nameToIncrement[-1].isnumeric():
        return incrementNumber(nameToIncrement)
    else:
        return incrementLetter(nameToIncrement)

def createDefaultName(typeOfElement : str, parentName : str, entities : dict) -> str:
    """Creates a default name thanks to specified parameters"""
    # we first determine if there already are entities with the same type and with the same parent
    similarEntities =  [element.split("/")[-1] for element in entities.keys() if entities[element] == typeOfElement and parentName == getParentName(element)]
    incrementalName = []
    if len(similarEntities) == 0:
        return similarEntities
    elif len(similarEntities) == 1:
        existingElement = similarEntities[1]
        if len(existingElement) == 1:
            #TODO : we consider that it might be a letter to increment
            pass
        else:
            #TODO : we make a whole different name, based on the type of object and the existing name
            pass
    else:
        # we try to extract a pattern from the name of the objects with the same type and the same parent
        similarPart = getSimilarityInName(similarEntities[0],similarEntities[1])
        # this pattern is the first part of the name, we assume that it is identic in general for similar objects (chassis are named 'chassisn' where n is an integer)
        k = 0
        while k < len(similarEntities) and similarEntities[k][:len(similarPart)] == similarPart:
            incrementalName.append(similarEntities[k])
            k += 1
    lastName = incrementalName[-1]
    return increment(lastName)

if __name__ == "__main__":
    EXISTING_ENTITY_NAMES = scrapAllName("DEMO_BASIC.ocli")
    print(createDefaultName("room", "/P/BASIC/A", EXISTING_ENTITY_NAMES))
    print(incrementLetter("chassisA"))