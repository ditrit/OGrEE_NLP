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

### THE MAIN WORDS TO BE DETECTED AS AN ACTION ###
ACTIONS_DEFAULT = {
                    "ACTION_POSITIVE" : ["make","build","put","place","add","insert","pack"],
                    "ACTION_NEGATIVE" : ["remove", "delete"], 
                    "ALTERATION" : ["modify", "change","move","set","rename","rotate"]
                    }

### THE VALUE FROM WHICH WE CONSIDER TWO WORDS ARE SYNONYM ###
SIMILARITY_THRESHOLD = 0.5

### KEY WORDS FOR EACH PARAMETER ###
PARAMETERS_DICT = {
            "name" : ["name","called"],
            "position" : ["position","at","located","posU","centered","centerXY","startPosition","startPos","endPosition"],
            "rotation" : ["rotation","turned","degree"],
            "size" : ["size","dimensions","height","sizeU","sizeXY"],
            "template" : ["template"],
            "axisOrientation" : ["axisOrientation", "axis", "orientation"],
            "unit" :  ["unit","floorUnit"],
            "slot" : ["slot"],
            "color" : ["color","usableColor","reservedColor","technicalColor"] + list(wiki.COLORS_HEX_BASIC.keys()), 
            "side" : ["side"],
            "temperature" : ["temperature","cold","warm"],
            "type" : ["type","wireframe","plain"],
            # "reserved" : ["reserved"],
            # "technical" : ["technical"]
            }

ENTITIES_FULL_NAME = {"entity" : list(wiki.ENTITIES.keys())}

KEY_WORDS_ALL = {**ENTITIES_FULL_NAME,  **PARAMETERS_DICT} # ALL KEYWORDS TO BE DETECTED

PARAMETERS_DICT_KEYS = PARAMETERS_DICT.keys()
ACTIONS_DEFAULT_KEYS = ACTIONS_DEFAULT.keys()

# TODO : the similarity func is very time-taking, we must shorten the process time or find another way

def findIndexMainSubject(processed_entry : Doc, dictioIndexKeyWords : dict, indexAction : int, indexMainEntity : int = None) -> int :
    """
    This function returns the main subject of the entry, that means the entity/parameter related to the action
    The identification is based on the action
    """

    # This function searches the subject in the token's children (if exist) while a candidate subject has not been found
    def searchSubjectRecursive(processed_entry : Doc, currentIndex : int, testConformity, level : int = 0) -> (list|None):
        if level == 5 : # if the research is too far from the original token, we stop
            return None
        if testConformity(processed_entry[currentIndex]) : 
            # If token can be the main subject, we return it
            return [(currentIndex, level)]
        else:
            # Else, we go through each of its children
            childList = []
            for child in processed_entry[currentIndex].children :
                childResult = searchSubjectRecursive(processed_entry, child.i, testConformity, level+1)
                if childResult != None :
                    childList.extend(childResult)
            if bool(childList) == True : 
                # If among all children there are candidates, we select the ones closer to the original token (according to level)    
                minLevel = min(childList, key=lambda x: x[1])[1]
                return [x for x in childList if x[1] == minLevel] 
            # because the children function returns token in ascending order, the final childList is sorted so
            return childList
    
    def testConformity(token : Token) -> bool :
        # This test is quite general, as the main subject could be almost anything
        if ((token.i in dictioIndexKeyWords.keys() or token.pos_ == "NOUN") # if not in the key words, should be a newly defined parameter
            and token.pos_ != "VERB"
            and not token.is_upper) :
            return True
        return False
    
    actionType = dictioIndexKeyWords[indexAction]

    result = searchSubjectRecursive(processed_entry, indexAction, testConformity)
    result = [x[0] for x in result] # remove the level for each value, as all values have the same level
    resultLength = len(result)

    if resultLength == 0 :
        raise Exception("Main request not identified")
    elif resultLength == 1 :
        return result[0]
    else : # if there are at least two tokens at the same length from the action

        if actionType == list(PARAMETERS_DICT_KEYS)[3] : # if "ALTERATION", prioritize known parameters over other parameters and entities e.g.
            resultOnlyParameters = [index for index in result if index in dictioIndexKeyWords.keys() and dictioIndexKeyWords[index] in PARAMETERS_DICT_KEYS]
            if bool(resultOnlyParameters) :
                return resultOnlyParameters[0]
            else :
                # we return the closest to the action verb (see searchSubjectRecursive)
                return result[0] 
            
        else : # if the request is not an alteration, we prioritze entites
            resultOnlyEntity = [index for index in result if index in dictioIndexKeyWords.keys() and dictioIndexKeyWords[index] == "entity"]
            if not bool(resultOnlyEntity) :
                return result[0]
            elif len(resultOnlyEntity) == resultLength and indexMainEntity in result :
                # if all candidates are entities, we return the main entity identified earlier
                return indexMainEntity
            else :
                return resultOnlyEntity[0]

