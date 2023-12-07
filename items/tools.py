"""This module contains static tools for the different classes"""

def isListOfNumbers(lst : list) -> bool:
        n = len(lst)
        k = 0
        verified = True
        while verified and k < n:
            verified = verified and (type(lst[k]) in [float, int])
            k += 1
        return verified