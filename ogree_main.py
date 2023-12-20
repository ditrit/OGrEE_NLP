import spacy
from spacy.tokens import Doc, Token
nlp = spacy.load("en_core_web_lg")

import numpy as np
import re
import importlib
import time
from typing import Optional
import os

import warnings
warnings.filterwarnings('ignore')

import ogree_wiki as wiki
import items.tools as tools
import scrapping
import getters_parameters as get
import initialization as init

ACTIONS_DEFAULT = {
                    "ACTION_POSITIVE" : ["make","build","put","place","add","insert"],
                    "ACTION_NEGATIVE" : ["remove", "delete"], 
                    "ALTERATION" : ["modify", "change","move","set","rename","rotate"]
                    }

ACTIONS_CLI = {
                "ACTION_POSITIVE" : "+",
                "ACTION_NEGATIVE" : "-"
                }

SIMILARITY_THRESHOLD = 0.5

PARAMETERS_DICT = {
            "name" : ["name","called"],
            "position" : ["position","at","located","posU","centered","centerXY","startPosition","startPos","endPosition",],
            "rotation" : ["rotation","turned","degree"],
            "size" : ["size","dimensions","height","sizeU","sizeXY"],
            "template" : ["template"],
            "axisOrientation" : ["axisOrientation", "axis", "orientation"],
            "unit" :  ["unit","floorUnit"],
            "slot" : ["slot"],
            "color" : ["color","usableColor","reservedColor","technicalColor"] + list(wiki.COLORS_HEX_BASIC.keys()), 
            "side" : ["side"],
            "temperature" : ["temperature","cold","warm"],
            "type" : ["type","wall","wireframe","plain"],
            # "reserved" : ["reserved"],
            # "technical" : ["technical"]
            }

DEFAULT_VALUE = {
    "tenant" : {"color" : "#FFFFFF"},
    "building" : {"position" : [0,0], "rotation" : 0},
    "room" : {"position" : [0,0], "rotation" : 0, "axisOrientation" : "+x+y", "floorUnit" : "t"},
    "rack" : {"position" : [0,0], "unit" : "t", "rotation" : [0,0,0]},
    "device" : {"position" : 0, "size" : 0},
    "corridor" : {"position" : [0,0], "rotation" : [0,0,0], "temperature" : "warm", "unit" : "t"},
    "tag" : {"color" : "#FFFFFF"},
    "separator" : {"type" : "wireframe"},
    "pillar" : {"position" : [0,0], "rotation" : 0}
}

CORRECT_NAMES = {
    "unit" : {
        "room" : "floorUnit"
    }
}

ENTITIES_FULL_NAME = {"entity" : list(wiki.ENTITIES.keys())}

KEY_WORDS_ALL = {**ENTITIES_FULL_NAME,  **PARAMETERS_DICT}

PARAMETERS_DICT_KEYS = PARAMETERS_DICT.keys()
ACTIONS_DEFAULT_KEYS = ACTIONS_DEFAULT.keys()

def findIndexMainSubject(processed_entry : Doc, dictioIndexKeyWords : dict, indexAction : int, indexMainEntity : int = None) -> int :

    def searchSubjectRecursive(processed_entry : Doc, currentIndex : int, testConformity, level : int = 0) -> (list|None):
        if level == 5 :
            return None
        if testConformity(processed_entry[currentIndex]) :
            return [(currentIndex, level)]
        else:
            childList = []
            for child in processed_entry[currentIndex].children :
                childResult = searchSubjectRecursive(processed_entry, child.i, testConformity, level+1)
                if childResult != None :
                    childList.extend(childResult)
            if bool(childList) == True : # if the list is not empty    
                minValue = min(childList, key=lambda x: x[1])[1]
                return [x for x in childList if x[1] == minValue] 
            return childList
    
    def testConformity(token : Token) -> bool :
        if ((token.i in dictioIndexKeyWords.keys() or token.pos_ == "NOUN") 
            and token.pos_ != "VERB"
            and not token.is_upper) :
            return True
        return False
    
    actionType = dictioIndexKeyWords[indexAction]

    result = searchSubjectRecursive(processed_entry, indexAction, testConformity)
    result = [x[0] for x in result]
    resultLength = len(result)

    if resultLength == 0 :
        raise Exception("Main request not identified")
    elif resultLength == 1 :
        return result[0]
    else : # if there are at least two tokens at the same length from the action

        if actionType == "ALTERATION" : # if alteration, prioritize known parameters
            resultOnlyParameters = [index for index in result if index in dictioIndexKeyWords.keys() and dictioIndexKeyWords[index] in PARAMETERS_DICT.keys()]
            if bool(resultOnlyParameters) :
                return resultOnlyParameters[0]
            else :
                return result[0]
            
        else : # prioritize entities
            resultOnlyEntity = [index for index in result if index in dictioIndexKeyWords.keys() and dictioIndexKeyWords[index] == "entity"]
            if not bool(resultOnlyEntity) :
                return result[0]
            elif len(resultOnlyEntity) == resultLength and indexMainEntity in result :
                return indexMainEntity
            else :
                return resultOnlyEntity[0]

