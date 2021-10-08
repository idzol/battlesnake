from typing import List, Dict

import logger as log 

import random as rand
import constants as CONST
import copy as copy 

# from functions import selectDestination


class snake:

    def __init__(self, data=""):

        depth = CONST.maxPredictTurns
        self.predict = [None] * (depth + 1)
        self.strategy = ["Eat",""]
        self.strategyinfo = {}
        self.strategylast = []
        
        self.interrupt = False

        self.head = [] 
        self.body = []  
        self.target = []  
        self.route = []  
        
        self.threat = 50
        self.aggro = 50   # out of 100 
        self.hunger = 0  # out of 100 
        self.health = 100 
        self.length = 3

        self.id = ""    # ID, eg. gs_JMJSHhdpyWtGSj66Sv3Dt8yD
        self.type = ""  # us, team, friendly, enemy 

        # TODO: Randomise, only used for some strats 
        self.direction = "right"
        self.shout = ""
        self.setLocation(data)


    # def resetCounters(self):
      
    #     self.direction = ""
    #     self.shout = ""

    def showStats(self):

        log.log('snake-showstats', self.health, self.hunger, self.aggro, self.threat, self.head, self.target, self.route, self.strategy, self.direction)
        

    def setHead(self, p):
        if (not isinstance(p, list)):
          print("ERROR: setHead(self, p) - list expected of format [y, x]") 
        else:       
          self.head = copy.copy(p)

    def setBody(self, p):
        if (not isinstance(p, list)):
          print("ERROR: setBody(self, p) - list expected of format [[y1, x1], [y2, x2],..]") 
        else:
          self.body = copy.copy(p)
          self.setLength(len(p) + 1)

    def setDirection(self, d):
        self.direction = copy.copy(d)
        
    def getDirection(self):
        d = copy.copy(self.direction)
        return d
        
    def setId(self, i):
        self.identity = copy.copy(i)
        
    def getId(self):
        i = copy.copy(self.identity)
        return i
        
    def setLength(self, l):
          self.length = copy.copy(l)  
          # TODO:  Check if correct (body + head)

    def setType(self, t):
        self.type = copy.copy(t)
        
    def getType(self):
        t = copy.copy(self.type)
        return t

    def setPath(self, p):
        self.path = copy.copy(p)
     
    def getPath(self):
        p = copy.copy(self.path)
        return p 

    def getLength(self):
        return copy.copy(self.length)

    def getHead(self):
        r = self.head
        return r[:]

    def getBody(self):
        r = self.body
        return r[:]

    def setPredict(self, p):
        self.predict = copy.copy(p)
        
    def getPredict(self):
        p = copy.copy(self.predict)
        return p

    def getLocation(self, p):
        if(p == "head"):
          return copy.copy(self.head)

        elif(p == "body"):
          return copy.copy(self.body)
          
        else: 
          return [-1,-1]

    # TODO:  Include list / array option    
    def setAll(self, data):

        health = data['health'] 
        
        self.setLocation(data)
        self.setHealth(health)
        
        aggro = 50
        hunger = 100 - health
        threat = 50

        self.setHunger(hunger)
        self.setThreat(threat) 
        self.setAggro(aggro)
        

    def setEnemy(self, data):
        # TODO:  Include additional parameters like how the snake is feeling (health, strat etc..) 
       
        self.setLocation(data)
        # self.setHealth(health)
        
        
    def setLocation(self, data):
        try:
          head = data['head']
          body = data['body']
          b = []

          self.head = [head['y'],head['x']]

          for pt in body:
            b.append([pt['y'],pt['x']])
          
          self.body = b

        except: 
          self.head = [-1,-1] 
          self.body = [-1,-1]
     
    def setRoute(self, r):
        self.route = copy.copy(r)
        return True
    
    def getRoute(self):
        r = self.route
        return r[:]

    def getThreat(self):
        t = copy.copy(self.threat)
        return t

    def setThreat(self, t):
        self.threat = copy.copy(t)

    def getHealth(self):
        return self.health

    def setHealth(self, h):
        self.health = h

    def getHunger(self):
        return self.hunger
    
    def setHunger(self, h):
        if isinstance(h, int):
            self.hunger = copy.copy(h) 
            return True
        else:
            return False 
    
    def getAggro(self):
        a = copy.copy(self.aggro)
        return a
    
    def setAggro(self,a):
        if isinstance(a, int):
            self.aggro = copy.copy(a)
            return True
        else:
            return False 

    # review strategy and update 
    def setStrategy(self, s, sinfo):
      self.strategy = copy.copy(s)
      self.strategyinfo = copy.copy(sinfo)


    # review strategy and update 
    def getStrategy(self):
      s = copy.copy(self.strategy)
      sinfo = copy.copy(self.strategyinfo)
      return (s, sinfo)

  
    def setTarget(self, dest):   
      if (isinstance(dest, dict)):
        t = [dest['y'],dest['x']]
       
      elif (isinstance(dest, list)):
        t = dest

      self.target = copy.copy(t)

    def getTarget(self):
      r = self.target
      return r[:]

    def setShout(self, turn):
      # Shout every 10 turns 
      if (turn % CONST.shoutFrequency == 0): 
        s, sinfo = self.getStrategy()  
        #     if (strategy=="enlarge"):
        #     elif (strategy=="taunt"):
        #     ... 
 
        self.shout = CONST.shouts[int(len(CONST.shouts) * rand.random())]
      
      return self.getShout()


    def getShout(self):
      s = copy.copy(self.shout)
      return s 
      
