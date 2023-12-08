"""This module contains static tools for the different classes"""
import re


def isListOfNumbers(lst : list) -> bool:
    n = len(lst)
    k = 0
    verified = True
    while verified and k < n:
        verified = verified and (type(lst[k]) in [float, int])
        k += 1
    return verified

def isHexColor(color : str) -> bool:
    return bool(re.compile(r"[0-9A-F]{6}").match(color))

def isOrientation(orientation : str) -> bool:
    return orientation in ["N","S","W","E","NW","NE","SW","SE","ESE"
                           "WNW","NNW","NNE","ENE","WSW","SSW","SSE"]