def findAssociatedValue(processed_entry : Doc, INDEXES_MAIN : dict, TAKEN_INDEXES : list = [], parameter : str = None, attachedEntity : str = None) :

    def searchAssociatedKeyWordRecursive(processed_entry : Doc, currentIndex : int, level : int = 0) -> (list|None) :
        if level == 3 :
            return None
        if processed_entry[currentIndex].lower_ == "to" :
            return [(currentIndex, level)]
        else:
            childList = []
            for child in processed_entry[currentIndex].children :
                childResult = searchAssociatedKeyWordRecursive(processed_entry, child.i, level+1)
                if childResult != None :
                    childList.extend(childResult)
            if bool(childList) == True : # if the list is not empty    
                minValue = min(childList, key=lambda x: x[1])[1]
                return [x for x in childList if x[1] == minValue] 
            return childList
    
    startIndexForSearch = None
    result = searchAssociatedKeyWordRecursive(processed_entry, INDEXES_MAIN["action"])
    if result :
        startIndexForSearch = result[0][0]
    else :
        startIndexForSearch = INDEXES_MAIN["subject"]
    
    if parameter and parameter != "name" and attachedEntity :
        return get.FUNCTIONS[parameter](processed_entry, startIndexForSearch, attachedEntity, startIndexForSearch, len(processed_entry), TAKEN_INDEXES)
    
    else :
        counter = 0
        value = []
        indexes = []
        for token in processed_entry[startIndexForSearch].subtree :
            counter += 1
            if counter == 1 : continue
            if token.text == "," : continue
            tokenRealIndex = list(processed_entry).index(token)
            if tokenRealIndex in TAKEN_INDEXES : continue
            value.append(token.text)
            indexes.append(tokenRealIndex)
        for index,text in enumerate(value) :
            if re.search("^\d+$", text) :
                if int(text) == float(text) :
                    value[index] = int(text)
                else :
                    value[index] = float(text)
        if not value :
            raise Exception("Value not detected")
        elif len(value) == 1 :
            return value[0], indexes
        else :
            return value, indexes

def testRelation(index1 : int, index2 : int, relationType : str, hierarchyPosition : dict, dictEntities : dict) -> bool :
    """Test if the relation is coherent, according to the relation"""
    if relationType == "hierarchy" and (hierarchyPosition[index2] < hierarchyPosition[index1] or (hierarchyPosition[index2] == hierarchyPosition[index1] and dictEntities[index2] == "device")):
        return True
    elif relationType == "location" and hierarchyPosition[index2] == hierarchyPosition[index1]:
        return True
    return False

def findIndexMainEntity(processed_entry : Doc, dictEntities : dict, indexAction : int) -> int :
    counter = 0
    currentIndexes = {index:index for index in dictEntities.keys()}
    currentWords = {index:processed_entry[index] for index in currentIndexes.keys()}

    while (not indexAction in currentIndexes.values()) and counter < 3 :
        currentWords = {originIndex : processed_entry[currentIndex].head for originIndex,currentIndex in currentIndexes.items()}
        currentIndexes = {originIndex : currentWords[originIndex].i for originIndex,_ in currentIndexes.items()}

        if list(currentIndexes.values()).count(indexAction) == 1 :
            return [originIndex for originIndex,currentIndex in currentIndexes.items() if currentIndex == indexAction][0]
        counter += 1

    if counter == 5 :
        raise Exception("Main entity not found")
    
    if list(currentIndexes.values()).count(indexAction) != 1 :
        listIndexesRemaining = [originIndex for originIndex,currentIndex in currentIndexes.items() if currentIndex == indexAction and originIndex > indexAction]
        return listIndexesRemaining[0]
    else :
        return [originIndex for originIndex,currentIndex in currentIndexes.items() if currentIndex == indexAction][0]

def findRelations(processed_entry : Doc, dictEntities : dict, indexAction : int) -> dict :

    RELATIONS = {
        "hierarchy" : ["in", "inside", "of"],
        "location" : ["next"]
    }
    global INDEX_MAIN_ENTITY
    
    if len(dictEntities) == 1 :
        INDEX_MAIN_ENTITY = list(dictEntities.keys())[0]
        return {}

    dictRelations = {index : None for index in dictEntities.keys()} # empty dict that will be filled

    # go through the ancestors and check if there's a synonym of the relation key words
    for index in dictEntities.keys() :
        for ancestor in processed_entry[index].ancestors :
            for relation in RELATIONS.keys() :
                if max([ancestor.similarity(nlp(word)[0]) > SIMILARITY_THRESHOLD for word in RELATIONS[relation]]) :
                    if ancestor.lower_ == "of" and ancestor.head.i not in dictEntities.keys() : continue
                    dictRelations[index] = relation
                    break

    # if zero or more than 1 entities don't have a relation
    withoutRelationCounter = list(dictRelations.values()).count(None)
    if  withoutRelationCounter != 1 :
        dictWithoutRelations = {index : relation for (index,relation) in dictRelations.items() if relation == None}
        if withoutRelationCounter == 0 :
            dictWithoutRelations = dictEntities
        INDEX_MAIN_ENTITY = findIndexMainEntity(processed_entry, dictWithoutRelations, indexAction)

    # if only one entity is not attached to a relation keyword, it's the main one
    else :
        INDEX_MAIN_ENTITY = [index for index,relation in dictRelations.items() if relation == None][0]

    # the hierarchy position : 0 is site, 3 is rack... etc
    hierarchyPosition = {index : list(wiki.ENTITIES.keys()).index(entity) for index, entity in dictEntities.items()}
    finalRelations = dict()

    # for all entities except the main one, we assign the related entity according to the relation
    for index, relation in dictRelations.items() : 
        if index == INDEX_MAIN_ENTITY:
            continue
        for token in processed_entry[index].ancestors :
            if token.i in dictEntities.keys(): 
                if testRelation(token.i, index, relation, hierarchyPosition, dictEntities):
                    finalRelations[index] = (token.i, relation)
                else:
                    finalRelations[index] = (token.i, "ERROR")
                break
            elif token.i == indexAction:
                if testRelation(INDEX_MAIN_ENTITY, index, relation, hierarchyPosition, dictEntities):
                    finalRelations[index] = (INDEX_MAIN_ENTITY, relation)
                else:
                    finalRelations[index] = (INDEX_MAIN_ENTITY, "ERROR")
                break
        if not index in finalRelations :
            finalRelations[index] = (INDEX_MAIN_ENTITY, relation)

    return finalRelations

