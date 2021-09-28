from typing import List, Dict

import constants as CONST

# from functions import selectDestination


class snake:

    strategy = "enlarge"  # "enlarge"
    lastStrategy = ""
    strategyList = ["enlarge", "attack", "defend", "stalk", "eat", "taunt"]

    # Enlarge -- focus on maximising snake size 
    # Eat -- focus on restoring health (may end up same as enlarge)..
    # Taunt -- full health, no attack options. eg. draw patterns
    # Attack -- larger, opportunity to kill (Eg. head to head collision)
    # Stalk -- larger, stay close to head.  Intercept food .. 
    # etc

    interrupt = False
    # trigger interrupt on critical situations (eg. low health, under threat)

    head = {}  # Dict - point {"x": 0, "y": 0}
    body = {}  # Dict - list [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} 
    target = {} # Dict - point 
    route = {}  # Dict - list 
    
    aggro = 20   # out of 100 
    hunger = 0  # out of 100 
    
    # TODO:  Deduplicate with above
    def __init__(self):
        self.strategy = "enlarge"  # "enlarge"
        self.lastStrategy = ""
        self.interrupt = False

        self.head = {}  # Dict - point {"x": 0, "y": 0}
        self.body = {}  # Dict - list [ {"x": 0, ...
        self.target = {} # Dict - point 
        self.route = {}  # Dict - list 
        
        self.aggro = 20   # out of 100 
        self.hunger = 0  # out of 100 

    def getLocation(self, t):
        if(t == "head"):
          return self.head 
        elif(t == "body"):
          return self.body 
        else: 
          return {}

    def setLocation(self, data):
        self.head = data['you']['head'] 
        self.head = data['you']['body'] 

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
  
    def setTarget(self, dest):
      self.target = dest

    def getTarget(self):
      return self.target


    def getShout(self):
        
        # shouts = []
        # Import from constants 

        strat = self.getStrategy()
  
        #     if (strategy=="enlarge"):
        #     elif (strategy=="taunt"):
        #     else
          
        shout = CONST.shouts[int(len(taunts) * rand.random())]
        return shout

