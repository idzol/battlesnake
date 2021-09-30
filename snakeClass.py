from typing import List, Dict

import random as rand
import constants as CONST

# from functions import selectDestination


class snake:

    strategyList = ["enlarge", "attack", "defend", "stalk", "eat", "taunt"]
    # Enlarge -- focus on maximising snake size 
    # Eat -- focus on restoring health (may end up same as enlarge)..
    # Taunt -- full health, no attack options. eg. draw patterns
    # Attack -- larger, opportunity to kill (Eg. head to head collision)
    # Stalk -- larger, stay close to head.  Intercept food .. 
    # etc

    # strategy = "enlarge"  # "enlarge"
    # lastStrategy = ""

    # interrupt = False
    # # trigger interrupt on critical situations (eg. low health, under threat)

    # head = {}  # Dict - point {"x": 0, "y": 0}
    # body = {}  # Dict - list [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} 
    # target = {} # Dict - point 
    # route = {}  # Dict - list 
    
    # aggro = 20   # out of 100 
    # hunger = 0   # out of 100 
    
    # TODO:  Deduplicate with above
    def __init__(self, data=""):
        self.strategy = "enlarge"
        self.lastStrategy = ""
        self.interrupt = False

        self.head = {}  # Dict - point {"x": 0, "y": 0}
        self.body = {}  # Dict - list [ {"x": 0, ...
        self.target = {} # Dict - point 
        self.route = {}  # Dict - list 
        
        self.aggro = 20   # out of 100 
        self.hunger = 0  # out of 100 

        self.setLocation(data)
        self.shout = ""
  
    # TODO:  Only supports dict for body ..  
    def getLocation(self, p, t="array"):

        h = self.head
        b = self.body
        if(p == "head"):

          if(t == "array"):
            return ([h['y'],h['x']])
          else:
            return h

        elif(p == "body"):
          return self.body 
          
        else: 
          return {}

    # TODO:  Include list / array option    
    def setLocation(self, data):
        try:
          self.head = data['you']['head'] 
          self.body = data['you']['body'] 

        except: 
          self.head = {'x':0,'y':0} 
          self.head = {'x':0,'y':0}
          # self.head = [0,0]
          # self.body = [0,0]
        
    def setRoute(self, r):
        self.route = r
        return True
    
    def getRoute(self):
        return self.route
    
    def getHunger(self):
        return self.hunger
    
    def setHunger(self, h):
        if isinstance(h, int):
            hunger = h 
            return True
        else:
            return False 
    
    def getAggro(self):
        return self.aggro
    
    def setAggro(self,a):
        if isinstance(a, int):
            aggro = a
            return True
        else:
            return False 

    def getStrategy(self):
        return self.strategy
    
    def setStrategy(self, s):
        if (s in self.strategyList):
            strategy = s
            return True
        else:
            return False
    
    # review strategy and update 
    def updateStrategy(self,data):
    
      # enlarge 
      # attack 
      # defend
      # eat 
      # stalk 
      # random -- loiter 

      return True
  
    # TODO: Try save all points as array (not dict)
    def setTarget(self, dest):
      self.target = dest

    def getTarget(self):
      return self.target

    def setShout(self, turn):
      
      # Shout every 10 turns 
      if (turn % CONST.shoutFrequency == 0): 
        strat = self.getStrategy()  
        #     if (strategy=="enlarge"):
        #     elif (strategy=="taunt"):
        #     ...  
        self.shout = CONST.shouts[int(len(CONST.shouts) * rand.random())]
        
      return self.getShout()


    def getShout(self):
      return self.shout
      