def name(processed_entry : Doc, 
         dictioEntities : dict, 
         dictioNameIndexes : dict, 
         listNameSynonyms : list, 
         takenIndexes : list, 
         indexesMain : dict,
         EXISTING_ENTITY_NAMES : dict,
         searchRawEnabled : bool = False) -> (dict,dict,list) :

    def isName(token : Token) -> bool :
        if (token.is_upper
            or not token.has_vector
            or (token.pos_ in ["NOUN","PROPN","PUNCT","X"] and token.text != ",")
            or (token.i +1 < len(processed_entry) and processed_entry[token.i+1].lower_ in ["-","/","\\"])
            or (token.i -1 > 0 and processed_entry[token.i-1].lower_ in ["-","/","\\"])) :
            return True
        return False

    def findClose(processed_entry : Doc, index : int) -> (int|None) :
        if (index +1 <= len(processed_entry)-1 
            and isName(processed_entry[index+1])
            and index+1 not in newTakenIndexes) :
            return findFullName(processed_entry, index+1)
        if (0 <= index -1 
            and isName(processed_entry[index-1])
            and index-1 not in newTakenIndexes) :
            return findFullName(processed_entry, index-1, False)
        return None

    def findFullName(processed_entry : Doc, index : int, towardsRight : bool = True) :
        fullNameIndexes = []

        indexJump = 1 if towardsRight else -1
        currentIndex = index
        isNameFinished = False
        while not isNameFinished :
            if currentIndex in newTakenIndexes : 
                isNameFinished = True
                continue
            currentToken = processed_entry[currentIndex]
            # if there is a dash, we take both current and next word (and the dash)
            if currentToken.lower_ in ["-","/","\\"] :
                fullNameIndexes.append(currentIndex)
            elif isName(currentToken) or currentToken.pos_ == "NUM" :
                # the method findFullName is called if the token pass the isName method. 
                # So the 2nd condition is correct as it will only test the following tokens
                fullNameIndexes.append(currentIndex)
            else :
                isNameFinished = True

            if not (0 <= currentIndex + indexJump <= len(processed_entry)-1) : 
                isNameFinished = True
            else : 
                currentIndex += indexJump

        return fullNameIndexes

    def findAttachedEntity(processed_entry : Doc, index : int) -> (int|None) : 
        counter = 0
        for token in processed_entry[index].ancestors :
            if counter == 3 :
                break
            if token.i in dictioEntities.keys() and token.i not in newDictioNameIndexes.keys() :
                return token.i
            if indexesMain and "action" in indexesMain.keys() and token.i == indexesMain["action"] and "entity" in indexesMain.keys():
                return indexesMain["entity"]
            counter += 1
        return None

    IMPLICIT = ["current","main"]

    newDictEntities = dictioEntities
    newDictioNameIndexes = dictioNameIndexes # dict with entityIndex : NameOfTheEntityIndex
    newTakenIndexes = takenIndexes

    if len(newDictioNameIndexes) < len(dictioEntities) : # if not all names found
        # begin with the synonyms of "called"
        for nameSynonymIndex in listNameSynonyms :
            currentToken = processed_entry[nameSynonymIndex]
            attachedEntityIndex = findAttachedEntity(processed_entry, nameSynonymIndex)
            attachedValueIndexes = []

            if attachedEntityIndex == None or attachedEntityIndex in newDictioNameIndexes.keys() :
                continue

            if (currentToken.similarity(nlp("called")[0]) > SIMILARITY_THRESHOLD # if "called", check right next to the token
                and currentToken.i < len(processed_entry)-1
                and currentToken.i+1 not in newTakenIndexes
                # and currentToken.is_ancestor(processed_entry[currentToken.i +1])
                and isName(processed_entry[currentToken.i +1])) :
                    attachedValueIndexes.extend(findFullName(processed_entry, currentToken.i +1))

            if len(list(currentToken.children)) != 0  and (not attachedValueIndexes) :
                for token in currentToken.rights :
                    if isName(token) and token.i not in newTakenIndexes :
                        attachedValueIndexes.extend(findFullName(processed_entry, token.i))
                        break
                if not attachedValueIndexes :
                    for token in list(currentToken.lefts)[::-1] :
                        if isName(token) and token.i not in newTakenIndexes :
                            attachedValueIndexes.extend(findFullName(processed_entry, token.i)) # we choose the rightmost
                            break 

            if len(list(currentToken.ancestors)) != 0 and not attachedValueIndexes :
                counter = 0
                for token in currentToken.ancestors :
                    if counter == 2 :
                        break
                    if isName(token) and token.i not in newTakenIndexes :
                        attachedValueIndexes.extend(findFullName(processed_entry, token.i))
                        break
                    else : counter += 1
                
            if attachedValueIndexes and all([x not in newDictioNameIndexes.values() for x in attachedValueIndexes]) :          
                newDictioNameIndexes[attachedEntityIndex] = attachedValueIndexes
                newTakenIndexes.extend(attachedValueIndexes)

    if len(newDictioNameIndexes) < len(dictioEntities) : # if not all names found

        # if the name if right beside the entity
        for entityIndex,_ in dictioEntities.items() :
            if entityIndex in newDictioNameIndexes.keys() :
                continue
            attachedValueIndexes = findClose(processed_entry, entityIndex)
            if attachedValueIndexes != None and attachedValueIndexes not in newDictioNameIndexes.values() :
                newDictioNameIndexes[entityIndex] = attachedValueIndexes
                newTakenIndexes.extend(attachedValueIndexes)

    if len(newDictioNameIndexes) < len(dictioEntities) : # if not all names found
        
        for token in processed_entry : # look directly for a name

            if token.i not in newTakenIndexes and isName(token) :
                indexAttachedEntity = findAttachedEntity(processed_entry, token.i)
                if (indexAttachedEntity != None
                    and indexAttachedEntity not in newDictioNameIndexes.keys()) :
                    attachedValueIndexes = findFullName(processed_entry, token.i)
                    if all([x not in newDictioNameIndexes.values() for x in attachedValueIndexes]) :
                        newDictioNameIndexes[indexAttachedEntity] = attachedValueIndexes
                        newTakenIndexes.extend(attachedValueIndexes)

    if searchRawEnabled :
        # we seek here existing names specified without the type of entity (e.g. create a rack in R1)

        for token in processed_entry : # look directly for a name

            if token.i not in newTakenIndexes and isName(token) :
                attachedValueIndexes = findFullName(processed_entry, token.i)
                stringName = "".join([processed_entry[index].text for index in attachedValueIndexes])
                if stringName[0] == "/" : stringName = stringName[1:]
                for fullName, entity in EXISTING_ENTITY_NAMES.items() :
                    match = re.findall(f"[-/\w]*/{stringName}$", fullName)
                    # TODO : préférer le dernier match
                    if match :
                        newDictioNameIndexes[attachedValueIndexes[0]] = attachedValueIndexes
                        newDictEntities[attachedValueIndexes[0]] = entity
                        newTakenIndexes.extend(attachedValueIndexes)

        
    # TODO : get current names

    # TODO : check for implicit words now
    
    return newDictioNameIndexes, newDictEntities, newTakenIndexes

