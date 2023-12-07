import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_directory, '..', 'items'))

from Tag import Tag

tag = Tag("slug", "red")

tag1 = Tag("slug", [0,12,32])

if tag.isConform() and tag1.isConform():
    print("It works")

tag = Tag(None, None)

if not(tag.isConform()):
    print("Return false cause no slot was given")

tag = Tag("slot", [-1,-1,-1])

if not(tag.isConform()):
    print("Return false cause the rdg doesn't exist")

tag = Tag("slot", ["False",1,1])

if not(tag.isConform()):
    print("Return false cause the rdg doesn't exist")