def findAssociatedValue(processed_entry : Doc, INDEXES_MAIN : dict, TAKEN_INDEXES : list = [], parameter : str = None, attachedEntity : str = None) :
    """
    This function finds the related value to the main subject when the action is "ALTERATION"
    """

    # Same as searchSubjectRecursive -> look above
    def searchAssociatedKeyWordRecursive(processed_entry : Doc, currentIndex : int, level : int = 0) -> (list|None) :
        if level == 3 : # the max level is lower, because Spacy use to recognize well the links with the word "to"
            return None
        if processed_entry[currentIndex].lower_ == "to" : 
            # the only difference is the test : here we look for the keyword "to"
            return [(currentIndex, level)]
        else:
            childList = []
            for child in processed_entry[currentIndex].children :
                childResult = searchAssociatedKeyWordRecursive(processed_entry, child.i, level+1)
                if childResult != None :
                    childList.extend(childResult)
            if bool(childList) == True :  
                minValue = min(childList, key=lambda x: x[1])[1]
                return [x for x in childList if x[1] == minValue] 
            return childList
    
    startIndexForSearch = None
    # we look for the keyword "to" related to the verb marking the reference to the new value (e.g. set the value of... to...)
    result = searchAssociatedKeyWordRecursive(processed_entry, INDEXES_MAIN["action"])
    if result : # if "to" is detected, we start our value research from this token
        startIndexForSearch = result[0][0]
    else : # if not, we look for a value close to the main subject (e.g. set the value 0 for...)
        startIndexForSearch = INDEXES_MAIN["subject"]
    
    # if the value seeked is related to a "classic" parameter, we use the adapted search function
    if parameter and parameter != "name" and attachedEntity :
        return get.FUNCTIONS[parameter](processed_entry, startIndexForSearch, attachedEntity, startIndexForSearch, len(processed_entry), TAKEN_INDEXES)
    
    else : # else, we search into the subtree of the start token, and we assume the dependencies are correct
        counter = 0
        value = []
        indexes = []
        for token in processed_entry[startIndexForSearch].subtree :
            counter += 1
            if counter == 1 : continue
            if token.text == "," : continue
            tokenRealIndex = list(processed_entry).index(token) # the subtree changes the indexes
            if tokenRealIndex in TAKEN_INDEXES : continue
            value.append(token.text)
            indexes.append(tokenRealIndex)
        for index,text in enumerate(value) :
            if re.search("^\d+$", text) : # if the values are numbers, we convert them into number type
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
    
