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
        positionList.extend(re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text))
    if not len(positionList) in LENGTH_CRITERIA :
        positionList = []
        for token in previous_words :
            positionList.extend(re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text))

    if not len(positionList) in LENGTH_CRITERIA :
        raise Exception("No position value detected")

    result = [float(coord) for coord in positionList]
    return result


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
        rotationList.extend(re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text))
    if len(rotationList) != LENGTH_CRITERIA :
        rotationList = []
        for token in previous_words :
            rotationList.extend(re.findall("^[-]*[0-9]+[.]*[0-9]*", token.text))

    if len(rotationList) != LENGTH_CRITERIA :
        raise Exception("No rotation value detected")
    else :
        rotationList = [float(x) for x in rotationList]
        isRotationNegative = re.search("counter.*clockwise", "".join([token.text for token in next_words]+[token.text for token in previous_words]))
        if isRotationNegative :
            rotationList = [-x for x in rotationList]
        if attachedEntity in ["rack", "corridor"] :
            return rotationList
        else :
            return rotationList[0]