# TODO : remove dictioEntityNames as parameter and change the function
def associateParameters(processed_entry : Doc, KEY_WORDS_ENTRY : dict, dictEntities : dict, dictioEntityNames : dict) -> dict :
    SPECIAL_KEY_WORD = ["for", "to"]

    association = {}

    if len(dictEntities) == 1:
        for index, keyword in KEY_WORDS_ENTRY.items():
            if keyword in PARAMETERS_DICT_KEYS:
                association[index] = (INDEX_MAIN_ENTITY, keyword)
        return association
    
    for index, keyword in KEY_WORDS_ENTRY.items():
        flagFor = False
        if keyword in PARAMETERS_DICT_KEYS:

            if len(dictEntities) == len(dictioEntityNames):

                if keyword != "name":
                    for token in processed_entry[index].subtree:
                        if token.lower_ in SPECIAL_KEY_WORD:
                            flagFor = True
                        if token.i in dictEntities.keys() and flagFor == True:
                            association[index] = (token.i, keyword)
                            break

                else:
                    for ancestor in processed_entry[index].ancestors:
                        if ancestor.i in dictEntities.keys() and not((ancestor.i, keyword) in association.values()):
                            association[index] = (ancestor.i, keyword)
                            break

            else:

                if keyword == "name":
                    for ancestor in processed_entry[index].ancestors:
                        if ancestor.i in dictEntities.keys() and not((ancestor.i, keyword) in association.values()):
                            association[index] = (ancestor.i, keyword)
                            break

                else:

                    for ancestor in processed_entry[index].ancestors:
                        if (ancestor.i, "name") in list(association.values()):
                            continue

                        if ancestor.i in KEY_WORDS_ENTRY.keys() and KEY_WORDS_ENTRY[ancestor.i] == "name":
                            association[index] = ([ancestor.i], keyword)
                            break

                        if ancestor.i in dictEntities.keys() and not((ancestor.i, keyword) in association.values()):
                            association[index] = (ancestor.i, keyword)
                            break

            # if not index in association.keys():
            #     for token in processed_entry[index].subtree:
            #         if token.i in dictEntities.keys():
            #             association[index] = (token.i, keyword)
            #             break
            
            if not index in association.keys():
                association[index] = (INDEX_MAIN_ENTITY, keyword)


    for index, (index2, parameterType) in association.items():
        if type(index2) == list:
            association[index] = (association[index2[0]][0], parameterType)
            
    return association

