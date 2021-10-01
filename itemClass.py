# from typing import List, Dict

# import numpy as np
# import pandas as pd
# import random as rand

import constants as CONST

# import itemClass as item
class item:

    name = ""
    itemType = "" 
    types = ["food","hazard"]
    location = {}    # {"x":0,"y":0}
    distances = {}
    
    def __init__(self, t, p):
      
        if(not isinstance(p, dict)):
          print("ERROR: item(t,p) expects location as dict")
          name = t + "@-1"
        else: 
          name = t + "@" + "x" + str(p['x']) + "y" + str(p['y']) 

        self.setType(t)
        self.setLocation(p) 
        self.setName(name)

    # # TODO:  is this complete?  
    # def getDistances(self, things): 
            
    #     d = []
    #     for t in things: 
    #         d.append(self.getDistance(t))
            
    #     return d 
    
    # # TODO:  is this complete? 
    # def getDistance(self, thing): 
        
    #     n = thing['name']
    #     d = thing.getLocation[dist]

    #     return {n:d}
            
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

        if (isinstance(pt, list)):
          self.location = pt
          return True 

        elif (isinstance(pt, dict)):
          self.location = [pt['y'], pt['x']]
          return True
        
        else:
          return False

                           
  