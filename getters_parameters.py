from spacy.tokens import Doc, Token
from typing import Optional
import re


def position(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int) :
    next_words = processed_entry[index+1:nextKeyWordIndex+1]
    previous_words = processed_entry[lastKeyWordIndex:index]

    LENGTH_CRITERIA = [2] 
    if attachedEntity == "device"  :
        LENGTH_CRITERIA = [1]
    if attachedEntity in ["rack", "corridor"] :
        LENGTH_CRITERIA.append(3)

    positionList = []
    for token in next_words :
        foundValue = re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text)
        if foundValue :  
            positionList.append((foundValue[0], token.i))
    if not len(positionList) in LENGTH_CRITERIA :
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


def rotation(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int) :
    next_words = processed_entry[index+1:nextKeyWordIndex+1]
    previous_words = processed_entry[lastKeyWordIndex:index]

    rotationKeyWords = {"front": [0, 0, 180],
                        "rear": [0, 0, 0],
                        "left": [0, 90, 0],
                        "right": [0, -90, 0],
                        "top": [90, 0, 0],
                        "bottom": [-90, 0, 0]
                        }

    if attachedEntity in ["rack", "corridor"] :
        # seek key words in the dict above
        rotationKeyWordsList = list(rotationKeyWords.keys())
        for token in next_words :
            if token.text in rotationKeyWordsList and processed_entry[index].is_ancestor(token) :
                return rotationKeyWords[token.text]
        for token in previous_words :
            if token.text in rotationKeyWordsList and processed_entry[index].is_ancestor(token) :
                return rotationKeyWords[token.text]

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
        

def size(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int) :
    next_words = processed_entry[index+1:nextKeyWordIndex+1]
    previous_words = processed_entry[lastKeyWordIndex:index]

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
    if len(sizeList) != LENGTH_CRITERIA :
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
        

def axisOrientation(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int) :
    next_words = processed_entry[index+1:nextKeyWordIndex+1]
    previous_words = processed_entry[lastKeyWordIndex:index]

    resultIndexes = []
    #An axis Orientation can be any combinason of [+/-]x[+/-]y. eg: +x+y or -x+y
    axisX = re.findall("[-\+]?[ ]?x", "".join([token.lower_ for token in next_words]))
    axisY = re.findall("[-\+]?[ ]?y", "".join([token.lower_ for token in next_words]))
    for token in next_words :
        if token.lower_ in "".join(axisX + axisY) :
            resultIndexes.append(token.i)

    if len(axisX) not in [0,1] or len(axisY) not in [0,1] or len(axisX)+len(axisY) == 0 :
        resultIndexes = []
        axisX = re.findall("[-\+]?[ ]?x", "".join([token.lower_ for token in previous_words]))
        axisY = re.findall("[-\+]?[ ]?y", "".join([token.lower_ for token in previous_words]))
        for token in previous_words :
            if token.lower_ in "".join(axisX + axisY) :
                resultIndexes.append(token.i)

    if len(axisX) not in [0,1] or len(axisY) not in [0,1] or len(axisX)+len(axisY) == 0 :
        raise Exception("No axisOrientation value detected")
    
    resultValues = ""
    if len(axisX) == 0 :
        resultValues = "+x" + axisY[0].replace(" ","")
    elif len(axisY) == 0 :
        resultValues = axisX[0].replace(" ","") + "+y"
    else :
        resultValues = axisX[0].replace(" ","") + axisY[0].replace(" ","")
    return resultValues, resultIndexes


def unit(processed_entry : Doc, index : int, attachedEntity : str, lastKeyWordIndex : int, nextKeyWordIndex : int) :
    next_words = processed_entry[index+1:nextKeyWordIndex+1]
    previous_words = processed_entry[lastKeyWordIndex:index]

    DICT_UNIT = {
            "meter" : "m",
            "tile" : "t",
            "foot" : "f"
            }

    resultValues = []
    resultIndexes = []
    #An unit can be m, t , f, meters, tiles, feet

    for token in list(processed_entry[lastKeyWordIndex:nextKeyWordIndex+1]) :
        if token.lemma_ in DICT_UNIT.keys() :
            resultValues.append(DICT_UNIT[token.lemma_])
            resultIndexes.append(token.i)
        if token.lower_ in DICT_UNIT.values() :
            resultValues.append(token.lower_)
            resultIndexes.append(token.i)

    # TODO : meter etc in the key words ??
        
    if not resultValues :
        raise Exception("No unit value detected")
    else :
        return resultValues[0]

