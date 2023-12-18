import spacy
from spacy.tokens import Doc, Token
nlp = spacy.load("en_core_web_md")
from typing import Optional
import re
import ogree_wiki as wiki


def template(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :
    next_words = [token for token in processed_entry[index+1:nextKeyWordIndex] if token.i not in forbiddenIndexes]
    previous_words = [token for token in processed_entry[lastKeyWordIndex+1:index] if token.i not in forbiddenIndexes]
    
    def isTemplate(token : Token) -> bool :
        if token.pos_ == "NOUN" or token.pos_ == "PROPN" : return True
        return False   

    # find the first token of the template name
    def findNameFirst(processed_entry : Doc, index : int) :
        name = ""
        indexes = []

        if list(processed_entry[index].children) : # we first seek in the children
            for token in processed_entry[index].subtree :
                tokenRealIndex = list(processed_entry).index(token)
                if tokenRealIndex in forbiddenIndexes : continue
                if (isTemplate(token) or 
                    (tokenRealIndex+2 < len(processed_entry) and processed_entry[tokenRealIndex +1].lower_ == "-")) :
                    name, indexes = findFullName(processed_entry, tokenRealIndex)
                    break
        
        if not name : # if none found, seek in the next words
            for token in next_words :
                tokenRealIndex = list(processed_entry).index(token)
                if (isTemplate(token) or 
                    (tokenRealIndex+2 < len(processed_entry) and processed_entry[tokenRealIndex +1].lower_ == "-")) :
                    name, indexes = findFullName(processed_entry, tokenRealIndex)
                    break
        if not name : # finally in the previous
            for token in previous_words :
                tokenRealIndex = list(processed_entry).index(token)
                if (isTemplate(token) or 
                    (tokenRealIndex+2 < len(processed_entry) and processed_entry[tokenRealIndex +1].lower_ == "-")) :
                    name, indexes = findFullName(processed_entry, tokenRealIndex)
                    break

        return name, indexes
    
    # find the full name of the template, from the start token
    def findFullName(processed_entry : Doc, index : int) :
        name = ""
        indexes = []

        currentIndex = index
        isNameFinished = False
        while not isNameFinished :
            validIndex = currentIndex not in forbiddenIndexes
            indexJump = 1
            # if there is a dash, we take both current and next word (and the dash)
            if validIndex and currentIndex+2 < len(processed_entry) and processed_entry[currentIndex+1].lower_ == "-" :
                if currentIndex+1 in forbiddenIndexes or currentIndex+2 in forbiddenIndexes :
                    currentIndex += 1
                    continue
                name = name + processed_entry[currentIndex].lower_ + processed_entry[currentIndex+1].lower_ + processed_entry[currentIndex+2].lower_
                indexes.extend([currentIndex, currentIndex+1, currentIndex+2])
                indexJump = 3
            elif validIndex and isTemplate(processed_entry[currentIndex]) :
                name = name + processed_entry[currentIndex].lower_ + "-"
                indexes.append(currentIndex)

            if currentIndex + indexJump > len(processed_entry)-1 : 
                isNameFinished = True
            else : 
                currentIndex += indexJump

        if name[-1] == "-" :
            name = name[:-1]
        return name, indexes

    resultValues = ""
    resultIndexes = []

    # if synonym of "called", start to seek from this token
    if (index +1 <= len(processed_entry)-1 
        and processed_entry[index+1].similarity(nlp("called")[0]) > 0.5
        and processed_entry[index].is_ancestor(processed_entry[index+1])) :
        resultValues, resultIndexes = findNameFirst(processed_entry, index+1)

    else :
        resultValues, resultIndexes = findNameFirst(processed_entry, index)

    if not resultValues : 
        raise Exception("No template value detected")
    else :
        return resultValues, resultIndexes


def position(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :
    next_words = [token for token in processed_entry[index+1:nextKeyWordIndex] if token.i not in forbiddenIndexes]
    previous_words = [token for token in processed_entry[lastKeyWordIndex+1:index] if token.i not in forbiddenIndexes]

    LENGTH_CRITERIA = [2] 
    if attachedEntity == "device"  : LENGTH_CRITERIA = [1]
    if attachedEntity in ["rack", "corridor"] : LENGTH_CRITERIA.append(3)

    positionList = []
    for token in next_words :
        foundValue = re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text)
        if foundValue :  
            positionList.append((foundValue[0], token.i))
    if not len(positionList) in LENGTH_CRITERIA : # if none found in next words
        positionList = []
        for token in previous_words :
            foundValue = re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text)
            if foundValue :  
                positionList.append((foundValue[0], token.i))

    if not len(positionList) in LENGTH_CRITERIA :
        raise Exception("No position value detected")

    resultValues = [float(x[0]) for x in positionList]
    if attachedEntity == "device" :
        resultValues = resultValues[0]
    resultIndexes = [x[1] for x in positionList]
    return resultValues, resultIndexes


