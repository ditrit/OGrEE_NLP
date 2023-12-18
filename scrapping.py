import re
import ogree_wiki as wiki

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

