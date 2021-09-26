# from typing import List, Dict

# import numpy as np
# import pandas as pd
# import random as rand

# import itemClass as item
class item:

    name = ""
    itemType = "" 
    types = ["food","hazard"]
    location = {}    # {"x":0,"y":0}

    def __init__(self, t, p):
        self.type = t
        self.location = p 
        self.name = str(t) + "@x" + str(p['x']) + "y" + str(p['y'])
        
    def getName(self):
        return self.name

    def setName(self, n):
        self.name = n

    def getType(self):
        return self.itemType

    def setType(self, t):
        self.type = t
        return True

    def getLocation(self):
        return self.location

    def setLocation(self, pt):
        self.location = {'x':pt['x'], 'y':pt['y']}
        return True 