def slashInName(parentName : str, partialName : str, EXISTING_ENTITY_NAMES : dict, dictEntities : dict, entityIndex : int):
    if parentName[0] != "/":
        parentName = "/" + parentName
    if parentName[-1] == "/":
        parentName = parentName[:-1]
            
    # ici commence l'enfer
    knownEntity = 0
    knownDevice = 0
    parentSplit = parentName[1:].split("/")
    parentSplit.reverse()
    prevEntityType = None
    existingEntityType = None
    if partialName != "":
        partialSplit = partialName[1:].split("/")
        if len(partialSplit) == 1:
                prevEntityType = dictEntities[entityIndex]
        elif len(partialSplit) > 1:
            for existingName in EXISTING_ENTITY_NAMES.keys():
                if len(existingName) >= len(partialSplit[0]) and partialSplit[0] == existingName[-len(partialSplit[0]):]:
                    prevEntityType = EXISTING_ENTITY_NAMES[existingName]
    for i, subParent in enumerate(parentSplit):
        existingEntityType = None
        if i == 0 and prevEntityType == None:
            knownEntity += 1
            prevEntityType = dictEntities[entityIndex]
            if existingEntityType == "device":
                knownDevice += 1
            continue
        for existingName in EXISTING_ENTITY_NAMES.keys():
            if len(existingName) >= len(subParent) and subParent == existingName[-len(subParent):]:
                existingEntityType = EXISTING_ENTITY_NAMES[existingName]
                if existingEntityType == "device":
                    knownDevice += 1
                if prevEntityType != existingEntityType:
                    knownEntity += 1
                break
        if existingEntityType == None:
            if prevEntityType == "site":
                knownEntity = -1
                break
            raise ValueError("One of the parent name is incorrect.")
        prevEntityType = existingEntityType

    partialName = parentName + partialName
    if partialName[-1] == "/":
        partialName = partialName[:-1]
    return partialName, knownEntity, knownDevice

def buildFullName(dictioEntityNames : dict, dictEntities : dict, finalRelations : dict, entityIndex : int, EXISTING_ENTITY_NAMES : dict, actionType : str) -> str :
    """Build the full name of the entity specified"""

    # Start with the partial name : the name of the entity specified
    partialName = dictioEntityNames[entityIndex]
    # List that contains all the entity index that are part of the name
    parentalTreeIndexList = [entityIndex]
    # Dictionnary that gives a level of hierarchy to an entity. Ex : index_of_a_site : 0, index_of_a_building : 1
    hierarchyPosition = {index : list(wiki.ENTITIES.keys()).index(entity) for index, entity in dictEntities.items()}
    levelCounter = hierarchyPosition[entityIndex]
    startingLevel = hierarchyPosition[entityIndex] - 1
    holeDetected = False
    holeGluer = None
    supDeviceCounter = 0

    # If the specified entity is a device, search for all other devices
    if dictEntities[entityIndex] == "device":
        for indexParent, (indexSon, relationType) in finalRelations.items():
            if indexSon in parentalTreeIndexList and dictEntities[indexParent] == "device" and relationType == "hierarchy":
                parentalTreeIndexList.append(indexParent)
                partialName = dictioEntityNames[indexParent] + "/" + partialName
                supDeviceCounter += 1

    # Check if the name has been written with / character 
    if "/" in partialName:
        partialName, knownEntity, knownDevice = slashInName(partialName, "", EXISTING_ENTITY_NAMES, dictEntities, entityIndex)
        if knownEntity == -1:
            return partialName
        nEntity = partialName.count("/")
        if not(knownEntity == 1 and nEntity > 1):
            startingLevel -= (nEntity-1-supDeviceCounter)
        if nEntity >= list(wiki.ENTITIES.keys()).index("device"):
            startingLevel = list(wiki.ENTITIES.keys()).index("site") - 1
        if startingLevel == -1:
            return partialName
        
    if partialName[0] != "/":
        partialName = "/" + partialName
    
    # Go through all the levels needed for the name
    for level in range(startingLevel, list(wiki.ENTITIES.keys()).index("site") - 1, -1):
        temporaryIndex = None
        if levelCounter <= level:
            continue
            
        # Go through all the relations that exists between entities
        for indexParent, (indexSon, relationType) in finalRelations.items():

            # The relation has the good parent if (3 conditions) : 
            #      the son of the relation is in our current list,
            #      the level of the parent is the one that we are looking for,
            #      the type of the relation is "hierarchy"
            if indexSon in parentalTreeIndexList and hierarchyPosition[indexParent] == level and relationType == "hierarchy":
                parentalTreeIndexList.append(indexParent)
                if holeDetected:
                    holeGluer = dictioEntityNames[indexParent]
                else:
                    if "/" in dictioEntityNames[indexParent]:
                        partialName, knownEntity, knownDevice = slashInName(dictioEntityNames[indexParent], partialName, EXISTING_ENTITY_NAMES, dictEntities, entityIndex)
                        if knownEntity == -1:
                            return partialName
                        levelCounter -= (knownEntity+knownDevice-1)
                    else:
                        partialName = "/" + dictioEntityNames[indexParent] + partialName
                levelCounter -= 1
                break
            # If the son of the current relation is not in the list but satisfy every other condition and the son is the MAIN_ENTITY, the parent is kept in extreme emergency.
            if indexSon == INDEX_MAIN_ENTITY and hierarchyPosition[indexParent] == level and relationType == "hierarchy":
                temporaryIndex = indexParent

        # If not parent found
        if levelCounter > level:
            # If a hole hasn't been detected previously, now it is the case
            if not holeDetected:
                holeDetected = True
            else:
                # If a hole has been detected previously and a parent has been detected, such a name with a hole is searched
                if holeGluer != None:
                    for existingName in EXISTING_ENTITY_NAMES.keys():
                        partialSplit = partialName.split("/")
                        beginningPartialName = ""
                        for splitted in partialSplit[:-1]:
                            beginningPartialName += "/" + splitted
                        correspondingName = re.findall(f"{holeGluer}/[-/\w]+{beginningPartialName}$", existingName)
                        if EXISTING_ENTITY_NAMES[existingName] == dictEntities[entityIndex] and len(correspondingName) > 0:
                            return existingName + partialName
                    raise ValueError("One of the parent name is incorrect or not all the parent tree is known to name the object.")
                # Search for existing entity with the same partial name
                for existingName in EXISTING_ENTITY_NAMES.keys():
                    if EXISTING_ENTITY_NAMES[existingName] == dictEntities[entityIndex] and len(existingName) >= len(partialName) and partialName == existingName[-len(partialName):]:
                        return existingName
                # Extreme emergency : assuming that specified entity and MAIN_ENTITY have the same parental tree
                if temporaryIndex != None:
                    parentalTreeIndexList.append(temporaryIndex)
                for existingName in EXISTING_ENTITY_NAMES.keys():
                    if EXISTING_ENTITY_NAMES[existingName] == list(wiki.ENTITIES.keys())[level]:
                        return existingName + partialName
                # Informations are incomplete
                else:
                    raise ValueError("Not all the parent tree is known to name the object.")
    
    if partialName[:2] != "/P/":
        partialName = "/P" + partialName
    if holeDetected:
        partialName = partialName[2:]
        if actionType == "ACTION_POSITIVE":
            partialSplit = partialName.split("/")
            beginningPartialName = ""
            for splitted in partialSplit[:-1]:
                beginningPartialName += "/" + splitted
            for existingName in EXISTING_ENTITY_NAMES.keys():
                if len(existingName) >= len(beginningPartialName) and beginningPartialName == existingName[-len(beginningPartialName):]:
                    return existingName + "/" + partialSplit[-1]
        else:
            for existingName in EXISTING_ENTITY_NAMES.keys():
                if len(existingName) >= len(partialName) and partialName == existingName[-len(partialName):]:
                    return existingName
        for existingName in EXISTING_ENTITY_NAMES.keys():
            if EXISTING_ENTITY_NAMES[existingName] == "site":
                return existingName + partialName

    # TODO : adapt hierarchyPosition

    return partialName