def findRelations(processed_entry : Doc, dictEntities : dict, indexAction : int) -> dict :
    """
    In every request, there is a main entity (related to the main subject) and entities mentionned for precisions
    This function identifies the main entity and its relations with the others
    """

    # Identifies the main entity (related to the main subject / action) among all entities
    def findIndexMainEntity(processed_entry : Doc, dictEntities : dict, indexAction : int) -> int :
        counter = 0
        # we create a dict made of originalIndex : currentIndex for all entities
        currentIndexes = {index:index for index in dictEntities.keys()}
        currentWords = {index:processed_entry[index] for index in currentIndexes.keys()}

        # The first entity to reach the action verb (in terms of dependencies) is considered the main entity
        # "counter" variable : if the entities are too far from the action verb, we stop
        while (not indexAction in currentIndexes.values()) and counter < 3 :
            # we update the current indexes and words for each entity
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
        
    # Test if the relation identified matches the entity hierarchy
    def testRelation(index1 : int, index2 : int, relationType : str, hierarchyPosition : dict, dictEntities : dict) -> bool :
        if relationType == "hierarchy" and (hierarchyPosition[index2] < hierarchyPosition[index1] or (hierarchyPosition[index2] == hierarchyPosition[index1] and dictEntities[index2] == "device")):
            return True
        elif relationType == "location" and hierarchyPosition[index2] == hierarchyPosition[index1]:
            return True
        return False

    # A dict with the keywords for each relation type
    RELATIONS = {
        "hierarchy" : ["in", "inside", "of"],
        "location" : ["next"]
    }
    global INDEX_MAIN_ENTITY
    
    if len(dictEntities) == 1 :
        INDEX_MAIN_ENTITY = list(dictEntities.keys())[0]
        return {}

    dictRelations = {index : None for index in dictEntities.keys()} # empty dict that will be filled

    # go through the ancestors of each entity and check if there's a synonym of the relation key words
    for index in dictEntities.keys() :
        for ancestor in processed_entry[index].ancestors :
            for relation in RELATIONS.keys() :
                # here, the similarity thresold is different than usual
                if max([ancestor.similarity(nlp(word)[0]) > 0.8 for word in RELATIONS[relation]]) : # similarity check
                    # the "of" keyword could be assigned to a non-entity word
                    if ancestor.lower_ == "of" and ancestor.head.i not in dictEntities.keys() : continue
                    dictRelations[index] = relation
                    break

            if index in dictRelations.keys() :
                break    
        
        # we check if the token right before the entity is a relation keyword
        if index-1 > 0 :
            for relation in RELATIONS.keys() :
                if max([processed_entry[index-1].similarity(nlp(word)[0]) > 0.8 for word in RELATIONS[relation]]) :
                    if processed_entry[index-1].lower_ == "of" and processed_entry[index-1].head.i not in dictEntities.keys() : continue
                    dictRelations[index] = relation
                    break

    # if zero or more than 1 entities don't have a relation
    withoutRelationCounter = list(dictRelations.values()).count(None) # the nb of entities without relation
    if  withoutRelationCounter != 1 :
        dictWithoutRelations = dictEntities
        if withoutRelationCounter != 0 :
            dictWithoutRelations = {index : relation for (index,relation) in dictRelations.items() if relation == None}
        # we find the main entity among the ones without relation
        INDEX_MAIN_ENTITY = findIndexMainEntity(processed_entry, dictWithoutRelations, indexAction)

    # if only one entity is not attached to a relation keyword, it's the main one
    else :
        INDEX_MAIN_ENTITY = [index for index,relation in dictRelations.items() if relation == None][0]

    # the hierarchy position : 0 is site, 3 is rack... etc
    # TODO : improve the hierarchyPosition dict
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
            # if the current entity refers to the main action, we assign it to the main entity
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
    """
    According to the sentence and the existing file, assign names to the entitites mentionned
    """

    def isName(token : Token) -> bool : 
        # Check if a work matches the criteria of an entity name
        if (token.is_upper
            or not token.has_vector
            or (token.pos_ in ["NOUN","PROPN","PUNCT","X"] and token.text != ",")
            or (token.i +1 < len(processed_entry) and processed_entry[token.i+1].lower_ in ["-","/","\\"])
            or (token.i -1 > 0 and processed_entry[token.i-1].lower_ in ["-","/","\\"])) :
            return True
        return False

    def findClose(processed_entry : Doc, index : int) -> (int|None) : 
        # Look for a name right beside the entity
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
        # If a part of a name is found, the function rebuilt the full name (split in several tokens, beside the original one)
        fullNameIndexes = []

        indexJump = 1 if towardsRight else -1
        currentIndex = index
        isNameFinished = False
        # We go across all tokens making the whole name until we find a word not matching the criteria
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
                # So the 2nd condition can be put here as it will only test the following tokens (making the whole name)
                fullNameIndexes.append(currentIndex)
            else :
                isNameFinished = True

            if not (0 <= currentIndex + indexJump <= len(processed_entry)-1) : 
                isNameFinished = True
            else : 
                currentIndex += indexJump

        return fullNameIndexes

    def findAttachedEntity(processed_entry : Doc, index : int) -> (int|None) :
        # Find the entity attached to the name, thanks to its dependencies
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

    IMPLICIT = ["current","main"] # TODO : understand "in the main building" or similar

    newDictEntities = dictioEntities # extended dict in which we add entities mentionned without the keyword ("building" e.g.)
    newDictioNameIndexes = dictioNameIndexes # dict with entityIndex : NameOfTheEntityIndex
    newTakenIndexes = takenIndexes

    if len(newDictioNameIndexes) < len(dictioEntities) : 
        # if not all names found : this condition is mandatory, especially since the name function is called twice

        for nameSynonymIndex in listNameSynonyms :
            # begin with the synonyms of "called"
            currentToken = processed_entry[nameSynonymIndex]
            attachedEntityIndex = findAttachedEntity(processed_entry, nameSynonymIndex)
            attachedValueIndexes = []

            if attachedEntityIndex == None or attachedEntityIndex in newDictioNameIndexes.keys() :
                # if one of these conditions is verified, the entity would have already be identified in the first call of the function
                continue

            if (currentToken.similarity(nlp("called")[0]) > SIMILARITY_THRESHOLD # if "called", check right next to the token
                and currentToken.i < len(processed_entry)-1
                and currentToken.i+1 not in newTakenIndexes
                # and currentToken.is_ancestor(processed_entry[currentToken.i +1]) ?
                and isName(processed_entry[currentToken.i +1])) :
                    attachedValueIndexes.extend(findFullName(processed_entry, currentToken.i +1))

            if len(list(currentToken.children)) != 0  and (not attachedValueIndexes) :
                # if name not found right beside the "called" token, we look into its right children
                for token in currentToken.rights :
                    if isName(token) and token.i not in newTakenIndexes :
                        attachedValueIndexes.extend(findFullName(processed_entry, token.i))
                        break
                if not attachedValueIndexes :
                    # if still not found, look into its left children
                    for token in list(currentToken.lefts)[::-1] :
                        if isName(token) and token.i not in newTakenIndexes :
                            attachedValueIndexes.extend(findFullName(processed_entry, token.i)) # we choose the rightmost
                            break 

            if len(list(currentToken.ancestors)) != 0 and not attachedValueIndexes :
                # if name not found yet, look into its ancestors 
                counter = 0
                for token in currentToken.ancestors :
                    if counter == 2 :
                        break
                    if isName(token) and token.i not in newTakenIndexes :
                        attachedValueIndexes.extend(findFullName(processed_entry, token.i))
                        break
                    else : counter += 1
                
            if attachedValueIndexes and all([x not in newDictioNameIndexes.values() for x in attachedValueIndexes]) :
                # if a name is found and is not already identified, we add it         
                newDictioNameIndexes[attachedEntityIndex] = attachedValueIndexes
                newTakenIndexes.extend(attachedValueIndexes)

    if len(newDictioNameIndexes) < len(dictioEntities) : 
        # if not all names found

        # if the name if right beside the entity (without "called")
        for entityIndex,_ in dictioEntities.items() :
            if entityIndex in newDictioNameIndexes.keys() :
                continue
            attachedValueIndexes = findClose(processed_entry, entityIndex)
            if attachedValueIndexes != None and attachedValueIndexes not in newDictioNameIndexes.values() :
                newDictioNameIndexes[entityIndex] = attachedValueIndexes
                newTakenIndexes.extend(attachedValueIndexes)

    if len(newDictioNameIndexes) < len(dictioEntities) : 
        # if not all names found
        
        for token in processed_entry : 
            # look directly for a name, and see if it is attached to an known entity

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
        # the goal is to identify entities not detected yet (as there is no entity keyword attached to it)

        for token in processed_entry : # look directly for a name

            if token.i not in newTakenIndexes and isName(token) :
                attachedValueIndexes = findFullName(processed_entry, token.i)
                stringName = "".join([processed_entry[index].text for index in attachedValueIndexes])
                if stringName[0] == "/" : stringName = stringName[1:]
                for fullName, entity in EXISTING_ENTITY_NAMES.items() :
                    match = re.findall(f"[-/\w]*/{stringName}$", fullName)
                    # TODO : prefer the last match (findall returns a list)
                    if match :
                        newDictioNameIndexes[attachedValueIndexes[0]] = attachedValueIndexes
                        newDictEntities[attachedValueIndexes[0]] = entity
                        newTakenIndexes.extend(attachedValueIndexes)

    # TODO : check for implicit words now, listed above -> use methods from scrapping.py
    
    return newDictioNameIndexes, newDictEntities, newTakenIndexes