def rotation(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :
    next_words = [token for token in processed_entry[index+1:nextKeyWordIndex] if token.i not in forbiddenIndexes]
    previous_words = [token for token in processed_entry[lastKeyWordIndex+1:index] if token.i not in forbiddenIndexes]

    rotationKeyWordsDict = {"front": [0, 0, 180],
                        "rear": [0, 0, 0],
                        "left": [0, 90, 0],
                        "right": [0, -90, 0],
                        "top": [90, 0, 0],
                        "bottom": [-90, 0, 0]
                        }

    if attachedEntity in ["rack", "corridor"] :
        # seek key words in the dict above
        rotationKeyWordsList = list(rotationKeyWordsDict.keys())
        for token in next_words :
            if token.text in rotationKeyWordsList and processed_entry[index].is_ancestor(token) :
                return rotationKeyWordsDict[token.text]
        for token in previous_words :
            if token.text in rotationKeyWordsList and processed_entry[index].is_ancestor(token) :
                return rotationKeyWordsDict[token.text]

    LENGTH_CRITERIA = 3 if attachedEntity in ["rack", "corridor"] else 1
    isRotationNegative = False
    rotationList = []

    for token in next_words :
        foundValue = re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text)
        if foundValue :  
            rotationList.append((foundValue[0], token.i))
    if len(rotationList) != LENGTH_CRITERIA :
        rotationList = []
        for token in previous_words :
            foundValue = re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text)
            if foundValue :  
                rotationList.append((foundValue[0], token.i))

    if len(rotationList) != LENGTH_CRITERIA :
        raise Exception("No rotation value detected")
    else :
        resultValues = [float(x[0]) for x in rotationList]
        resultIndexes = [x[1] for x in rotationList]
        isRotationNegative = re.search("counter.*clockwise", "".join([token.lower_ for token in next_words]+[token.text for token in previous_words]))
        if isRotationNegative :
            rotationList = [-x for x in rotationList]
        if not attachedEntity in ["rack", "corridor"] :
            resultValues = resultValues[0]
        return resultValues, resultIndexes
        

def size(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :
    next_words = [token for token in processed_entry[index+1:nextKeyWordIndex] if token.i not in forbiddenIndexes]
    previous_words = [token for token in processed_entry[lastKeyWordIndex+1:index] if token.i not in forbiddenIndexes]

    LENGTH_CRITERIA = 3
    if attachedEntity == "pillar" :
        LENGTH_CRITERIA = 2
    if attachedEntity == "device" :
        LENGTH_CRITERIA = 1

    sizeList = []
    for token in next_words :
        foundValue = re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text)
        if foundValue :  
            sizeList.append((foundValue[0], token.i))
    if len(sizeList) != LENGTH_CRITERIA : # if none found in next words
        sizeList = []
        for token in previous_words :
            foundValue = re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text)
            if foundValue :
                sizeList.append((foundValue[0], token.i))

    if len(sizeList) != LENGTH_CRITERIA :
        raise Exception("No size value detected")
    else :
        resultValues = [float(x[0]) for x in sizeList]
        resultIndexes = [x[1] for x in sizeList]
        if attachedEntity == "device" :
            resultValues = resultValues[0]
        return resultValues, resultIndexes
        