def getKeyWords(processed_entry : Doc) -> dict :
    ENTITIES_FULL_NAME = {"entity" : list(wiki.ENTITIES.keys())}
    KEY_WORDS_ALL = {**ENTITIES_FULL_NAME,  **PARAMETERS_DICT}

    KEY_WORDS_ENTRY = {}
    # we detect key words in the sentence given and put them into KEY_WORDS_ENTRY
    lastParameter = None
    for index,token in enumerate(processed_entry) :
        matching_list = [] # list of tuples with the similarity score and type of key word (for each key word)
        if token.pos_ == "VERB" and str(token) == token.lemma_ and token.head == token : # 2nd test : if infinitive verb
            for parameter in ACTIONS_DEFAULT_KEYS :
                if token.lower_ in ACTIONS_DEFAULT[parameter] :
                    matching_list.append((1,parameter))
                else :
                    similarity = max([token.similarity(nlp(word)[0]) for word in ACTIONS_DEFAULT[parameter]])
                    matching_list.append((similarity,parameter))
        else :
            for parameter in KEY_WORDS_ALL.keys() :
                if token.lower_ in KEY_WORDS_ALL[parameter] :
                    matching_list.append((1,parameter))
                elif token.pos_ in ["NOUN","ADP","VERB"] :
                    similarity = max([token.similarity(nlp(word)[0]) for word in KEY_WORDS_ALL[parameter]])
                    matching_list.append((similarity,parameter))
        
        if not matching_list :
            continue

        match = max(matching_list)

        # if "called" or a synonym is used for a parameter and not for an entity
        if match[1] == "name" and (lastParameter == token.head or lastParameter in token.children) :
            continue
        if match[1] == lastParameter and match[1] not in ["name","position"] :
            continue
        if match[0] > SIMILARITY_THRESHOLD :
            # if is considered a key word, is added to the dict
            KEY_WORDS_ENTRY[index] = match[1] 
            if match[1] in PARAMETERS_DICT_KEYS :
                lastParameter = match[1]

    return KEY_WORDS_ENTRY

# TODO : the similarity func is very time-taking, we must shorten the process time or find another way

