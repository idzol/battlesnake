# from typing import List, Dict

# import numpy as np
# import pandas as pd
# import random as rand
import copy as copy

import constants as CONST

# import itemClass as item
class item:

    name = ""
    itemType = "" 
    types = ["food", "hazard"]
    location = [] 
    distances = {}
    
    def __init__(self, t, p):
      
        if(not isinstance(p, dict)):
          # QQ 
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
        n = self.name
        return copy.copy(n)

    def setName(self, n):
        self.name = n

    def getType(self):
        t = self.itemType
        return copy.copy(t)

    def setType(self, t):
        self.type = copy.copy(t)
        return True

    def getLocation(self):
        r = self.location
        return r[:]

    def setLocation(self, pt):

        if (isinstance(pt, list)):
          self.location = copy.copy(pt)
          return True 

        elif (isinstance(pt, dict)):
          self.location = [pt['y'], pt['x']]
          return True
        
        else:
          return False

                           
  