def axisOrientation(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :
    next_words = [token for token in processed_entry[index+1:nextKeyWordIndex] if token.i not in forbiddenIndexes]
    previous_words = [token for token in processed_entry[lastKeyWordIndex+1:index] if token.i not in forbiddenIndexes]

    resultIndexes = []
    #An axis Orientation can be any combinason of [+/-]x[+/-]y. eg: +x+y or -x+y
    axisX = re.findall("[-\+]?[ ]?x", "".join([token.lower_ for token in next_words]))
    axisY = re.findall("[-\+]?[ ]?y", "".join([token.lower_ for token in next_words]))
    if len(axisX) in [0,1] and len(axisY) in [0,1] and len(axisX)+len(axisY) != 0 :
        # get the indexes
        for token in next_words :
            if token.lower_ in "".join(axisX + axisY) :
                resultIndexes.append(token.i)

    # if not found in the next words, seek in the previous words
    if len(axisX) not in [0,1] or len(axisY) not in [0,1] or len(axisX)+len(axisY) == 0 :
        resultIndexes = []
        axisX = re.findall("[-\+]?[ ]?x", "".join([token.lower_ for token in previous_words]))
        axisY = re.findall("[-\+]?[ ]?y", "".join([token.lower_ for token in previous_words]))
        if len(axisX) in [0,1] and len(axisY) in [0,1] and len(axisX)+len(axisY) != 0 :
            for token in previous_words :
                if token.lower_ in "".join(axisX + axisY) :
                    resultIndexes.append(token.i)

    if len(axisX) not in [0,1] or len(axisY) not in [0,1] or len(axisX)+len(axisY) == 0 :
        raise Exception("No axisOrientation value detected")
    
    # if the value is not comprehensive
    resultValues = ""
    if len(axisX) == 0 :
        resultValues = "+x" + axisY[0].replace(" ","")
    elif len(axisY) == 0 :
        resultValues = axisX[0].replace(" ","") + "+y"
    else :
        resultValues = axisX[0].replace(" ","") + axisY[0].replace(" ","")
    return resultValues, resultIndexes


def unit(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :

    DICT_UNIT = {
            "meter" : "m",
            "tile" : "t",
            "foot" : "f"
            }

    resultValues = []
    resultIndexes = []

    allWords = [token for token in processed_entry[lastKeyWordIndex+1:nextKeyWordIndex] if token.i not in forbiddenIndexes]
    for token in allWords :
        if token.lemma_ in DICT_UNIT.keys() : # if whole word
            resultValues.append(DICT_UNIT[token.lemma_])
            resultIndexes.append(token.i)
        if token.lower_ in DICT_UNIT.values() : # if only a letter
            resultValues.append(token.lower_)
            resultIndexes.append(token.i)

    if len(resultValues) != 1 :
        raise Exception("No unit value detected")
    else :
        return resultValues[0], resultIndexes
    

def findKeyWord(processed_entry : Doc, 
                index : int, 
                attachedEntity : str, 
                lastKeyWordIndex : int, 
                nextKeyWordIndex : int, 
                forbiddenIndexes : list = [],
                keyWordsList : list = []) :
    
    resultValues = []
    resultIndexes = []

    allWords = [token for token in processed_entry[lastKeyWordIndex+1:nextKeyWordIndex] if token.i not in forbiddenIndexes]
    for token in allWords :
        if token.lower_ in keyWordsList :
            resultValues.append(token.lower_)
            resultIndexes.append(token.i)
            break

    if len(resultValues) != 1 :
        return None,None
    else :
        return resultValues[0], resultIndexes
    
def color(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :
    # We first seek a keyword, if not found we directly seek a hexa code
    colorKeyWords = wiki.COLORS_HEX_BASIC.keys()
    if processed_entry[index].lower_ in colorKeyWords :
        return wiki.COLORS_HEX_BASIC[processed_entry[index].lower_], [index]
    else :
        value, indexes = findKeyWord(processed_entry, index, attachedEntity, lastKeyWordIndex, nextKeyWordIndex, forbiddenIndexes, colorKeyWords)
        if value != None and indexes != None :
            return wiki.COLORS_HEX_BASIC[value], [index]

    next_words = [token for token in processed_entry[index+1:nextKeyWordIndex] if token.i not in forbiddenIndexes]
    previous_words = [token for token in processed_entry[lastKeyWordIndex+1:index] if token.i not in forbiddenIndexes]

    resultIndexes = []
    resultValues = re.findall("#[ ]*[a-zA-Z0-9]{6}", "".join([token.text for token in next_words]))
    if len(resultValues) == 1 :
        for token in next_words :
            if token.text in resultValues[0] :
                resultIndexes.append(token.i)

    if len(resultValues) != 1 : # if none found, seek in the previous words
        resultValues = re.findall("#[ ]*[a-zA-Z0-9]{6}", "".join([token.text for token in previous_words]))
        if len(resultValues) == 1 :
            for token in previous_words :
                if token.text in resultValues[0] :
                    resultIndexes.append(token.i)

    if len(resultValues) != 1 : 
        raise Exception("Not color value detected")
    else : 
        return resultValues[0].replace(" ", ""), resultIndexes
    

def slot(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :
    return template(processed_entry, index, attachedEntity, lastKeyWordIndex, nextKeyWordIndex, forbiddenIndexes)


def side(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :
    sideKeyWords = ["front", "rear", "frontflipped", "rearflipped"]
    return findKeyWord(processed_entry, index, attachedEntity, lastKeyWordIndex, nextKeyWordIndex, forbiddenIndexes, sideKeyWords)


def temperature(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :
    temperatureKeyWords = ["cold","warm"]
    if processed_entry[index].lower_ in temperatureKeyWords :
        return processed_entry[index].lower_, [index]
    else :
        return findKeyWord(processed_entry, index, attachedEntity, lastKeyWordIndex, nextKeyWordIndex, forbiddenIndexes, temperatureKeyWords)

    
def type(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int, forbiddenIndexes : list = []) :
    typeKeyWords = ["wireframe","plain"]
    if processed_entry[index].lower_ in typeKeyWords :
        return processed_entry[index].lower_, [index]
    else :
        return findKeyWord(processed_entry, index, attachedEntity, lastKeyWordIndex, nextKeyWordIndex, forbiddenIndexes, typeKeyWords)




