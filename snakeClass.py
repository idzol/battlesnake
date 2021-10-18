from typing import List, Dict

from logger import log

import random as rand
import constants as CONST
import copy as copy 

import functions as fn 


class snake:

    def __init__(self, data=""):

        depth = CONST.maxPredictTurns
        self.predict = [None] * (depth + 1)
        
        self.interruptlist = []
        self.strategyinfo = {}
        self.strategylist = [["Eat",""]]
        
        self.interrupt = False

        self.head = [] 
        self.body = []  
        self.tail = []  
        self.target = []  
        self.route = []     # Vector notation
        self.path = []      # Point notation
        self.routeHistory = []
        
        self.aggro = CONST.aggroLow   # out of 100 
        self.hunger = 0  # out of 100 
        self.eating = False 
        self.health = 100 
        self.length = 0

        self.identity = ""  # ID, eg. gs_JMJSHhdpyWtGSj66Sv3Dt8yD
        self.name = ""  # idzol, brensch .. 
        self.type = ""  # us, team, friendly, enemy 

        # TODO: Randomise, only used for some strats 
        self.move = "right" # .. 
        self.direction = "right" # direction of travel 
        self.shout = ""
        # self.setLocation(data)


    def setAll(self, data):

        health = data['health'] 
        length = data['length'] 
        name = data['name']

        self.setName(name)
        # Set new location 
        self.setLocation(data)
        self.setEating()
        # Save location to history 
        self.savePath()
        
        # Set attributes
        self.setHealth(health)
        self.setLength(length)

        # Set meta 
        aggro = CONST.aggroLow
        hunger = 100 - health
        self.setHunger(hunger)
        self.setAggro(aggro)
        

    def setEnemy(self, data):
        # TODO:  Include additional parameters like how the snake is feeling (health, strat etc..) 
        name = data['name']

        self.setName(name)
        self.setType("enemy")
        self.setId(data['id'])
        
        self.setEating() 
        # Set new location 
        self.setLocation(data)

        # Save location to history 
        self.savePath()
    
        self.setLength(data['length'])
        # self.setHealth(health)


    def showStats(self):

        log('snake-showstats', self.health, self.hunger, self.aggro, self.head, self.target, self.route, str(self.strategylist), self.direction)
        

    def setHead(self, p):
        if (not isinstance(p, list)):
          print("ERROR: setHead(self, p) - list expected of format [y, x]") 
        else:       
          self.head = copy.copy(p)

        
    def setPath(self, rt):        
        # Translate route to path
        # Note: may return blank [] for unknown locations  
        a = self.getHead()
        blist = copy.copy(rt)
        # Insert first point (head)
        pts = [a]
        # Iterate through vector 
        for b in blist:
          # Iterate through list 
          try:
            p = fn.getPointsInLine(a, b)
            pts.append(p.pop(0))
          except Exception as e:
            log('exception', 'setPath', str(e))
            # TODO: handle blank return from functions, eg. [] ..  
            pass

          a = copy.copy(b)

        # print("SNAKE PATH", str(self.getType()), str(pts))
        self.path = copy.copy(pts)
                

    def getPath(self):        
        return copy.copy(self.path)
        
        
    def setBody(self, p):
        if (not isinstance(p, list)):
          print("ERROR: setBody(self, p) - list expected of format [[y1, x1], [y2, x2],..]") 
        else:
          self.body = copy.copy(p)
          self.setLength(len(p) + 1)


    def savePath(self):
        # Save current location to route history (list)
        h = self.getHead()
        rth = self.routeHistory
        rth.insert(0, h)
        self.routeHistory = rth


    def getDirection(self):
        # Compare last two points to get direction   
        h = self.routeHistory
        if(len(h) > 1):
          # Check at least two points 
          a = h[1]
          b = h[0]
          self.direction = fn.translateDirection(a, b)
          
        else:
          # Use default path (ie. right)
          pass 

        d = copy.copy(self.direction)
        return d

    def setMove(self, m):
        self.move = copy.copy(m)
        
    def getMove(self):
        m = copy.copy(self.move)
        return m
      
    def getTail(self):

        if (len(self.body)):
          self.tail = self.body[-1]
          return copy.copy(self.tail)
        else:
          return []

    def setId(self, i):
        self.identity = copy.copy(i)
        
    def getId(self):
        i = copy.copy(self.identity)
        return i

    def setName(self, n):
        self.name = copy.copy(n)
        
    def getName(self):
        return copy.copy(self.name)
        
    def setLength(self, l):
          self.length = copy.copy(l)  
          # TODO:  Check if correct (body + head)

    def setType(self, t):
        self.type = copy.copy(t)
        
    def getType(self):
        t = copy.copy(self.type)
        return t

    def setName(self, n):
        self.name = copy.copy(n)
        
    def getName(self):
        n = copy.copy(self.name)
        return n

    def getLength(self):
        return copy.copy(self.length)

    def getHead(self):
        r = self.head
        return r[:]

    def getBody(self):
        r = self.body
        return r[:]

    # TODO:  Test 
    def getHeadBody(self):
        b = copy.copy(self.body)
        h = copy.copy(self.head)
        b.insert(0, h) 
        return b[:]

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

        
        
    def setLocation(self, data):
        try:
          head = data['head']
          body = data['body']
          b = []

          self.head = [head['y'], head['x']]

          for pt in body:
            b.append([pt['y'],pt['x']])
          
          self.body = b

        except Exception as e:
          log('exception', 'setLocation', str(e))
          self.head = [-1,-1] 
          self.body = [-1,-1]
     
    def setRoute(self, r):
        self.route = copy.copy(r)
        return True
    
    def getRoute(self):
        r = self.route
        return r[:]

    def getHealth(self):
        return self.health

    def setHealth(self, h):
        self.health = h

    def getEating(self):
        return copy.copy(self.eating)

    def setEating(self):
        b = self.getBody()
        l = self.getLength()
        e = False 
        if (l > 2): 
          # If last two points are the same 
          if(b[-1] == b[-2]):
            e = True

        self.eating = e

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

    def getInterrupt(self):
        return copy.copy(self.interruptlist)

    def setInterrupt(self, i): 
        self.interruptlist = copy.copy(i)

    def setStrategy(self, s, sinfo):
    # review strategy and update 
      self.strategylist = copy.copy(s)
      self.strategyinfo = copy.copy(sinfo)


    def getStrategy(self):
    # review strategy and update 
      s = copy.copy(self.strategylist)
      sinfo = copy.copy(self.strategyinfo)
      return (s, sinfo)

  
    def setTarget(self, dest):   
      if (isinstance(dest, dict)):
        t = [dest['y'],dest['x']]
       
      else:
          # (isinstance(dest, list)):
          # elif (type(dest).__module__ == np.__name__):
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
      
