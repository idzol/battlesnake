
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

from boardClass import board
from snakeClass import snake

class snakeTest(snake):

    pass 

global perf

perf = {}
perf['pathProbability_markov_step'] = 0
perf['pathProbability_markov'] = 0
perf['predictMove_step'] = 0
perf['updateMarkov_step'] = 0

class boardTest(board):

    def updateMarkov(self, us, snakes:dict, foods:list, turns=CONST.lookAheadPath): 
      # TODO: Assumes no solids, otherwise requires a version of route with gradient = 1..
      w = self.width
      h = self.height
      markovs = []

      turns = min(turns, CONST.lookAheadPath)
      for t in range(0, turns):
        
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
            # print("SNAKE MARKOV BASE", sn.getId(), t)# print(markov)

            sn.setMarkov(copy.copy(markov), t)
            sn.setMarkovBase(copy.copy(markov), t)
            # Update markov probability 
            self.updateMarkov_step(sn, copy.deepcopy(snakes), foods, t)

            # snakes_updated.append(sn)
            snakes[sid] = copy.deepcopy(sn)

        # TODO: Calculate second iteration of probability, based on first round of markov models
        # for sn in snakes:
        #     self.updateMarkov_step(sn, snakes, foods, t)
            
      
      # Sum all snakes into final markov matrix
      for sn in snakes:
        for t in range(0, turns - 1): 

          markov = np.zeros([w, h], np.intc)
          for snid in snakes:
              sn = snakes[snid]
              # markov_sn = sn[identity].getMarkov()
              # TODO: If snake -1 length but eating .. 
              if sn.getLength() < us.getLength():
                markov_sn = sn.getMarkovBase(t)
              else:
                markov_sn = sn.getMarkov(t)
                  
              markov = markov + markov_sn

          self.markovs[t] = copy.copy(markov)
      
      # self.markovs = copy.copy(markovs)     


    def updateMarkov_step(self, target, snakes:dict, foods:list, turn=1): 

        global perf
        perf['updateMarkov_step'] += 1
        # Output probability path for target.  Update markov 

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
        if(len(body) >= 3):
          a = body[0]
          b = body[1]
          if (a == b):
              # TODO: work out where duplicate coming from.. 
              # ie. [[9, 8], [9, 8], [10, 8] ... ]
              b = body[2]
          
          dirn = fn.translateDirection(b, a)
          # print(target.getName(), a, b, body, dirn)
          if (body[-1] == body[-2]):
            eating = True 

        else:
          # Direction uncertain
          dirn = 'none'
          # Eating uncertain
          pass 

        # Update probabiliy by direction
        if(target.getType() == 'us'):
            # No prediction logic rqd for us  
            pass
        else: 
            # Enemy snake 
            # Recursive function until probability < X 
            markov = self.pathProbability_markov(head, turn)
            
            # Rewrite body over markov
            sn_dict = target.getFuture(turn)
            sn_body = sn_dict['body']

            for cell in sn_body: 
                if(self.inBounds(cell)):
                  # Paint markov matrix for turn t + 1
                  y = cell[0]
                  x = cell[1]
                  markov[y, x] = 100
                
        # # TODO:  Introduce logic based on other snakes  
        # for sn in snakes: 
        #   # Get heads .. 
        #   pass 

        # # TODO:  Introduce logic based on food  
        # for fo in foods:
        #   # Get
        #   pass  

        target.setMarkov(markov, turn)


    def predictMove_step(self, target, foods, turn=0):
        # Based on markov for one snake, calculate most likely path -- eg. food, killcut, other
        # TODO:  Special logic for our snake (known path)
        
        # Get current body 
        global perf
        perf['predictMove_step'] += 1


        turn = min(turn, CONST.lookAheadPath - 1)

        snake = copy.copy(target)      
        sn_future = snake.getFuture(turn)
              
        body = sn_future['body']
        if (not (len(body))):
          return body
        
        # # Get current markov 
        markov = snake.getMarkov(turn)
                  
        # # Select path based on probability (start with highest)
        new_head = []
        if(snake.getType() == 'us'):
            # Special logic for us - we know the way 
            route = snake.getRoute()
            if (turn < len(route)):
              new_head = route[turn]
            else:
              new_head = []
              pass

        else:  
            # Enemy snake             
            probs = np.nonzero((markov < 100) & (markov > 0))
            prob_max = 0
            prob_max_pt = []

            for i in range(0, len(probs[0] - 1)):
              prob_pt = [probs[0][i], probs[1][i]]
              prob = markov[prob_pt[0], prob_pt[1]]
              
              if prob == 100:
              # if prob > prob_max:
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
        # if (len(new_head)):
        #     new_body.insert(0, new_head)

        # Update body
        return new_body


    def pathProbability_markov(self, head, depth=CONST.lookAheadEnemy):
        # Calculates the probability assuming random walk from any location on the board (head), given obstacles (trails)
        # Returns probablility board (chance) from 0 - 100 (%)
        global perf
        perf['pathProbability_markov'] += 1


        w = self.width
        h = self.height
        chance = np.zeros([w, h], np.intc)
        
        enclosed = self.enclosedSpacev2(head)
        dirn_avail = dict(filter(lambda elem: elem[1] > 0, enclosed.items()))

        # Calculate random walk probabiliy of each square
        for dirn in dirn_avail:
            path = [copy.copy(head)]
            prob = 100 / len(dirn_avail)
            turn = 1
            step = list(map(add, head, CONST.directionMap[dirn]))
            self.pathProbability_markov_step(chance, path, prob, step, turn, depth)

        # dirn_avail.remove(dirn)
        # print(str(dirn_avail))

        return chance

    def pathProbability_markov_step(self, chance, path, prob, step, turn=1, depth=CONST.lookAheadEnemy):

        global perf
        perf['pathProbability_markov_step'] += 1

        # Exit if path exceeds depth limit 
        if (len(path) > depth): 
          return chance 
        
        dy = int(step[0])
        dx = int(step[1])
        s = self.trails

        # Check if not blocked
        if (turn >= s[dy, dx]):

            # Add to enclosure
            chance[dy, dx] = chance[dy, dx] + copy.copy(prob)
            dirn_avail = self.findEmptySpace(path, step, turn + 1)
            path_new = copy.copy(path)
            path_new.append(step)
        
            # print("PATH PROB", str(turn), str(step), str(dirn_avail))

            for d in dirn_avail:

                dnext = list(map(add, step, CONST.directionMap[d]))
                # dny = dnext[0]
                # dnx = dnext[1]

                # Reduces based on # directions
                prob_new = prob * 1 / len(dirn_avail)

                # If point is in map & prob > threshold to prevent loop
                if (self.inBounds(dnext) and prob_new > CONST.minProbability):
                    # Recursive
                    turn = turn + 1

                    # print("PATH PROB STEP", str(path), str(prob), str(dnext), str(turn))
                    chance = self.pathProbability_markov_step(chance, path_new, prob_new, dnext, turn, depth)

        else:
            pass

        return chance