def associateParameters(processed_entry : Doc, KEY_WORDS_ENTRY : dict, dictEntities : dict, dictioEntityNames : dict) -> dict :
    """
    Associate the index of all parameters to the entity
    """
    # TODO : remove dictioEntityNames as parameter and change the function

    SPECIAL_KEY_WORD = ["for", "to"]
    association = {}

    # If only one entity is detected, all parameters are associated to it
    if len(dictEntities) == 1:
        for index, keyword in KEY_WORDS_ENTRY.items():
            if keyword in PARAMETERS_DICT_KEYS:
                association[index] = (INDEX_MAIN_ENTITY, keyword)
        return association
    
    # Go through every key words
    for index, keyword in KEY_WORDS_ENTRY.items():
        flagFor = False
        # If the word is a parameter
        if keyword in PARAMETERS_DICT_KEYS:

            # If every entity has a name in the sentence
            if len(dictEntities) == len(dictioEntityNames):

                if keyword != "name":
                    # Keyword "for/to" and an entity are searched in the subtree
                    for token in processed_entry[index].subtree:
                        if token.lower_ in SPECIAL_KEY_WORD:
                            flagFor = True
                        if token.i in dictEntities.keys() and flagFor == True:
                            association[index] = (token.i, keyword)
                            break

                else:
                    # The entity is searched in the ancestors for the name
                    for ancestor in processed_entry[index].ancestors:
                        if ancestor.i in dictEntities.keys() and not((ancestor.i, keyword) in association.values()):
                            association[index] = (ancestor.i, keyword)
                            break

            else:
            # If the number of name is lower than the number of entity

                # The entity is searched in the ancestors for the name
                if keyword == "name":
                    for ancestor in processed_entry[index].ancestors:
                        if ancestor.i in dictEntities.keys() and not((ancestor.i, keyword) in association.values()):
                            association[index] = (ancestor.i, keyword)
                            break

                else:

                    for ancestor in processed_entry[index].ancestors:
                        # If the ancestor is a name and already associated to an entity, skip this ancestor
                        if (ancestor.i, "name") in list(association.values()):
                            continue

                        # If the ancestor is a name, the parameter will later be added to the corresponding entity
                        if ancestor.i in KEY_WORDS_ENTRY.keys() and KEY_WORDS_ENTRY[ancestor.i] == "name":
                            association[index] = ([ancestor.i], keyword)
                            break
                        
                        # If an entity is detected in the ancestors
                        if ancestor.i in dictEntities.keys() and not((ancestor.i, keyword) in association.values()):
                            association[index] = (ancestor.i, keyword)
                            break
            
            # If no association has been made for the parameter, it is associated to the main entity
            if not index in association.keys():
                association[index] = (INDEX_MAIN_ENTITY, keyword)


    # If a parameter was associated to a name, the parameter is now associated to the corresponding entity
    for index, (index2, parameterType) in association.items():
        if type(index2) == list:
            association[index] = (association[index2[0]][0], parameterType)
            
    return association

