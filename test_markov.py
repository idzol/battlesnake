
from typing import List, Dict

import math
import operator
from operator import add
import random as rand
import numpy as np
# import pandas as pd
# import random as rand
import copy as copy

import time as time
from logger import log

import constants as CONST
import functions as fn

# from snakeClass import snake


class snake():

    def __init__(self):
        self.futures = [None] * CONST.lookAhead
        self.markovs = [None] * CONST.lookAhead
        self.eating = False 
        self.length = 3

    def getPath(self):        
        return copy.copy(self.path)
        
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

    def getLength(self):
        return copy.copy(self.length)

    def getHead(self):
        r = self.head
        return r[:]

    def getHeadBody(self):
        b = copy.copy(self.body)
        h = copy.copy(self.head)
        b.insert(0, h) 
        return b[:]
        
    def getBody(self):
        r = self.body
        return r[:]


    def getEating(self):
        return copy.copy(self.eating)


    def setMarkov(self, m, t):
      self.markovs[t] = copy.copy(m) 


    def getMarkov(self, t):
      m = self.markovs[t]
      return copy.copy(m)

    def setFuture(self, b, t=0):
        future = { 
          'body':copy.copy(b)
          # 'head':copy.copy(head), 
          # 'tail':copy.copy(tail), 
          # 'length':copy.copy(length),
          # 'eating':copy.copy(eating),
          # 'direction':copy.copy(direction)
        }
        self.futures[t] = copy.copy(future)

    # def setFuturev2(self, b, t=0):
    #     self.futures[t] = copy.copy(b)

    # def getFuturev2(self, b, t=0):
    #     return self.futures[t]


    def getFuture(self, turn=0):
      future = copy.copy(self.futures[turn])
      if (future == None):
        return []
      else: 
        return future


