from typing import List, Dict

import random as rand
import constants as CONST

# from functions import selectDestination


class snake:

    def __init__(self, data=""):
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

        self.setLocation(data)
        self.shout = ""

    def showStats(self): 
        print("""
  Health: %d
  Hunger: %d
  Aggro: %d
  Threat: %d
  Head: %s
  Target: %s
  Strategy: %s
        """ % (self.health, self.hunger, self.aggro, self.threat, self.head, self.target, self.strategy))

    def setHead(self, p):
        if (not isinstance(p, list)):
          print("ERROR: setHead(self, p) - list expected of format [y, x]") 
        else:       
          self.head = p

    def setBody(self, p):
        if (not isinstance(p, list)):
          print("ERROR: setBody(self, p) - list expected of format [[y1, x1], [y2, x2],..]") 
        else: 
          self.body = p 
          self.setLength(len(p))

    def setLength(self, l):
          self.length = l + 1   # TODO:  Check if correct (body + head)

    def getLength(self):
          return self.length

    def getHead(self):
        return self.head

    def getBody(self):
        return self.body

    def getLocation(self, p):

        if(p == "head"):
          return self.head

        elif(p == "body"):
          return self.body
          
        else: 
          return [-1,-1]

    # TODO:  Include list / array option    
    def setAll(self, data):

        health = data['you']['health'] 

        self.setLocation(data)
        self.setHealth(health)
        
        aggro = 50
        hunger = 100 - health
        threat = 50

        self.setHunger(hunger)
        self.setThreat(threat) 
        self.setAggro(aggro)
        

    def setLocation(self, data):
        try:
          head = data['you']['head']
          body = data['you']['body']
          b = []

          self.head = [head['y'],head['x']]

          for pt in body:
            b.append([pt['y'],pt['x']])
          
          self.body = b

        except: 
          self.head = [-1,-1] 
          self.body = [-1,-1]
     
    def setRoute(self, r):
        self.route = r
        return True
    
    def getRoute(self):
        return self.route

    def getThreat(self):
        return self.threat

    def setThreat(self, t):
        self.threat = t


    def getHealth(self):
        return self.health

    def setHealth(self, h):
        self.health = h

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
            self.aggro = a
            return True
        else:
            return False 

    # review strategy and update 
    def setStrategy(self, s, sinfo):
    
      self.strategy = s
      self.strategyinfo = sinfo


    # review strategy and update 
    def getStrategy(self):

      s = self.strategy
      sinfo = self.strategyinfo
      return (s, sinfo)

  
    def setTarget(self, dest):
      
      if (isinstance(dest, dict)):
        self.target = [dest['y'],dest['x']]
       
      elif (isinstance(dest, list)):
        self.target = dest


    def getTarget(self):
      return self.target

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
      return self.shout
      