def slashInName(parentName : str, partialName : str, EXISTING_ENTITY_NAMES : dict, dictEntities : dict, entityIndex : int):
    """
    Elementary function for buildFullName, count all the entity known and the number of device in order to update the level counter
    """

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
    # Find the entity type of the last entity
    if partialName != "":
        partialSplit = partialName[1:].split("/")
        if len(partialSplit) == 1:
                prevEntityType = dictEntities[entityIndex]
        elif len(partialSplit) > 1:
            for existingName in EXISTING_ENTITY_NAMES.keys():
                if len(existingName) >= len(partialSplit[0]) and partialSplit[0] == existingName[-len(partialSplit[0]):]:
                    prevEntityType = EXISTING_ENTITY_NAMES[existingName]

    # for parents, search if the name exists and detect if it is a device or not
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

    # Construct the name
    partialName = parentName + partialName
    if partialName[-1] == "/":
        partialName = partialName[:-1]
    return partialName, knownEntity, knownDevice

def buildFullName(dictioEntityNames : dict, dictEntities : dict, finalRelations : dict, entityIndex : int, EXISTING_ENTITY_NAMES : dict, actionType : str) -> str :
    """
    Build the full name (from the start : "/P/...") of the entity specified
    """
    
    # Start with the partial name : the name of the entity specified
    partialName = dictioEntityNames[entityIndex]
    # List that contains all the entity index that are part of the name
    parentalTreeIndexList = [entityIndex]
    # Dictionnary that gives a level of hierarchy to an entity. Ex : index_of_a_site : 0, index_of_a_building : 1
    hierarchyPosition = {index : list(wiki.ENTITIES.keys()).index(entity) for index, entity in dictEntities.items()}
    # Counter and flag needed to go through the levels
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

    # Check if the name has been written with / character and adjust the starting level
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
                        correspondingName = re.findall(f"{holeGluer}/[-/\w]+{partialName}$", existingName)
                        if EXISTING_ENTITY_NAMES[existingName] == dictEntities[entityIndex] and len(correspondingName) > 0:
                            return existingName
                    print(holeGluer + " + " + partialName)
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
    
    # Correct the beginning of the name
    if partialName[:2] != "/P/":
        partialName = "/P" + partialName
    # If there is a hole for the last level (site), search for an existing name
    if holeDetected:
        partialName = partialName[2:]
        # if ACTION_POSITIVE, keep the partial name without the current entity
        if actionType == "ACTION_POSITIVE":
            partialSplit = partialName.split("/")
            beginningPartialName = ""
            for splitted in partialSplit[:-1]:
                beginningPartialName += "/" + splitted
            for existingName in EXISTING_ENTITY_NAMES.keys():
                if len(existingName) >= len(beginningPartialName) and beginningPartialName == existingName[-len(beginningPartialName):]:
                    return existingName + "/" + partialSplit[-1]
        # if the entity already exists, keep all the partial name
        else:
            for existingName in EXISTING_ENTITY_NAMES.keys():
                if len(existingName) >= len(partialName) and partialName == existingName[-len(partialName):]:
                    return existingName
        for existingName in EXISTING_ENTITY_NAMES.keys():
            if EXISTING_ENTITY_NAMES[existingName] == "site":
                return existingName + partialName
        raise ValueError("No site available")

    # TODO : adapt hierarchyPosition to manage groups etc

    return partialName

