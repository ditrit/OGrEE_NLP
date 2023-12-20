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
            allCommand += re.findall("\\+[A-Za-z]*:[\\w/]*[@\n]", line)
            line = commands.readline()

    # for each command, cut the string and put the name as key and the entity type as value. Ex : "/P/BASIC" : "site"
    for command in allCommand:
        separatedCommand = command.split(":")
        if separatedCommand[0][1:] in ENTITIES_FROM_MIN.keys():
            separatedCommand[0] = separatedCommand[0][0] + ENTITIES_FROM_MIN[separatedCommand[0][1:]]
        entityWithName[separatedCommand[1][:-1]] = separatedCommand[0][1:]

    return entityWithName

def getSimilarityInName(name1 : str, name2 : str) -> str:
    """Returns the similarity in the name of two elements, this similarity has to be a letter or a group of letters, it cannot be an integer"""
    l1, l2 = list(name1), list(name2)
    similarity = ""
    k = 0
    n = min(len(l1),len(l2))
    while k < n and l1[k] == l2[k] and not (l1[k].isnumeric() and l2[k].isnumeric()):
        similarity += l1[k]
        k +=1
    return similarity

def getSimilarityInList(namesToCompare : list) -> str:
    """Returns the similarity between the two last elements of a list sharing at least one alphabet character"""
    k = len(namesToCompare) - 1
    similarity = ""
    while len(similarity) < 1 and k > 0:
        similarity = getSimilarityInName(namesToCompare[k-1], namesToCompare[k])
        k -= 1
    return similarity

def incrementNumber(nameToIncrement : str) -> str:
    """Returns an automatically incremented name with the format X(letters)0(n times)p where p is an integer"""
    a, b = re.match('(\\D*)(\\d+)', nameToIncrement).groups()
    return f"{a}{int(b)+1:0{len(b)}d}"

def incrementLetter(nameToIncrement : str) -> str:
    """Increments the letter in the last part of a name following the alphabetical order"""
    similarPart = nameToIncrement[:-1]
    letterToIncrement = nameToIncrement[-1]
    if letterToIncrement not in ascii_letters:
        # we consider that if the last part of the nameToIncrement is not a letter this function should not have been called
        raise ValueError("The name {} cannot be incremented to create a default name".format(letterToIncrement))
    if letterToIncrement in ['z','Z']:
        raise ValueError("We cannot increment further than the last letter of the alphabet")
    return similarPart + ascii_letters[ascii_letters.index(letterToIncrement) + 1]


def incrementName(nameToIncrement : str) -> str:
    """Returns an incremented version of a name, may it be with a letter or a number at the end. We consider that the preliminary work of selection of the name has been done"""
    if nameToIncrement[-1].isnumeric():
        return incrementNumber(nameToIncrement)
    else:
        return incrementLetter(nameToIncrement)

def createDefaultName(typeOfElement : str, parentName : str, entities : dict) -> str:
    """Creates a default name thanks to the type of element we are creating, the name of the parent containing the element and a dictionnary of all existing entities"""
    # we first determine if there already are entities with the same type and with the same parent, and we sort the list obtained
    similarEntities =  [element.split("/")[-1] for element in entities.keys() if entities[element] == typeOfElement and parentName == getParentName(element)]
    similarEntities.sort()
    print("Those are the entities with the same type and parent : ", similarEntities)
    incrementalName = []
    defaultName = ""
    if len(similarEntities) == 0:
        # we consider that someone might be trying to create a room in a room for example
        result = input("Are you sure you want to create a {} in {} ? (y/n) : ".format(typeOfElement, parentName)).lower()
        if result == "y":
            # the command below works if we are sure that the typeOfElement can be added in the parent given
            defaultName = typeOfElement + "A"
        elif result == "n":
            # we do nothing
            print("The creation has been cancelled")
        else:
            # the answer given has not the right type
            raise ValueError("The answer you gave was incorrect, the process has been terminated")
    elif len(similarEntities) == 1:
        existingElement = similarEntities[0]
        if len(existingElement) == 1:
            # we consider that it might be a letter to increment, we assume that it cannot be just a number
            defaultName = incrementLetter(existingElement)
        else:
            # we make a name based on the name of the existing element by adding 2 at the end
            defaultName = existingElement + "2"
    else:
        # we try to extract a pattern from the name of the last objects with the same type and the same parent
        similarPart = getSimilarityInList(similarEntities)
        if similarPart == "" :
            #in the extreme case where in all the elements there is not even one similar letter we create a name based on the type
            defaultName = typeOfElement + "A"
            if defaultName in similarEntities:
                #if the name already exists, we only increment it, and we know it is correct because otherwise a similarity would have been detected
                defaultName = incrementName(defaultName)
        # this pattern is the first part of the name, we assume that it is identic in general for similar objects (chassis are named 'chassisn' where n is an integer)
        k = len(similarEntities) - 1
        # we go through the list of similar entities from the end to have a name 
        while k >= 0 and similarEntities[k][:len(similarPart)] == similarPart:
            incrementalName.append(similarEntities[k])
            k -= 1
        defaultName = incrementName(incrementalName[0])
    return defaultName

if __name__ == "__main__":
    EXISTING_ENTITY_NAMES = scrapAllName("OCLI_files/DEMO_BASIC.ocli")
    #those commands are tests to understand the behaviour of the function
    print("The default name given is : ", createDefaultName("site", "/P", EXISTING_ENTITY_NAMES))
    print("The default name given is : ", createDefaultName("building", "/P/BASIC", EXISTING_ENTITY_NAMES))
    print("The default name given is : ", createDefaultName("room", "/P/BASIC/A", EXISTING_ENTITY_NAMES))
    print("The default name given is : ", createDefaultName("rack", "/P/BASIC/A/R1", EXISTING_ENTITY_NAMES))
    print("The default name given is : ", createDefaultName("device", "/P/BASIC/A/R1/A02", EXISTING_ENTITY_NAMES))
    print("The default name given is : ", createDefaultName("device", "/P/BASIC/A/R1/A02/chassis01", EXISTING_ENTITY_NAMES))
    #the command below is supposed to be a problem since we try to create a name for a room in  a room
    print("The default name given is : ", createDefaultName("room", "/P/BASIC/A/R1", EXISTING_ENTITY_NAMES))