def NL_to_OCLI(ocliFile : str) -> str :
    importlib.reload(wiki)
    FINAL_INSTRUCTION = ""
    TAKEN_INDEXES = []

    EXISTING_ENTITY_NAMES = scrapping.scrapAllName(ocliFile)

    natural_entry = input("Enter a prompt. Please follow the instructions given.\n")
    processed_entry = nlp(natural_entry)

    KEY_WORDS_ENTRY = getKeyWords(processed_entry)
    print("KEY_WORDS_ENTRY : ", KEY_WORDS_ENTRY)
    TAKEN_INDEXES.extend(KEY_WORDS_ENTRY.keys())

    dictEntities = {index : processed_entry[index].text for index,keyword in KEY_WORDS_ENTRY.items() if keyword == "entity"}
    print("dictEntities :", dictEntities)

    dictioNameIndexes, dictEntities, TAKEN_INDEXES = name(processed_entry,
                                                            dictEntities,
                                                            {},
                                                            [index for index,parameter in KEY_WORDS_ENTRY.items() if parameter == "name"],
                                                            TAKEN_INDEXES,
                                                            {},
                                                            EXISTING_ENTITY_NAMES,
                                                            True)

    # test detection
    list_key_param = list(KEY_WORDS_ENTRY.values())
    count_action = 0 # the nb of action words indentified
    for action_type in ACTIONS_DEFAULT_KEYS :
        count_action += list_key_param.count(action_type)

    if count_action != 1 :
        raise Exception("Action not detected")
    
    # TODO : check entities
    # if no entity mentionned : must be alteration
    # if no entity and color, seek for keyword reserved etc besides the color

    # if no entity :check the ocli file
    indexAction= [index for index,keyword in KEY_WORDS_ENTRY.items() if keyword in ACTIONS_DEFAULT_KEYS][0]
    finalRelations = findRelations(processed_entry, dictEntities, indexAction)
    indexMainSubject = findIndexMainSubject(processed_entry, KEY_WORDS_ENTRY, indexAction, INDEX_MAIN_ENTITY)  

    INDEXES_MAIN = {"subject" : indexMainSubject, 
                    "action" : indexAction, 
                    "entity" : INDEX_MAIN_ENTITY}
    print("INDEXES_MAIN : ", INDEXES_MAIN)

    dictioNameIndexes, dictEntities, TAKEN_INDEXES = name(processed_entry,
                                                            dictEntities,
                                                            dictioNameIndexes,
                                                            [index for index,parameter in KEY_WORDS_ENTRY.items() if parameter == "name"],
                                                            TAKEN_INDEXES,
                                                            INDEXES_MAIN,
                                                            EXISTING_ENTITY_NAMES,
                                                            False)
    
    dictioEntityNames = {}
    for entityIndex, valueIndexes in dictioNameIndexes.items() :
        stringName = "".join([processed_entry[index].text for index in valueIndexes])
        if stringName[-1] in ["/","\\"] : stringName = stringName[:-1]
        dictioEntityNames[entityIndex] = stringName
    print("dictioNameIndexes : ", dictioNameIndexes)
    print("dictioEntityNames : ",dictioEntityNames)
    print("dictEntities : ", dictEntities)
    
    association = associateParameters(processed_entry, KEY_WORDS_ENTRY, dictEntities, dictioEntityNames)
    print("association : ", association)

    fullName = buildFullName(dictioEntityNames, dictEntities, finalRelations, INDEX_MAIN_ENTITY, EXISTING_ENTITY_NAMES, KEY_WORDS_ENTRY[INDEXES_MAIN["action"]])
    print(fullName)
    if fullName == None:
        raise ValueError("Not all the parent tree is known to name the object.")
    
    # TODO : change the name of parameters depending on the entity (e.g. unit -> floorUnit)
    if INDEXES_MAIN["subject"] in KEY_WORDS_ENTRY.keys() and KEY_WORDS_ENTRY[INDEXES_MAIN["subject"]] == "entity" :
        # we do the processes related to each parameter

        if KEY_WORDS_ENTRY[INDEXES_MAIN["action"]] == "ACTION_POSITIVE" :
            if fullName in EXISTING_ENTITY_NAMES.keys():
                raise ValueError(f'This {dictEntities[INDEXES_MAIN["subject"]]} already exists.')
            dictioEntityParameters = wiki.makeDictParam(processed_entry[INDEXES_MAIN["subject"]].text)
            dictioEntityParameters["name"] = fullName.upper()
            allEntryItemsList = list(KEY_WORDS_ENTRY.items())
            for counter,(index,parameterName) in enumerate(allEntryItemsList) :
                if ((not parameterName in PARAMETERS_DICT_KEYS) 
                    or bool(dictioEntityParameters[parameterName]) == True 
                    or association[index][0] != INDEXES_MAIN["subject"]) :
                    continue
                lastKeyWordIndex = 0 if counter == 0 else allEntryItemsList[counter-1][0]
                nextKeyWordIndex = len(processed_entry) if counter == len(allEntryItemsList)-1 else allEntryItemsList[counter+1][0]
                # get the parameter value
                # TODO : change to the get file
                parameterValue, parameterIndex = get.FUNCTIONS[parameterName](processed_entry, 
                                                                          index, 
                                                                          dictEntities[association[index][0]], 
                                                                          lastKeyWordIndex, 
                                                                          nextKeyWordIndex, 
                                                                          TAKEN_INDEXES)
                TAKEN_INDEXES.extend(parameterIndex)
                dictioEntityParameters[parameterName] = parameterValue # store the value
            
            print("dictioEntityParameters : ", dictioEntityParameters)
            FINAL_INSTRUCTION = tools.create(dictEntities[INDEXES_MAIN["subject"]], dictioEntityParameters)

        elif KEY_WORDS_ENTRY[INDEXES_MAIN["action"]] == "ACTION_NEGATIVE" :
            FINAL_INSTRUCTION = tools.delete("", {"name" : fullName})
        
        else:
            raise NotImplementedError("The action '"+KEY_WORDS_ENTRY[INDEXES_MAIN["action"]]+"' has not been implemented for '"+KEY_WORDS_ENTRY[INDEXES_MAIN["subject"]]+"' as main subject")

    else:
        # TODO : if parameter is "name"
        if KEY_WORDS_ENTRY[INDEXES_MAIN["action"]] == "ACTION_POSITIVE" :
            allEntryItemsList = list(KEY_WORDS_ENTRY.items())
            for counter,(index,parameterName) in enumerate(allEntryItemsList) :
                if (not parameterName in PARAMETERS_DICT_KEYS) or parameterName == "name": # or association[index][0] != INDEX_MAIN_ENTITY
                    continue
                lastKeyWordIndex = 0 if counter == 0 else allEntryItemsList[counter-1][0]
                nextKeyWordIndex = len(processed_entry) if counter == len(allEntryItemsList)-1 else allEntryItemsList[counter+1][0]
                # get the parameter value
                parameterValue, parameterIndexes = get.FUNCTIONS[parameterName](processed_entry,
                                                                          index, 
                                                                          dictEntities[association[index][0]], 
                                                                          lastKeyWordIndex, 
                                                                          nextKeyWordIndex, 
                                                                          TAKEN_INDEXES)
                TAKEN_INDEXES.extend(parameterIndexes)
                fullName = buildFullName(dictioEntityNames, dictEntities, finalRelations, association[index][0], EXISTING_ENTITY_NAMES, KEY_WORDS_ENTRY[INDEXES_MAIN["action"]])
                if fullName == None:
                    raise ValueError("Not all the parent tree is known to name the object.")
                FINAL_INSTRUCTION += tools.createAttribute(fullName, parameterName, parameterValue) + "\n"

        elif KEY_WORDS_ENTRY[INDEXES_MAIN["action"]] == "ALTERATION" :
            # REQUIRES : the full name, the parameter and its value
            if not fullName in EXISTING_ENTITY_NAMES.keys() :
                raise ValueError(f"This {dictEntities[INDEX_MAIN_ENTITY]} doesn't exist.")
            parameterName = None
            attachedEntityIndex = None
            # then we take the more relevant/right attachedEntity
            if INDEXES_MAIN["subject"] not in KEY_WORDS_ENTRY.keys() :
                attachedEntityIndex = INDEXES_MAIN["entity"]
            else :
                attachedEntityIndex = association[INDEXES_MAIN["subject"]][0]
                parameterName = association[INDEXES_MAIN["subject"]][1]

            # get the parameter value
            parameterValue, parameterIndexes = findAssociatedValue(processed_entry, INDEXES_MAIN, TAKEN_INDEXES, parameterName, dictEntities[attachedEntityIndex])
            print(parameterValue)
            TAKEN_INDEXES.extend(parameterIndexes)

            fullName = buildFullName(dictioEntityNames, dictEntities, finalRelations, attachedEntityIndex, EXISTING_ENTITY_NAMES, KEY_WORDS_ENTRY[INDEXES_MAIN["action"]])
            if fullName == None:
                raise ValueError("Not all the parent tree is known to name the object.")
            if INDEXES_MAIN["subject"] not in KEY_WORDS_ENTRY.keys() : parameterName = processed_entry[INDEXES_MAIN["subject"]]
            if INDEXES_MAIN["subject"] in KEY_WORDS_ENTRY.keys() and KEY_WORDS_ENTRY[INDEXES_MAIN["subject"]] == "name":
                currentNameSplit = fullName.split("/")[1:]
                if parameterValue[0] != "/":
                    parameterValue = "/" + parameterValue
                if parameterValue[-1] == "/":
                    parameterValue = parameterValue[:-1]
                newName = ""
                for i in range(len(currentNameSplit) - parameterValue.count("/")):
                    newName += "/" + currentNameSplit[i]
                newName += parameterValue
                FINAL_INSTRUCTION += tools.setName(fullName, newName)
            else:
                FINAL_INSTRUCTION += tools.setAttribute(fullName, parameterName, parameterValue, dictEntities[attachedEntityIndex]) + "\n"
    
        else:
            raise NotImplementedError("The action '"+KEY_WORDS_ENTRY[INDEXES_MAIN["action"]]+"' has not been implemented for '"+KEY_WORDS_ENTRY[INDEXES_MAIN["subject"]]+"' as main subject")
    
    # if seeking the name for the main entity, pass the indexaction as parameter
    # if no name found, check the type of action : if +, a name is needed, otherwise not necessarily

    # check if parameters were not given
    print("FINAL_INSTRUCTION : ", FINAL_INSTRUCTION)
    return FINAL_INSTRUCTION

if __name__ == "__main__":

    init.main()
    repeat = True

    while (repeat):
        ocliCommand = NL_to_OCLI(init.FILEPATH)
        print("Command created : " + ocliCommand)
        satisfied = input("Satisfied ? (Yes : Press Enter, No : type n|N) ").lower()
        if satisfied == "" or satisfied == "yes":
            init.addCommandInOcli(ocliCommand)
        another = input("Do you want to create another command ? (Yes : Press Enter, No : type n|N) ").lower()
        if another != "" and another != "yes":
            repeat = False