def getKeyWords(processed_entry : Doc) -> dict :
    """
    Get all keywords in the given sentence, according to the keywords defined in the dicts above
    """

    ENTITIES_FULL_NAME = {"entity" : list(wiki.ENTITIES.keys())} # all the entites are under the "entity" keyword name
    KEY_WORDS_ALL = {**ENTITIES_FULL_NAME,  **PARAMETERS_DICT}

    KEY_WORDS_ENTRY = {}
    # we detect key words in the sentence given and put them into KEY_WORDS_ENTRY
    lastParameter = None, None

    for index,token in enumerate(processed_entry) :
        matching_list = [] 
        # list of tuples with the similarity score (between 0 and 1) and type of key word (for each key word)

        if token.pos_ == "VERB" and str(token) == token.lemma_ and token.head == token : # 2nd test : if infinitive verb
            # this test is first to avoid properties being considered as verbs (like "name" etc)
            for actionKeyword in ACTIONS_DEFAULT_KEYS :
                if token.lower_ in ACTIONS_DEFAULT[actionKeyword] :
                    # if the exact word is in the keywords list, the similarity given is 1
                    matching_list.append((1,actionKeyword))
                else :
                    similarity = max([token.similarity(nlp(word)[0]) for word in ACTIONS_DEFAULT[actionKeyword]])
                    # we take the max similarity score over all words related to the keyword
                    matching_list.append((similarity,actionKeyword))
        else :
            for keyword in KEY_WORDS_ALL.keys() :
                if token.lower_ in KEY_WORDS_ALL[keyword] :
                    matching_list.append((1,keyword))
                elif token.pos_ in ["NOUN","ADP","VERB"] :
                    # this test allows excluding all the "stop words"
                    # we do not directly test with "is_stop" as keywods such as "at" exist
                    similarity = max([token.similarity(nlp(word)[0]) for word in KEY_WORDS_ALL[keyword]])
                    matching_list.append((similarity,keyword))
        
        if not matching_list :
            continue

        match = max(matching_list) # we only keep the highest similarity score

        if match[1] == "name" and lastParameter[0] and (lastParameter[0] == token.head.i or processed_entry[lastParameter[0]] in token.children) :
            # if "called" or a synonym is used for a parameter and not for an entity (e.g. "template called intel640")
            continue
        if match[1] == lastParameter[1] and match[1] not in ["name","position"] :
            # there should not be two same parameters in a row, except for a few ones
            continue
        if match[0] > SIMILARITY_THRESHOLD :
            # if is considered a key word (must exceed the threshold), is added to the dict
            if match[1] == "entity" and match[0] != 1 :
                # if an entity is not correctly wrote, we don't take any risk : we pass
                continue

            """
            TODO : handle the position example : "build a rack 1.1m from the left wall"
            if (match[1] == "position" 
                and match[1] == lastParameter[1] 
                and processed_entry[index].lower_ == "from"
                and processed_entry[lastParameter[0]].lower_ != "from") :
                continue
            """

            # the token is then added to the dict
            KEY_WORDS_ENTRY[index] = match[1] 
            if match[1] in PARAMETERS_DICT_KEYS :
                lastParameter = (index,match[1])

    return KEY_WORDS_ENTRY