class board():

    width = 11
    height = 11
    trails = np.zeros([height, width], np.intc)
    markovs = []
    markov = np.zeros([height, width], np.intc)
    
    def inBounds(self, a):
        # Check a point (a = [y,x]) is in map bounds

        # Invalid point -- return false
        if (not len(a)):
            return False

        h = self.height
        w = self.width

        try:
            if (0 <= a[0] < h) and (0 <= a[1] < w):
                return True
            else:
                return False

        except Exception as e:
            log('exception', 'inBounds', str(e))

        return False


    def updateMarkov(self, us:snake, snakes:dict, foods:list, turns=CONST.lookAhead): 
        # TODO: Assumes no solids, otherwise requires a version of route with gradient = 1..
        w = self.width
        h = self.height
        depth = CONST.lookAhead

        markovs = []   
        for t in range(0, turns - 1):
          
          # Iterate through snakes to get the first step / next step based on probability
          # snakes_updated = []
          for sid in snakes:
              
              sn = snakes[sid]
              markov = np.zeros([w,h], np.intc)
              sn_body = []
              sn_future = []
                
              # Prediction for first turn
              if (not t):
                # First move -- establish initial markov (t = 0) 
                sn_body = sn.getHeadBody()
                sn.setFuture(sn_body, 0)
                
              else:
                # Predict current move (t) based on last markov (t) 
                # Set future location ) 
                sn_body = self.predictMove_step(sn, foods, t - 1)
                sn.setFuture(sn_body, t)
                
              for cell in sn_body: 
                  if(self.inBounds(cell)):
                    # Paint markov matrix for turn t + 1
                    y = cell[0]
                    x = cell[1]
                    markov[y, x] = 100
              
              # Set markov 
              sn.setMarkov(copy.copy(markov), t)
              # Update markov probability 
              self.updateMarkov_step(sn, copy.deepcopy(snakes), foods, t)
              # snakes_updated.append(sn)
              snakes[sid] = copy.deepcopy(sn)


          # snakes = copy.deepcopy(snakes_updated)
          
          # Calculate next round of probabiliy based on new markov models
          # for sn in snakes:
          #     self.updateMarkov_step(sn, snakes, foods, t)
              
        
        # Sum all snakes into final markov matrix
        markovs = [None] * depth
        for sn in snakes:
          for t in range(0, turns - 1): 

            markovs[t] = np.zeros([w, h], np.intc)
            for snid in snakes:
                sn = snakes[snid]
                # markov_sn = sn[identity].getMarkov()
                markov_sn = sn.getMarkov(t)
                markovs[t] = markovs[t] + markov_sn

        self.markovs = copy.copy(markovs)
        return markovs


    def predictMove_step(self, target, foods, turn=0):
      # Based on markov for one snake, calculate most likely path -- eg. food, killcut, other
      # TODO:  Special logic for our snake (known path)
      
      # Get current body 
      
      snake = copy.copy(target)      
      sn_future = snake.getFuture(turn)
      
      
      body = sn_future['body']
      if (not (len(body))):
        return body

      
      # Get current markov 
      markov = snake.getMarkov(turn)
                 
      # Select path based on probability (start with highest)
      probs = np.nonzero((markov < 100) & (markov > 0))
      prob_max = 0
      prob_max_pt = []

      for i in range(0, len(probs[0] - 1)):
        prob_pt = [probs[0][i], probs[1][i]]
        prob = markov[prob_pt[0], prob_pt[1]]
        
        if prob > prob_max:
          prob_max = copy.copy(prob)
          prob_max_pt = copy.copy(prob_pt)
          
      if (self.inBounds(prob_max_pt)):
          # Make this new head
          # markov[prob_max_pt[0], prob_max_pt[1]] = 100
          new_head = copy.copy(prob_max_pt)

      
      # If eating -- add Tail 
      if snake.getEating(): 
        tail = body[-1]
        body.append(tail)

      # Reduce body length by one
      body.pop(-1)
      
      # Add new head
      new_body = copy.copy(body)
      
      new_body.insert(0, new_head)
      # Update body
      return new_body


    def updateMarkov_step(self, target:snake, snakes:dict, foods:list, turn=1): 

        # Output probability path for target.  Update markov 
        directionSides = {
          'up':[[-1,0],[0,1],[0,-1]],
          'down':[[1,0],[0,1],[0,-1]],
          'left':[[0,-1],[1,0],[-1,0]],
          'right':[[0,1],[1,0],[-1,0]],
          'none':[[0,1],[0,-1],[1,0],[-1,0]]

        }
        w = self.width
        h = self.height
            
        # Target snake
        markov = target.getMarkov(turn)
        body_dict = target.getFuture(turn)
        
        # No body (too far in future)
        body = body_dict['body']
        if (not len(body)):
            # Set blank markov 
            markov = np.zeros([w, h], np.intc)
            target.setMarkov(markov, turn)
            return 

        # Head 
        head = body[0]
        # Tail 
        tail = body[-1]

        # Direciton  & Eating      
        eating = False
        if(len(body) >= 2):
          a = body[0]
          b = body[1]
          dirn = fn.translateDirection(b, a)

          if (body[-1] == body[-2]):
            eating = True 

        else:
          # Direction uncertain
          dirn = 'none'
          # Eating uncertain
          pass 

        # Update probabiliy by direction
        sides = directionSides[dirn] 
        i = 0
        for side in sides: 
          
          prob_pt = list(map(add, head, side))
          if (bo.inBounds(prob_pt)):
            if(dirn == 'none'):
              markov[prob_pt[0], prob_pt[1]] = 25           
            else:
              if i == 0:
                markov[prob_pt[0], prob_pt[1]] = 50 
              else: 
                markov[prob_pt[0], prob_pt[1]] = 25 
         
          i = i + 1

        # # Introduce logic based on other snakes  
        # for sn in snakes: 
        #   # Get heads .. 
        #   pass 

        # # Introduce logic based on food  
        # for fo in foods:
        #   # Get
        #   pass  

        target.setMarkov(markov, turn)


    def updateTrails_stub(self, snakes):
        
        w = self.width
        h = self.height
        trails = np.zeros([w, h], np.intc)

        for body in snakes:

            l = len(body)
            # Mark each point
            for pt in body:
                trails[pt[0], pt[1]] = l
                # Descending from head = N to tail = 1
                l = l - 1

        self.trails = copy.copy(trails)
        return trails


bo = board()



# sn_body.insert(0, sn_head)
# enemy_body.insert(0, enemy_head)
us = snake()
us2 = snake()
them = snake()
us.setHead([3,3])
us.setBody([[3,2], [3,1], [3,0], [2,0]])
us2.setHead([2,2])
us2.setBody([[2,1], [2,0], [1,0], [0,0]])
them.setHead([7,7])
them.setBody([[7,6], [7,5]])
sn_body = us.getBody()
enemy_body = them.getBody()
us.setId('ourSnek')
us2.setId('ourSnek2')
them.setId('enemySnek')
allSnakes = {
  'ourSnek1':us,
  'ourSnek2':us2,
  'enemySnek':them
}
them.setBody([[7,6], [7,5]])

  # for sndata in snakes: 
  # sn = snakes[sndata]

foods = [[2,2]]

# us.setFuture([[3,2], [3,1]])
# body = us.getFuture(0)
# print(body)


tr = bo.updateTrails_stub([sn_body, enemy_body])
ma = bo.updateMarkov(us, allSnakes, foods)

# print(tr)
# print(ma)

for t in range(0, CONST.lookAhead):
  print(ma[t])
  
  for snid in allSnakes:
      sn = allSnakes[snid]
      mk = sn.getMarkov(t)
      