data = {'game': {'id': '609d47ca-e773-49f9-b3f4-2c52afa4a05c', 'ruleset': {'name': 'solo', 'version': 'v1.0.22', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'royale': {'shrinkEveryNTurns': 0}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'timeout': 500, 'source': ''}, 'turn': 4, 'board': {'height': 11, 'width': 11, 'snakes': [], 'food': [], 'hazards': []}, 'you': {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}}

# Snakes -- {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}
# Food -- {'x': 2, 'y': 6}, {'x': 5, 'y': 5}

us = snakeTest()
us2 = snakeTest()
them = snakeTest()

us.setHead([3,3])
us.setBody([[3,2], [3,1], [3,0], [2,0]])
us2.setHead([6,2])
us2.setBody([[6,1], [6,0], [5,0], [4,0]])
them.setHead([7,7])
them.setBody([[7,6], [7,5]])

sn_body = us.getBody()
enemy_body = them.getBody()

us.setType('us')
us.setId('ourSnek')
us2.setId('enemySnek1')
them.setId('enemySnek2')
them.setBody([[7,6], [7,5]])

allSnakes = {
  'ourSnek1':us,
  'enemySnek1':us2,
  'enemySnek2':them
}

foods = [[2,2]]

bo = boardTest()

CONST.minProbability = 1

bo.setStartTime()

log('time', '== Start Update ==', bo.getStartTime())
bo.updateBoards(data, us, allSnakes, foods) 
log('time', '== Update Chance==', bo.getStartTime())
bo.updateChance(allSnakes, foods)
log('time', '== Update Markov ==', bo.getStartTime())
bo.updateMarkov(us, allSnakes, foods)
log('time', '== Finish Markov ==', bo.getStartTime())

ma = copy.copy(bo.markovs)

for t in range(0, CONST.lookAheadPath):
  # print("BOARD MARKOV", t)
  # print(ma[t])  
  for snid in allSnakes:
      sn = allSnakes[snid]

      mk = sn.getMarkov(t)
      mkb = sn.getMarkovBase(t)

      # print("SNAKE MARKOV", sn.getId(), t)
      # print(mk)

print(perf)