def NL_to_OCLI(ocliFile : str) -> str :
    """
    The only function launched at the start. Asks for input and calls the other required functions
    """
    
    importlib.reload(wiki) # only for tests
    FINAL_INSTRUCTION = ""
    TAKEN_INDEXES = [] # all the indexes already used somewhere (keywords, value...) -> to not be assigned to multiple things by error

    EXISTING_ENTITY_NAMES = scrapping.scrapAllName(ocliFile)

    natural_entry = input("Enter a prompt. Please follow the instructions given.\n")
    processed_entry = nlp(natural_entry)

    KEY_WORDS_ENTRY = getKeyWords(processed_entry)
    print("KEY_WORDS_ENTRY : ", KEY_WORDS_ENTRY)
    TAKEN_INDEXES.extend(KEY_WORDS_ENTRY.keys())

    dictEntities = {index : processed_entry[index].text for index,keyword in KEY_WORDS_ENTRY.items() if keyword == "entity"}

    dictioNameIndexes, dictEntities, TAKEN_INDEXES = name(processed_entry = processed_entry,
                                                            dictioEntities = dictEntities,
                                                            dictioNameIndexes = {},
                                                            listNameSynonyms = [index for index,parameter in KEY_WORDS_ENTRY.items() if parameter == "name"],
                                                            takenIndexes = TAKEN_INDEXES,
                                                            indexesMain = {},
                                                            EXISTING_ENTITY_NAMES = EXISTING_ENTITY_NAMES,
                                                            searchRawEnabled = True)
    # this call, with searchRaw enabled, is mainly to identify non specified entities (e.g. "place in ROOM1 the rack ..." -> there is no "room" keyword)

    # test detection
    list_key_param = list(KEY_WORDS_ENTRY.values())
    count_action = 0 # the nb of action words indentified
    for action_type in ACTIONS_DEFAULT_KEYS :
        count_action += list_key_param.count(action_type)

    if count_action != 1 :
        # there should be only one action per sentence given
        raise Exception("Action not detected")
    
    # TODO : check entities
    # if no entity mentionned : must be alteration
    # if no entity and color, seek for keyword reserved etc besides the color

    # if no entity : check the ocli file
    indexAction= [index for index,keyword in KEY_WORDS_ENTRY.items() if keyword in ACTIONS_DEFAULT_KEYS][0]
    finalRelations = findRelations(processed_entry, dictEntities, indexAction)
    print("relations : ", finalRelations)
    indexMainSubject = findIndexMainSubject(processed_entry, KEY_WORDS_ENTRY, indexAction, INDEX_MAIN_ENTITY)  

    INDEXES_MAIN = {"subject" : indexMainSubject, 
                    "action" : indexAction, 
                    "entity" : INDEX_MAIN_ENTITY}
    print("INDEXES_MAIN : ", INDEXES_MAIN)

    # now that the main purpose of the sentence is identified, we call name back to find all remaining entities without name
    dictioNameIndexes, dictEntities, TAKEN_INDEXES = name(processed_entry = processed_entry,
                                                            dictioEntities = dictEntities,
                                                            dictioNameIndexes = dictioNameIndexes,
                                                            listNameSynonyms = [index for index,parameter in KEY_WORDS_ENTRY.items() if parameter == "name"],
                                                            takenIndexes = TAKEN_INDEXES,
                                                            indexesMain = INDEXES_MAIN,
                                                            EXISTING_ENTITY_NAMES = EXISTING_ENTITY_NAMES,
                                                            searchRawEnabled = False)
    
    dictioEntityNames = {}
    # we build the names from the related indexes
    for entityIndex, valueIndexes in dictioNameIndexes.items() :
        stringName = "".join([processed_entry[index].text for index in valueIndexes])
        if stringName[-1] in ["/","\\"] : stringName = stringName[:-1]
        dictioEntityNames[entityIndex] = stringName
    print("dictioEntityNames : ",dictioEntityNames)
    print("dictEntities : ", dictEntities)

    if not INDEXES_MAIN["entity"] in dictioEntityNames.keys() :
        dictioEntityNames[INDEXES_MAIN["entity"]] = scrapping.createDefaultName(dictEntities[INDEXES_MAIN["entity"]], EXISTING_ENTITY_NAMES)
    
    association = associateParameters(processed_entry, KEY_WORDS_ENTRY, dictEntities, dictioEntityNames)
    print("association : ", association)

    fullName = buildFullName(dictioEntityNames = dictioEntityNames, 
                             dictEntities = dictEntities, 
                             finalRelations = finalRelations, 
                             entityIndex = INDEX_MAIN_ENTITY, 
                             EXISTING_ENTITY_NAMES = EXISTING_ENTITY_NAMES, 
                             actionType = KEY_WORDS_ENTRY[INDEXES_MAIN["action"]])
    print("fullname : ", fullName)
    if fullName == None:
        raise ValueError("Not all the parent tree is known to name the object.")
    
    # Now time to switch cases depending on the entry
    if (INDEXES_MAIN["subject"] in KEY_WORDS_ENTRY.keys() 
        and INDEXES_MAIN["subject"] == INDEXES_MAIN["entity"]) :
        # if the main subject is an entity

        if KEY_WORDS_ENTRY[INDEXES_MAIN["action"]] == "ACTION_POSITIVE" :
            # if it's asked to create a new entity
            if fullName in EXISTING_ENTITY_NAMES.keys():
                raise ValueError(f'This {dictEntities[INDEXES_MAIN["subject"]]} already exists.')
            
            dictioEntityParameters = {}
            listGivenParameters = []
            # we make the list of all parameters attached to the entity
            for index,(entityIndex, parameterName) in association.items() :
                if entityIndex == INDEXES_MAIN["subject"] :
                    listGivenParameters.append(parameterName)
            isGivenTemplate = "template" in listGivenParameters
            if dictEntities[INDEXES_MAIN["subject"]] == "device" :
                dictioEntityParameters = wiki.makeDictParam(dictEntities[INDEXES_MAIN["subject"]], isGivenTemplate, listGivenParameters)
            else :
                dictioEntityParameters = wiki.makeDictParam(dictEntities[INDEXES_MAIN["subject"]], isGivenTemplate)

            dictioEntityParameters["name"] = fullName.upper()
            allEntryItemsList = list(KEY_WORDS_ENTRY.items())

            # get the parameter value for all parameters linked to the entity
            for counter,(keywordIndex,parameterName) in enumerate(allEntryItemsList) :
                if ((parameterName not in PARAMETERS_DICT_KEYS) 
                    or parameterName not in dictioEntityParameters.keys()
                    or dictioEntityParameters[parameterName]
                    or association[keywordIndex][0] != INDEXES_MAIN["subject"]) :
                    continue
                lastKeyWordIndex = 0 if counter == 0 else allEntryItemsList[counter-1][0]
                nextKeyWordIndex = len(processed_entry) if counter == len(allEntryItemsList)-1 else allEntryItemsList[counter+1][0]
                # get the parameter value
                parameterValue, parameterIndexes = get.FUNCTIONS[parameterName](processed_entry = processed_entry, 
                                                                            index = keywordIndex, 
                                                                            attachedEntity = dictEntities[association[keywordIndex][0]], 
                                                                            lastKeyWordIndex = lastKeyWordIndex, 
                                                                            nextKeyWordIndex = nextKeyWordIndex, 
                                                                            forbiddenIndexes = TAKEN_INDEXES)
                TAKEN_INDEXES.extend(parameterIndexes)
                dictioEntityParameters[parameterName] = parameterValue # store the value

            # if some parameters don't have a given value, we take the default value if available
            for parameterName, value in dictioEntityParameters.items() :
                if value == None and dictEntities[INDEXES_MAIN["entity"]] in wiki.DEFAULT_VALUE.keys() and parameterName in wiki.DEFAULT_VALUE[dictEntities[INDEXES_MAIN["entity"]]] :
                    dictioEntityParameters[parameterName] = wiki.DEFAULT_VALUE[dictEntities[INDEXES_MAIN["entity"]]][parameterName]
            
            print("dictioEntityParameters : ", dictioEntityParameters)
            FINAL_INSTRUCTION = tools.create(dictEntities[INDEXES_MAIN["subject"]], dictioEntityParameters)

        elif KEY_WORDS_ENTRY[INDEXES_MAIN["action"]] == "ACTION_NEGATIVE" :
            FINAL_INSTRUCTION = tools.delete("", {"name" : fullName})
        
        else :
            raise NotImplementedError("The action '"+KEY_WORDS_ENTRY[INDEXES_MAIN["action"]]+"' has not been implemented for '"+KEY_WORDS_ENTRY[INDEXES_MAIN["subject"]]+"' as main subject")

    else : # (if the main subject is a parameter)

        # TODO : if parameter is "name"

        if KEY_WORDS_ENTRY[INDEXES_MAIN["action"]] == "ACTION_POSITIVE" :

            allEntryItemsList = list(KEY_WORDS_ENTRY.items())
            for counter,(keywordIndex,parameterName) in enumerate(allEntryItemsList) :

                if (not parameterName in PARAMETERS_DICT_KEYS) or parameterName == "name": # or association[keywordIndex][0] != INDEX_MAIN_ENTITY
                    continue

                lastKeyWordIndex = 0 if counter == 0 else allEntryItemsList[counter-1][0]
                nextKeyWordIndex = len(processed_entry) if counter == len(allEntryItemsList)-1 else allEntryItemsList[counter+1][0]
                # get the parameter value
                parameterValue, parameterIndexes = get.FUNCTIONS[parameterName](processed_entry = processed_entry,
                                                                                index = keywordIndex, 
                                                                                attachedEntity = dictEntities[association[keywordIndex][0]], 
                                                                                lastKeyWordIndex = lastKeyWordIndex, 
                                                                                nextKeyWordIndex = nextKeyWordIndex, 
                                                                                forbiddenIndexes = TAKEN_INDEXES)
                TAKEN_INDEXES.extend(parameterIndexes)
                fullName = buildFullName(dictioEntityNames, dictEntities, finalRelations, association[keywordIndex][0], EXISTING_ENTITY_NAMES, KEY_WORDS_ENTRY[INDEXES_MAIN["action"]])
                if fullName == None:
                    raise ValueError("Not all the parent tree is known to name the object.")
                
                # TODO : we should only create attribute for parameters directly linked to the main action
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
            print("parameterValue : ", parameterValue)
            TAKEN_INDEXES.extend(parameterIndexes)

            fullName = buildFullName(dictioEntityNames, dictEntities, finalRelations, attachedEntityIndex, EXISTING_ENTITY_NAMES, KEY_WORDS_ENTRY[INDEXES_MAIN["action"]])
            if fullName == None:
                raise ValueError("Not all the parent tree is known to name the object.")
            
            if INDEXES_MAIN["subject"] not in KEY_WORDS_ENTRY.keys() : parameterName = processed_entry[INDEXES_MAIN["subject"]]
            
            if INDEXES_MAIN["subject"] in KEY_WORDS_ENTRY.keys() and KEY_WORDS_ENTRY[INDEXES_MAIN["subject"]] == "name":
                # if a name is changed, we build the new full name
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
    
    # TODO
    # if seeking the name for the main entity, pass the indexAction as parameter
    # if no name found, check the type of action : if +, a name is needed, otherwise not necessarily

    # check if parameters were not given
    print("FINAL_INSTRUCTION : ", FINAL_INSTRUCTION)
    return FINAL_INSTRUCTION

# automatically runs the file
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

