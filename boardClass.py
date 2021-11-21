# Search for failed games & include as test cases 
# https://console.cloud.google.com/logs/query 
# resource.type="cloud_run_revision"
# resource.labels.service_name="battlesnake1"
# 8c202d0a-e493-4f3a-acc0-26b875d83c03
# 66
# v1.0.22


from typing import List, Dict

import math
import operator
from operator import add

import random as rand

# from matplotlib.pyplot import xcorr
import numpy as np
# import pandas as pd
# import random as rand
import copy as copy
import time as time

# from werkzeug.datastructures import T 

from logClass import log

import constants as CONST
import functions as fn

import sys

# Set recursion limit
# TODO: Replace with loop if possible ..
sys.setrecursionlimit(50000)


class board():

    ## == INIT ==
    legend = CONST.legend  # Import map values

    def __init__(self, logger=log(), height=0, width=0):

        self.logger = logger

        self.height = height
        self.width = width
        self.identity = "" 
        
        self.closest = {}

        self.best = {}
        self.bestLength = {} # np.zeros((height, width), np.intc)
        self.bestWeight = {} # np.zeros((height, width), np.intc)
        self.routepoint = {}

        # self.dijkstra = [None] * CONST.lookAheadPathContinue
        self.markovs = [None] * CONST.lookAheadPathContinue

        self.foods = []
        self.hazards = []
        self.constrains = []

        self.turn = 0

        self.resetCounters()
    

    def setTimeouts(self, t):

        self.timeStart = 0.4 * t 
        self.timeMid = 0.6 * t
        self.timeEnd = 0.8 * t


    def setLogger(self, l):
        """
        Used for global reporting  
        ===
        l:  logClass import log
        """
        # Reference 
        self.logger = l

    def resetCounters(self):
        """
        DEPRECATE 
        Resets timers for recursion & timers   
        """
        self.recursion_route = 0
        self.hurry = False
        # self.gradients = {}


    # def resetRouting(self):
    #     # Reset start of each turn 
    #     h = self.height
    #     w = self.width 

    #     markovs = []
    #     dijkstra = []
        
    #     depth = CONST.lookAheadPathContinue
    #     for t in range(0, depth):
    #         dijkstra.append(np.zeros([h, w], np.intc))
    #         # Enemy prediction 
    #         markovs.append(np.zeros([h, w], np.intc))

    #     self.markovs = copy.copy(markovs)
    #     self.dijkstra = copy.copy(dijkstra)


# == GETTER / SETTER ==

    def setDimensions(self, x:int, y:int):
        """
        Board dimensions 
        ===
        x:  width
        y:  height 
        """
        if isinstance(x, int) and isinstance(y, int):
            self.width = x
            self.height = y
            # self.land = np.zeros((x, y), np.intc)
            return True

        else:
            return False

    def getDimensions(self):
        """
        Board dimensions 
        ===
        (width:int, height:int) 
        """
        return [self.width, self.height]

    def getWidth(self): 
        return self.width

    def setIdentity(self, i):
        self.identity = i

    def getIdentity(self):
        i = self.identity
        return i

    def getHeight(self):
        return self.height

    # def setPoint(self, p: Dict[str, int], t="array"):
    #     try:
    #         if (t == "dict"):
    #             self.land[p["x"], p["y"]] = 1
    #             return True

    #         elif (t == "array"):
    #             self.land[p] = 1
    #             return True

    #     except:
    #         return False

    # def getPoint(self, x, y):
    #     return self.land[x, y]

    # def getYou(self):
    #     return copy.copy(self.you)

    # def getSolid(self):
    #     return copy.copy(self.solid)

    def getCombine(self):
        return self.combine

    # def getThreat(self):
    #     return copy.copy(self.threat)

    # def getSnakes(self):
    #     return copy.copy(self.snakes)

    # def getItems(self):
    #     return copy.copy(self.items)

    # def getDijkstra(self):
    #     return copy.copy(self.dijkstra)

    # def setDijkstra(self, d):
    #     self.dijkstra = copy.copy(d)

    # # Return future predict matrix
    # def getPredictMatrix(self, t):
    #     return self.predict[t]

    def getTurn(self):
        t = self.turn
        return copy.copy(t)

    def setTurn(self, t):
        self.turn = t


# == BOARDS ==

    def updateBoards(self, data:dict, us, snakes:list, foods:list, hazards:list):
        """
        Update boards 
        ===
        data
        us
        snakes
        foods
        ===
        none 

        self.setDimensions -- set board width, heigth
        self.setTurn -- set game turn 
        self.combine -- all layers (snakes, walls, items) used for map
        self.trails  -- snake body by length 
        self.markovs -- initialise for future probability boards 
        self.hazards -- hazard tiles
        """

        # Enclosed - xx
        # Solid - xx
        # Combine - 

        # Snake Head
        hy = data['you']['head']['y']
        hx = data['you']['head']['x']
        # head = [hy, hx]

        # Update game parameters
        width = int(data['board']['width'])
        height = int(data['board']['height'])
        self.setDimensions(width, height)
        self.setTurn(data['turn'])
        
        # Combine board 
        self.updateCombine(us, snakes, foods, hazards)
        
        # Snake trail board
        self.updateTrails(snakes)

        # Constraint board 
        self.updateConstrains()

        # Eating boards 
        self.boards = {}

        # Hazard & foods  
        self.hazards = hazards  
        self.foods = foods 
        
        # Meta boards
        depth = CONST.lookAheadPathContinue
        
        # Chance boards
        self.updateChance(snakes, foods)

        # Routing Boards - init (blank)
        markovs = []
        for t in range(0, depth):
            markovs.append(np.zeros([height, width], np.intc))
            
        self.markovs = markovs
            
        self.updateMarkov(us, snakes, foods, hazards)
        

    def updateConstrains(self): 
        """
        Any paths with two or less paths 
        === 
        self.constrains
        """

        w = self.width
        h = self.height
        constrains =[] 
        for y in range(0, h):
            for x in range(0, w):
                paths = 0

                # Down: y - 1, x 
                # Up: y + 1, x
                # Left: y, x - 1
                # Right: y, x + 1 
                t = self.trails 

                # Down
                if (y - 1) >= 0:
                    if not t[(y - 1), x]:
                        paths += 1

                # Up
                if (y + 1) < h:
                    if not t[(y + 1), x]:
                        paths += 1

                # Left 
                if (x + 1) < w :
                    if not t[y, x + 1]:
                        paths += 1

                # Left 
                if (x - 1) >= 0:
                    if not t[y, x - 1]:
                        paths += 1

            # Add to list 
            if (paths <= 2): 
                constrains.append([y, x])

        # Save list 
        # print ("DEBUG", constrains)
        self.constrains = constrains 


    def updateCombine(self, us, snakes:list, foods:list, hazards:list):     
        """
        Print snakes, food onto board for visualisation  
        TODO: Print hazards as well 
        ===
        us:         Our snake   (20,21..)
        snakes:     All snakes  (30,31..)
        foods:      Food        (-10,..)
        hazards:  Hazards     (-20,..)
        ===
        return none
        updates self.solid 
        """
        w = self.width
        h = self.height

        # HAZARDS 
        mapboard = np.zeros((h, w), np.intc)
        for hd in hazards:
            px = hd[1]
            py = hd[0]
            # self.items[h-py-1, px] = self.legend['hazard']
            mapboard[py, px] = self.legend['hazard']

        # SNAKES 
        for skid in snakes:

            sk = snakes[skid]
            if sk.getType() != 'us':
                # print (str(sk))
                body = sk.getBody()
                for pt in body:
                    px = pt[1]
                    py = pt[0]

                    mapboard[py, px] = CONST.legend['enemy-body']

                try:
                    head = sk.getHead()
                    px = head[1]
                    py = head[0]
                    # self.snakes[h-py-1, px] = self.legend['enemy-head']
                    mapboard[py, px] = CONST.legend['enemy-head']

                except Exception as e:
                    self.logger.error('exception', 'updateBoardSnakes', str(e))

        # YOU 

        body = us.getBody()
        for pt in body:
            px = pt[1]
            py = pt[0]
            mapboard[py, px] = CONST.legend['you-body']

        try:
            head = us.getHead()
            px_head = head[1]
            py_head = head[0]
            mapboard[py_head, px_head] = CONST.legend['you-head']

        except Exception as e:
            self.logger.error('exception', 'updateBoardsYou',
                'INFO: Your snake head not defined. ' + str(e))

        # ITEMS 
        for fd in foods:

            px = fd[1]
            py = fd[0]
            # self.items[h-py-1, px] = self.legend['food']
            mapboard[py, px] = self.legend['food']

        # Update boards 
        # self.you = copy.copy(youboard)
        # self.snakes = copy.copy(snakeboard)
        # self.items = copy.copy(itemboard)
        # self.solid = rs * np.ceil(youboard / (youboard + 1) + snakeboard / (snakeboard + 1))
        
        self.combine = mapboard


    def updateDistance(self, data):

        w = self.width
        h = self.height
        self.distance = np.zeros((h, w), np.intc)

        # Distances from snake head
        head = fn.XYtoLoc(data['you']['head'])

        for i in range(0, w):
            for j in range(0, h):
                d = fn.distanceToPoint(head, [j, i])
                self.distance[i, j] = d


    def updateChance(self, snakes, foods):

        # 
        turns = CONST.lookAheadEnemy
        # us = self.getIdentity()

        for snid in snakes:
          snake = snakes[snid]
          
          if (snake.getType() != "us"):
            # Update snake chance boards
            chance = self.pathProbability(snake, turns)
            

    def updateCell(self, cell:list, weight:int, turn:int=0, replace=True):
        """
        Update markov cell 
        ===
        cell:   route point to update (eg. [6,2]) 
        weight: weight to set point (eg. CONST.routeSolid)
        turn:   future turn (0 to CONST.lookAheadPathContinue - 1)
        === 
        return none 
        updates self.markovs 
        """
        t = min(turn, CONST.lookAheadPathContinue - 1)
        if(self.inBounds(cell)):
            # Paint markov matrix for turn t + 1
            y = cell[0]
            x = cell[1]
            if(replace):
                self.markovs[t][y, x] = weight
            else:            
                self.markovs[t][y, x] += weight

    def updateBoardsEnemyMoves(self, snakes:list): 
        """
        Update markov boards with future path of each snake (except us)
        ===
        snakes:     list of snakes 
        === 
        none 

        updates 
        self.markovs
        """

        uid = self.identity
        us = snakes[uid]
        length_us = us.getLength()

        for sid in snakes:
            sn = snakes[sid]
            if sn.getType != "us": 
                moves = sn.getRoute()
                length = sn.getLength()
                # DEBUG:  print(moves)
                n = 0

                # Predict up to snake length moves 
                # decrease certainty after 2*length? 
                for m in range(0, CONST.lookAheadPathContinueEnemy):
                    # Get first m steps in route
                    if m > length:
                        n += 1

                    # Fade moves after m > length 
                    steps = moves[n:m+1]
                    # Update markov board (m) for each step 
                    for step in steps:
                        # If snake is smaller, don't make head solid 
                        if length < length_us and step == steps[-1]:
                            pass 

                        else: 
                            # Draw markov board one move in advance ..
                            self.updateCell(step, CONST.routeSolid, m-1)
                            

    # def updateHazard(self, hazards:list): 
    #     """
    #     Add threat to hazard cells 

    #     """
    #     turns = CONST.lookAheadPathContinue
    #     for h in hazards: 
    #         for turn in range(0, turns):
    #             self.updateCell(h, CONST.routeHazard, turn)

    # 
    def increaseHazard(self, turns=CONST.lookAheadPathContinue, foods:list=[], solid=False, multiplier=1):
        turns = min(turns, CONST.lookAheadPathContinue)
        hazards = self.hazards 

        for t in range(0, turns):
            markov = self.markovs[t]
            for hz in hazards: 
                if solid:
                    # Don't set food square to sollid 
                    if hz not in foods: 
                        markov[hz[0], hz[1]] = CONST.routeSolid

                else:
                    # increase threat level 
                    markov[hz[0], hz[1]] = CONST.routeHazard * multiplier
            
            # print("DEBUG HAZARDS", markov)
        
            markov[hz[0], hz[1]] = CONST.routeHazard
            self.markovs[t] = markov


    def updateMarkov(self, us, snakes:dict, foods:list, hazards:list, turns=CONST.lookAheadPathContinue): 
      
      w = self.width
      h = self.height
      # markovs = []

      turns = min(turns, CONST.lookAheadPathContinue)
      for t in range(0, turns):
        
        # Iterate through snakes to get the first step / next step based on probability
        # snakes_updated = []
        for sid in snakes:
            
            sn = snakes[sid]
            # who = sn.getType() 
            # head = sn.getHead()
            # tail = sn.getTail()
            length = sn.getLength()
            markov = np.zeros([w, h], np.intc)
            sn_body = []
            # sn_future = []
              
            # Prediction for first turn
            if (not t):
              # First move -- establish initial markov (t = 0) 
              
              # BUGFIX:  check/  Body already includes head, ie. function was doubleprinting head?
              # sn_body = sn.getHeadBody()
              sn_body = sn.getBody()
              sn.setFuture(sn_body, 0)
              body = sn_body

            else:
              # Predict current move (t) based on last markov (t) 
              # Set future location ) 
              # sn_body = self.predictMove_step(sn, foods, t - 1)
              sn_body = sn.getFuture(t - 1)
              body = sn_body['body']
              if (len(body)):
                body.pop(-1)
              
              sn.setFuture(body, t)
              
            # Update markov probability 
            # =========================
            for b in body: 
                # if(self.inBounds(cell)):
                # Paint markov matrix for turn t + 1
                # y = cell[0]
                # x = cell[1]
                    
                # if who == "us" and cell == head:
                #     # Adjust head to zero for routing
                #     markov[y, x] = 0

                if length > 3 and self.trails[b[0], b[1]] == 1: 
                    # Erase tail unless snake is eating
                    markov[b[0], b[1]] = 1

                else:
                    markov[b[0], b[1]] = CONST.routeSolid


            sn.setMarkovBase(markov, t)
            # Set markov + chance
            if (not len(body)):
                # Set blank markov 
                # markov = np.zeros([w, h], np.intc)
                sn.setMarkov(markov, t)

            else: 
                
                # Update probabiliy by direction
                if(sn.getType() == 'us'):
                    # No prediction logic rqd for us  
                    pass

                else: 
                    # Draw markov   
                    chance = sn.getChance(t)
                    if chance is not None:
                        markov = markov + chance 

                sn.setMarkov(markov, t)
            
            # ===================
            # snakes[sid] = copy.deepcopy(sn)

        # TODO: Calculate second iteration of probability, based on first round of markov models
        # for sn in snakes:
        #     self.updateMarkov_step(sn, snakes, foods, t)


      # Sum all snakes into final markov matrix
      for sn in snakes:
        for t in range(0, turns - 1): 

          markov = np.zeros([w, h], np.intc)
          for hz in hazards: 
              if hz not in foods:
                markov[hz[0], hz[1]] = CONST.routeHazard
          
          for snid in snakes:
              sn = snakes[snid]
              # markov_sn = sn[identity].getMarkov()
              
              # if t >= CONST.lookAheadEnemy:
              if sn.getLength() < us.getLength() or t >= CONST.lookAheadEnemy:
                # Remove threat from smaller snakes, or after N turns (because snake threat unknown)
                markov_sn = sn.getMarkovBase(t)
              else:
                markov_sn = sn.getMarkov(t)
                  
              markov = markov + markov_sn 

          # print("LENGTH", len(self.markovs), t)
          self.markovs[t] = markov
          # self.markovbase[t] = copy.copy(markov)
      
    
    def clearBest(self):
        """
        Clear routing boards.  Set self.best to none
        ==  
        none
        == 
        returns none 
        """
        self.best = {}
        self.bestWeight = {}
        self.bestLength = {}


    def updateBest(self, start:list, start_path:list=[], turn=0, snakes:list=[], foods:list=[], eating_start={}, performance=True, rr_max=CONST.lookAheadPathContinue):
        """
        Calculate paths from start to any point on the board 
        ==  
        start:      starting point, eg. [7, 3]
        == 
        none 

        updates arrays for str(start) 
        self.best           # path to each point (dict, np array, dict)
        self.bestLength     # length to each point (dict, np array)
        self.bestWeight     # weight to each point (dict, np array)
        """
        
        w = self.width 
        h = self.height
        # Find path to all points on the board by length, weight 
        
        perf = 0
        dot_weight = 0
        save = start + []   # copy.copy

        # print("SAVE TO", save)]
        
        # Start path includes head which is not a turn, hence len(start_path) - 1
        dot_alpha = {'loc':start, 'weight':0, 'length':max(0, turn), \
                    'path':[], 'food':[], 'hazard':[], \
                    'directions':CONST.directions, 'from':''}
        
        # Recursive dots 
        dots = []
        dots.append(dot_alpha)
        # Final board
        best = {}
        best[str(start)] = dot_alpha
        best_length = np.zeros([h,w], np.intc)
        best_weight = np.zeros([h,w], np.intc)

        # Complexity - O(4wh)
        rr = 0
        # rr_max = CONST.lookAheadPathContinue    #  w + h  

        # while(len(dots)):
        while(len(dots) or rr < rr_max):
            
            dots_next = []
            # Each dot recurses into adjacent cells 
            # print("NEXT", rr, dots)
            for dot in dots:
                
                # alive = False    
                for dirn in dot['directions']:

                    # if dot['loc'] == [4, 6]:
                    #     print("DEBUG DOR DIRN", dirn)

                    alive = False 
                    dot_hazard = dot['hazard'] + []
                    dot_food = dot['food'] + []
                    # dot_constrain = dot['constrain'] + [] 
                
                    if dot['from'] == dirn:
                        # Skip direction we came from 
                        continue 

                    # Check next swap 
                    dot_loc = list(map(add, dot['loc'], CONST.directionMap[dirn]))
                    # dot_loc = copy.copy(step)
                    
                    dot_path = dot['path'] + []     # copy.copy

                    # Check in bounds 
                    if self.inBounds(dot_loc):

                        dot_length = dot['length'] + 0
                        t = min(dot_length, CONST.lookAheadPathContinue - 2) 
                        dot_weight = dot['weight'] + self.markovs[t+1][dot_loc[0]][dot_loc[1]]
                        
                        # Check if edge - don't route along walls, save for escapes
                        # if not self.isEdge(step):
                        # Check if food is in past moves
                        if dot_loc in self.foods:
                            dot_food.append(dot_length + 1)
                        
                        eating = {}
                        foods_eaten = len(dot_food)
                        for sid in snakes:
                            if snakes[sid].getType() == 'us': 
                                if sid in eating_start:
                                    eating[sid] = eating_start[sid] + foods_eaten
                                else:
                                    eating[sid] = foods_eaten

                            else:
                                # Todo: enemy eating 
                                # Enemy eating in next N turns 
                                if turn >= 1:  
                                    eating[sid] = snakes[sid].getEatingFuture()
                                    
                                # print(sid, eating[sid])
                            
                        # Check we can route 
                        exists = False 
                            
                        # if performance:
                            # if dot_length >= self.trails[dot_loc[0], dot_loc[1]]:
                            #     exists = True
                        # if not performance: 
                        
                        if self.isRoutePointv2(dot_loc, turn=dot_length, eating=eating , path=dot_path + start_path):
                            # if dot_loc in [[5, 3]]: 
                            #     print("BEST", dot_loc, dot_length, dot_path)  # eating, 
                        
                            dot_length += 1
                            exists = True 

                        if exists:  # Check if path exists                        
                            # Save turn of food 

                                
                            # Save turn of hazard
                            if dot_loc in self.hazards:
                                dot_hazard.append(dot_length)
                                
                            # Save location of constraint
                            # if dot_loc in self.constrains:
                            #     dot_constrain.append(dot_loc)
                            #     # FIX:  Temporary until we can work out checkConstrain 
                            #     dot_weight += CONST.routeConstrain
                                
                            if not str(dot_loc) in best: 
                                # print("NEW", dot_loc, best)
                                alive = True 

                                # Check if better path 
                            else: 
                                dot_omega = best[str(dot_loc)]
                                # print("DEBUG HAZARD", len(dot_hazard), len(dot_omega['hazard']))
                                
                                if (dot_length < dot_omega['length'] or
                                        (dot_length == dot_omega['length'] and
                                        dot_weight < dot_omega['weight']) or 
                                        (dot_length == dot_omega['length'] and 
                                        len(dot_hazard) < len(dot_omega['hazard']))):

                                    alive = True
          
                    else:
                        # Kill dot 
                        pass 

                    # DEBUG 
                    # if (alive and dot_loc in [[9, 9], [8, 9], [7, 9], [6, 9], [5, 9], [4, 9], [3, 9], [2, 9], [1, 9], [0, 9], [0, 8], [0, 7], [0, 6], [0, 5], [0, 4], [0, 3], [0, 2], [0, 1], [0, 0], [1, 0]]   ): 
                    #     print("DEBUG DOT LOC ", alive, eating, dot_loc, dot_weight) # , dot_path, t, self.markovs[t][dot_loc[0]][dot_loc[1]]) 
                    #     print("DEBUG MARKOV", self.markovs[t+1][dot_loc[0]][dot_loc[1]], t+1)
                    #     # dot_food

                    if alive: 

                        dot_path.append(dot_loc)
                        # Create another dot (recursive)
                        dot_new = {'loc':dot_loc, 
                            'weight':dot_weight,
                            'length':dot_length, 
                            'path':dot_path,
                            'food':dot_food,
                            'hazard':dot_hazard,
                            'directions':CONST.directionRotation[dirn],
                            'from':CONST.directionOpposite[dirn]
                            }


                        dots_next.append(dot_new)
                        # Save new best path 
                        best[str(dot_loc)] = dot_new
                        best_length[dot_loc[0], dot_loc[1]] = dot_length
                        best_weight[dot_loc[0], dot_loc[1]] = dot_weight
                
                    perf += 1

                dots = dots_next

            # print("LAST", rr)
            rr += 1

        # Save board - optimisation        
        self.best[str(save)] = best         
        self.bestLength[str(save)] = best_length
        self.bestWeight[str(save)] = best_weight
       
        return perf


    def checkConstrain(self, route, snakes):
        """
        Check route to determine if enemy can get to constrain point before us 
        Return True if enemy cannot constrain 
        """
        # turn = 0 
        # alive = True 


        # # init constricts 
        # constricts = {} 

        # # Update each route point 
        # constricts[turn] = dot_loc

        # constricts = route['constricts']
        # path  = route['path']

        # first = ''
        # last = ''

        # for t in turns:
        # c = constricts[t]

        # # Calculate actual distance to all enemy snake heads 
        # # Very expensive -- just do for first & last constrict point 
        # if not(first):  
        #     start = path[-1]
        #     path = dot_path[] 
        #     best = updateBest[c, turn]
        #     first = c 
        # # go through enemy heads 
        #     for head in heads
        #     if (len(best[start][head) 

        # last = c 


        # if last != first: 
        #     path = dot_path[] 
        #     self.updateBest[c, turn]
        #     first = c 


        # for fn.distToPoint(c, enemy 

   # check if enemy can get to t before 

        # heads = []
        # for sid in snakes:
        #     fsnake = snakes[sid]
        #     ftype = fsnake.getType()   
        #     if (ftype == 'enemy'):
        #         fhead = fsnake.getHead()
        #         heads.append(fhead)
                
        #     # Look for each location 
        #     control_max = 0
        #     for d in CONST.directions: 
        #         # maximise board control - stepwise max 
        #         step = list(map(add, start, CONST.directionMap[d]))
        #         if (bo.inBounds(step) and bo.isRoutePointv2(step, 0)):
        #         # Return board control matrix 
        #         dist = bo.closestDist(step, heads)

        # for step in route: 
        #     print("DEBUG CONSTRAIN", step['constrain'])

        return False  



    
    def checkHealth(self, snake, route):
        """
        Check route to determine if enough health to survive
        Returns True if health never drops below zero 
        ===
        snake:
        route:
        ===
        return alive   
        """

        health = snake.getHealth()
        length = snake.getLength()
        
        alive = True 
        # print("DEBUG HEALTH", health, route)
        # print ("DEBUG CHECK HEALTH", route)
        
        # for turn in range(1, # route['length'] + 1):
        # print(route['path'])

        # only look ahead N moves becaues random padding doesn't accommodate for threat (ie. all long routes look bad)
        # usually danger in next 10 moves .. 
        for turn in range(1, 10):
            health -= 1
            # print(health)
            if turn in route['hazard']:
                health -= 15
            if turn in route['food']:
                health = 100  
            
            if health <= 0:
                alive = False 
            
            # print("HEALTH", health, turn)
            
        return alive 


    def updateGradient(self, a, turn=0):

        return 
        # == DEPRECATE == 
         
        # Max threshold
        rtmax = CONST.routeThreshold
        h = self.height
        w = self.width

        if (not self.recursion_route):
            # Initialise gradient -- MOVED TO SERVER.PY
            self.gradient = np.full([h, w], CONST.routeThreshold)
            self.gradient[a[0], a[1]] = 0

        # Max number of turns / boards in prediction matrix
        tmax = CONST.lookAheadPath - 1
        if (turn > tmax):
            turn = tmax

        dijkstra = self.getDijkstra()
        dt = dijkstra[turn]

        # Exit if timer or recursion exceeded
        rr = self.recursion_route
        self.recursion_route = rr + 1

        if (self.hurry):
            return


        if (rr > 0 and not (rr % 100)):
            
            # Timer exceeded
            st = self.logger.getStartTime()
            diff = 1000 * (time.time() - st)
            if diff > CONST.timeStart:
                self.logger.message('timer-hurry')
                self.logger.log('performance', 'updateGradient - timeStart exceeded')
                self.hurry = True

            if rr > CONST.maxRecursion:
                self.logger.log('performance', 'updateGradient - max recursion reached')
                self.hurry = True
                
            # Log every N iterations 
            if not (rr % 1000):
                self.logger.timer('Gradient 1000')
                self.logger.message('timer-hurry')
                # self.hurry = True

            
        # Iterate through four directions
        for d in CONST.directions:

            a1 = list(map(add, a, CONST.directionMap[d]))

            # Check in bounds
            if (self.inBounds(a1)):

                g0 = self.gradient[a[0], a[1]]
                g1 = self.gradient[a1[0], a1[1]]
                d1 = max(dt[a1[0], a1[1]], 0)

                # Check path is less than route threshold and cheaper than last

                # If target is solid, always solid ..
                # if route_solid()
                if ((d1 < rtmax) and (g0 + d1) < g1):

                    # Update point
                    self.gradient[a1[0], a1[1]] = g0 + d1

                    # Recursion.  Check which prediction matrix to use based on number of turns (t)
                    turn = turn + 1
                    self.updateGradient(a1, turn)


    def updateGradientFix(self, a):

        return 

        # == DEPRECATE == 
        # BUGFIX: Prevent snake from "seeing through" themselves in predict matrix in a future turn (eg. loop around & think not there)
        for d in CONST.directions:
            a1 = list(map(add, a, CONST.directionMap[d]))
            if (self.inBounds(a1)):
                self.gradient[a1[0], a1[1]] = self.dijkstra[0][a1[0], a1[1]]


    def updateTrails(self, snakes):
        # TODO: Replace updatePredict with a set of layers
        # updatePredict
        # predict = trails + ...

        w = self.width
        h = self.height
        trails = np.zeros([w, h], np.intc)

        self.trailsSnake = {}
        
        for sid in snakes:    
            snake = np.zeros([w, h], np.intc)
            sn = snakes[sid]
            # BUGFIX:  check/  Body already includes head, ie. function was doubleprinting head?
            # body = sn.getHeadBody()
            body = sn.getBody()
            l = len(body) + 1 

            # If eating tail takes one more turn
            # if sn.getEating():
            #   l = l + 1

            # Mark each point
            pt_last = []
            for pt in body:
                if pt != pt_last:
                    l = l - 1
                trails[pt[0], pt[1]] = l
                snake[pt[0], pt[1]] = l
                # Descending from head = N to tail = 1
                pt_last = pt
                

            # Individual snakes (used for eating)
            self.trailsSnake[sid] = snake

        # All trails 
        self.trails = trails
        

    def pathProbability(self, snake, depth=CONST.lookAheadEnemy):
        """
        Calculates the probability assuming random walk for a snake
         from any location on the board (head), given obstacles (trails)
        ===
        snake:snake     snake object   
        depth:int       number of turns to look ahead 
        ===
        sn.updateChance()       updates probablility board (chance) from 0 - 100 (%)
        """
        
        head = snake.getHead()
        body = snake.getBody()
            
        w = self.width
        h = self.height
            
        rr = 0
        dot = {'step':head, 'path':body, 'prob':CONST.maxProbability, 'turn':rr }
        dots = [dot]

        s = self.trails    

        # Recursive 
        chance = np.zeros([w, h], np.intc)
        while len(dots) and rr < depth:
            
            # Check each point 
            for dot in dots:
                
                alive = False 

                # Chance board updated for each snake 
                dots_next = []

                turn_new = dot['turn'] + 1
                step = dot['step']
                prob = dot['prob']
                path_new = dot['path'] + []
                dirn_last = fn.translateDirection(path_new[1], path_new[0])
                dirn_avail = self.findEmptySpace(step, path_new, turn_new)
                
                for dirn in dirn_avail:
                    # Check 
                    step_new = list(map(add, step, CONST.directionMap[dirn]))
                    same_dirn = list(map(add, path_new[0], CONST.directionMap[dirn_last]))
                    
                    # If in the open and three directions (50:25:25)
                    if len(dirn_avail) == 3:
                        if step_new == same_dirn:
                            prob_new = prob / 2
                        else:
                            prob_new = prob / 4
                    else:
                        # ..Otherwise (50:50, or 100)
                            prob_new = prob / len(dirn_avail)
            
                    # Check if not blocked (simple)
                    dy = step_new[0]
                    dx = step_new[1]
                    
                    
                    if (turn_new >= s[dy, dx]):
                        
                        # Add to enclosure
                        # print(step_new, prob_new)
                        chance[dy, dx] += prob_new
                        path_new.append(step_new)
            
                        # If point is in map & prob > threshold to prevent loop
                        
                        if self.inBounds(step_new):
                            if (turn_new < CONST.lookAheadPathContinueEnemy and prob_new > CONST.minProbability or  
                                turn_new >= CONST.lookAheadPathContinueEnemy and prob_new == CONST.maxProbability):

                                
                                # Recursive
                                alive = True 
                    
                    if (alive):  
                        dot = {
                            'step':step_new,
                            'path':path_new,
                            'prob':prob_new,
                            'turn':turn_new
                        }
                        dots_next.append(dot)
                        
            rr += 1
            dots = dots_next
            snake.setChance(chance, turn_new)
            # print(dots, chance)
               

# == ROUTING ==

# TODO: Fuzzy Routing, ie. get close to an object)

    def fuzzyRoute(self, start, targetmap, snake='', threshold=CONST.routeThreshold):
        # Send shape - return best path to any point in shape
        # a = [1, 1]
        # b = np.zeros([h, w], np.intc)
        # b[1:3, 3:6] = 1
        # result, weight = fuzzyRoute(a, b)
        w = self.width
        h = self.height
        
        route = []
        route_weight = CONST.routeThreshold
 
        a = start
        b = targetmap
        
        r = np.zeros([h, w], np.intc)
        r = r + b
        r[a[0], a[1]] = 1

        targets = np.nonzero(b > 0)
        
        # Iterate through potential targets
        for i in range(0, len(targets[0] - 1)):
            t = [targets[0][i], targets[1][i]]
            try:
                r, w = self.route(a, t, snake)
                # Save best route 
                if w < route_weight:
                    route = r
                    route_weight = w

            except Exception as e:
                self.logger.error('exception', 'fuzzyRoute', str(e))
                pass

        # Remove head from route (if already here)
        if len(route):
            if route[0] == start:
                route.pop(0)

        return route, route_weight


    def route(self, start:list, dest:list, snake='', threshold=CONST.routeThreshold):
        """
        Route from start to dest 
        Route always assumes current turn 
        ===
        start:list
        dest:list
        === 
        return (route, weight)
        """
        # if start != us.getHead()
        #   warning -- ie. best only valid for start 
                    
        path = []
        reason = []
        weight = CONST.routeThreshold

        if start == dest: 
            return [start], 0

        if not str(start) in self.best:
            self.updateBest(start, turn=0)

        if self.inBounds(dest):
            if str(dest) in self.best[str(start)]:
                route = self.best[str(start)][str(dest)]
                path = route['path']
                weight = route['weight']
                if (snake):
                    if not self.checkHealth(snake, route):
                        reason.append("Route found.  Healtcheck failed")
                        weight += 2 * CONST.routeThreshold

        # print("DEBUG ROUTE#2", start, dest, path, route, weight)
        # print("DEBUG ROUTE#2", self.best[str(start)])
        # print("Reasons: %s" % reason)
        
        return path, weight



    def dijkstraPath(self, path, turn=0):
        # Sum dijkstra map between two points
        
        # Check which prediction matrix to use
        tmax = min(turn, CONST.lookAheadPathContinue - 1)

        result = 0

        # Capture largest increment (probability of collision)  
        largest_point = 0
        
        # Iterate through path
        # dt = self.getDijkstra()

        for p in path:
            if self.inBounds(p):

                # Add markov value
                increment = int(self.markovs[tmax][p[0], p[1]])
                result = result + increment
                tmax = tmax + 1
                if (increment > largest_point):
                  largest_point = increment 

        return result, largest_point


    def routePadding(self, route:list, snakes:list, foods:list, depth=CONST.lookAheadPathContinue, method="random"):
        """
        Extend an existing route path by N moves to check whether it is safe
        ===
        route:      Existing route (used to avoid collisions with self) 
        snakes:     All snakes 
        foods:      All food (used to determine eating)
        depth:      Max number of turns padding to search. CONST.lookAheadPathContinue (default)
        method      Padding method.  "weight" (default), "length", "tail", "random"
        ===
        route:     route of padding, [] if not found
        weight:    weight of padding, CONST.Threshold if no path, 0 if no padding (?)
        """

        path = []
        weight = CONST.routeThreshold
        weight_continue = 0 
        routefound = False
        reason = []

        # print("METHOD", method)
        # Needs minimum one point to start padding route
        if (not len(route)):
            return path, weight

        # Convert vectors to points
        #if (len(route) > 1):
        #     print("DEBUG ROUTE BEFORe", route)
        #     path_start = fn.getPointsInRoute(route)
        #     print("DEBUG ROUTE AFTER", path_start)

        # else: 
        path_start = route

        # Confirm we have a path
        if (turn := len(path_start)):

            # Get snake info 
            sid_us = self.getIdentity()
            us = snakes[sid_us]
            head = us.getHead()
            length = us.getLength()

            # BUGFIX:  When route contains start, looks like we are one turn further 
            if head == path_start[0]:
                turn -= 1

            # Get turn based on path (past moves)
            # start = path_start[-1]
            start_random = path_start 
            
            # A) Largest path - using bestPath 
            if method in ['weight', 'length', 'tail', 'rfactor']:
            
                route_best = self.continuePath(path_start, snakes, foods, depth, method)
                
                # Check if any route found 
                if (len(route_best)):     
                    # route_sorted = sorted(route_best, key=lambda d: d['weight'])
                    # Path comes back reversed 
                    weight = route_best['weight']
                    path = path_start + route_best['path']
                    # path = copy.copy(path_padding)                        
                    # routefound = True

                    # Check if route meets min depth
                    if (len(path)) >= depth: 
                        reason.append("Continue Path. Route found")
                        routefound = True 
                        
                    else:
                        # Pad with random 
                        reason.append("Continue Path. Random pad")                  
                        start_random = path

                else:  
                    # Start again .. 
                    reason.append("Continue Path. Route not found")
                    start_random = path_start
                    weight = 0 
                    
                turn = len(start_random)
                weight_continue = weight 
            
                # print("DEBUG PADDING", start_random, path, weight, turn, routefound)
                   
            # B) Find Largest path in random walk 
            if method in 'random' or not routefound:
                
                # depth = min(length, depth)
                depth_random = max(depth, CONST.lookAheadPathRandom)
                eating = self.findEating(snakes, start_random, foods)
                rr, route_best = self.findLargestPathv2(start_random, snakes, turn=turn, eating_start=eating, foods=foods, depth=depth_random)
                
                if (len(route_best)): 
                    path = route_best['path']
                    weight = route_best['weight'] + weight_continue
                    # weight = route_best['weight'] 
                    reason.append("Random. Route found")

                else: 
                    path = start_random


                if (len(path) >= depth_random):  
                    # target = path[-1]
                    # weight = 0 # self.bestWeight[target[0], target[1]]        
                    routefound = True 
                
                else:
                    weight += CONST.routeSolid
                    reason.append("Random. Length not greater than depth_random")

                # print("DEBUG RANDOM", path, weight, len(path), depth)
                    
        # Add weight for any constrained points 
        # Get heads 
        them = []
        for sid in snakes:
            enemy  = snakes[sid]
            if (enemy.getType() == 'enemy'):
                enemy_head = enemy.getHead()
                them.append(enemy_head)

        # print(path)
        # print(self.constrains)
        for pt in path:
            # print(pt)
            if pt in self.constrains:
                weight += CONST.routeConstrain    
                closest = self.closestDist(head, them)
                # print ("ROUTE CLOSEST", closest)
                if not (closest[pt[0], pt[1]]):
                    weight += CONST.routeConstrain # Solid     
            
                            
        if not self.checkHealth(us, route_best):
            weight += 2 * CONST.routeThreshold
            # print(route_best)
            reason.append("Continue Path. Failed health check")

        # if [0, 5] in path:  
        # print("DEBUG ROUTE")
        
        us.setRoute(path)
        # self.showMapsFuture(snakes)
        self.logger.log("Reason:", reason)
        return path, weight


    def isHazard(self, start):
        """
        Check if point is a hazard tile
        """
        if start in self.hazards:
            return True
        else: 
            return False 


    def distanceToSafety(self, start):
        pass 
        # non hazard points  
        # sort by closest  
        # route 

 

    def isRoutePointv2(self, step, turn=0, eating={}, path=[], enemy=False):
        """
        Check if point is a valid route point based on threat (markov) and collision (snakes)
        ===
        step - check route points from start location
        turn - adjust for future turn state 
        eating - adjust for past / future eating 
        path - check past path points for collision
        enemy - ignore markov threat when predicting enemy moves
        ===
        boolean - confirm if valid route point or not
        """

        # Optimise -- return false if already been here 
        # BUGFIX: doesn't account for small snake / circular routes 
        if step in path: 
            return False 

        # routeHash = str(step) + str(turn) + str(eating) + str(path) + str(enemy)
        # if routeHash in self.routepoint:
        #     return self.routepoint[hash]

        w = self.width
        h = self.height

        # Optimisation -- Get step
        # dy = step[0]
        # dx = step[1]

        # Get markov for next turn 
        t = min(turn, CONST.lookAheadPathContinue - 2)
        markov = self.markovs[t+1]
        
        # Optimise -- use previous board 
        routeKey = str(eating) + str(turn)
        if routeKey in self.boards:         
            board = self.boards[routeKey]
            
        else:        
            # Get tails 
            board = np.zeros([w, h], np.intc)
            trails = self.trailsSnake
            for sid in trails:
            # Adjust trails for each snake based on eating
                # print("EATING", eating)
                if sid in eating.keys(): 
                    # Add eating to trail 
                    board += np.where(trails[sid], trails[sid] + eating[sid], trails[sid])  
                    
                else: 
                    board += trails[sid]

            self.boards[routeKey] = board
    
        # DEBUG ..
        # if step == [6, 3]: #  or step == [4, 7]:
        # # if step in [[6, 7], [6, 8]]:
        #     print("DEBUG", turn, step, path)
        #     print("MARKOV", markov[dy, dx])
        #     print("BOARD", board[dy, dx])
            
        # Route logic 

        exists = False 
        if (0 <= step[0] < h):
            if (0 <= step[1] < w):  
                
                # Enemy prediction logic
                if (enemy and turn >= board[step[0], step[1]] - 1):
                    exists = True    
                    
                # Our prediction logic
                elif(turn >= (board[step[0], step[1]] - 1) and 
                        markov[step[0], step[1]] < CONST.routeThreshold):
                    exists = True     
                        
        # self.routepoint[routeHash] = exists
        # if (step in [[0, 9]]): 
        #     print(step, turn, board, eating, path, exists)
            
        return exists 


    def hasEaten(self, snakes, foods):
        # this is taken care of in self.trails 
        pass
        

    def findEating(self, snakes, path, foods):

        eating = {}
        for sid in snakes: 
            # Use provided path for us,  
            # TODO: consistency in function to just use snake.getNextSteps()
            if (snakes[sid].getType() != "us"): 
                # Return every possible path of length N = lookAheadPredictFuture calculated in self.predictEnemyMoves
                # paths = snakes[sid].getNextSteps()
                # food_in_route = 0 
                # try:
                #     food_path = 0  
                #     # Check if food is in future moves 
                #     for path in paths: 
                #         food_path = len(list(filter(lambda x: x in foods, path)))
                #         food_in_route = max(food_in_route, food_path)                 
                #         # print("DEBUG ENEMY PATH", sid, path, food_path)   # lookAheadPredictFuture

                # except:
                #     pass 

                # eating[sid] = food_in_route
                # # print("DEBUG ENEMY FINAL", food_in_route)
                eating[sid] = snakes[sid].getEatingFuture()

            else:
                # Calculate sum of food in path 
                try:
                    # Check if food is in future moves
                    food_in_route = len(list(filter(lambda x: x in foods, path)))
                    eating[sid] = food_in_route
                
                except:
                    eating[sid] = 0


        return eating 


    def continuePath(self, route, snakes, foods=[], depth=CONST.lookAheadPathContinue, method="random"):
   
        w = self.width  

        if not len(route):
            return []
            
        else:
            start = route[-1]
            path = route + []  # copy.copy
                
        # Look for dots that makes it to longest path..
        routes = []
        target = []
    
        # Calculate best paths from target point 
        # OPTIMISE: Use best array within N 
        
        # Pad route by length + 1 to accommodate for not having head 
        turn = len(route)
        
        head = []
        for sid in snakes: 
            if snakes[sid].getType() == 'us':
                head = snakes[sid].getHead()
        if head in route: 
            print("ERROR: UPDATE BEST route should not include head.  Puts turn out by 1. ", head, start, route, turn)

        # Pass in eating from past routes... 
        eating = self.findEating(snakes, route, foods)
        self.updateBest(start, route, turn=turn, snakes=snakes, eating_start=eating, foods=foods, rr_max=depth)
        

        # Find BEST route 
        # 1) longest with no weight 
        if (method == "weight"):
            rfactor = self.bestLength[str(start)]       # copy.copy
            while smax := np.argmax(rfactor):      
                sy = int(smax / w)
                sx = smax % w
                target = [sy, sx]
                if self.bestWeight[str(start)][sy, sx] == 0:
                    break
                else:
                    rfactor[sy, sx] = 0
        
        
        # 2) Weighted rfactor 
        elif (method == "tail"):
            # Get snake info 
            sid_us = self.getIdentity()
            us = snakes[sid_us]
            target = us.getTail()
            sy = target[0]
            sx = target[1]


        # 2) Weighted rfactor 
        elif (method == "rfactor"):
            # R20211104 - changed from 10*len to 10*2^len 
            rfactor = np.round(pow(self.bestLength[str(start)], 3) / (self.bestWeight[str(start)] + 1), 0)
            smax = np.argmax(rfactor)
            sy = int(smax / w)
            sx = smax % w
            target = [sy, sx]


        else:  # method == 'length'
        # 3) Longest length 
            rfactor = self.bestLength[str(start)]
            smax = np.argmax(rfactor)
            sy = int(smax / w)
            sx = smax % w
            target = [sy, sx]

        
        if not len(target):
            return []

        # [8, 7], [9, 7], [10, 7], [10, 6], [10, 5], [9, 5], [8, 5], [7, 5], [6, 5], [5, 5], [4, 5], [3, 5], [2, 5], [1, 5], [0, 5], [0, 4], [0, 3], [0, 2], [0, 1], [0, 0]]  
        try:
            # If key exists
            routes = self.best[str(start)][str(target)]
        except:
            pass 
        
        # for key in self.best:

        # print("DEBUG ROUTES", routes)
        # print("DEBUG BEST Start: %s Target: %s. Method: %s" % (start, target, method))
        # print("DEBUG BEST WEIGHT", self.bestWeight[str(start)])
        # print("DEBUG BEST LENGTH", self.bestLength[str(start)])
        # print("DEBUG BEST TARGET", target)
        # print("DEBUG BEST PATH", routes)
        
        return routes
        

    def findLargestPathv2(self, route, snakes, turn=0, eating_start={}, foods=[], depth=CONST.lookAheadPathRandom):
        """
        Iterate through path closed space to check volume
        ===
        self
        route
        snakes
        turn=0
        foods=[]
        depth=CONST.lookAheadPath
        ===
        path
        weight
        """

        dots = []
        start = route[-1]
                    
        head = []
        for sid in snakes: 
            if snakes[sid].getType() == 'us':
                head = snakes[sid].getHead()
        if head == route[0]: 
            print("ERROR: LARGEST PATH route should not include head.  \
Puts turn out by 1. head:%s start:%s route:%s turn:%s" % (head, start, route, turn))


         # Start path includes head which is not a turn, hence len(start_path) - 1
        dot_weight = 0 
        dot_length = max(0, turn)
        dot_alpha = {'loc':start, 'weight':0, 'length':dot_length, \
                    'path':route, 'food':[], 'hazard':[], 'to':CONST.directions+[]}

        # Save longest route 
        dot_omega = copy.copy(dot_alpha)
        dot_largest = 0
        
        w = self.width
        h = self.height
        
        dots.append(dot_alpha)
        rr = 0
        rr_max = CONST.maxRecursion

        # while(len(dots)):
        found = False 

        while(len(dots) and rr < rr_max and not found):
                            
            # Each dot recurses into adjacent cells 
            # Always pull last dot 
            # print(dots)
            dot = dots.pop(-1)
            # print("LARGEST", rr, dot)
                
            if len(dot['to']):
                
                rr += 1

                # Take next direction 
                dirn = dot['to'][0]
                dot['to'].pop(0)

                # print("LARGEST DEBUG", route, dot, dirn)  # eating, 
                if len(dot['to']):
                    dots.append(dot)

                alive = False 
              
                # Check next swap 
                dot_loc = list(map(add, dot['loc'], CONST.directionMap[dirn]))
                dot_length = dot['length']
                    
                # Check in bounds 
                if (0 <= dot_loc[0] < h) and (0 <= dot_loc[1] < w):

                    dot_path = dot['path'] + []
                    
                    t = min(dot_length, CONST.lookAheadPathContinue - 2) 
                    dot_weight = dot['weight'] + self.markovs[t+1][dot_loc[0]][dot_loc[1]]
                    
                    # Save turn of food 
                    dot_food = dot['food'] + []
                    if dot_loc in self.foods:
                        dot_food.append(dot_length)
                    
                    # Check if food is in past moves
                    eating = {}

                    foods_eaten = len(dot_food)
                    for sid in snakes:
                        if snakes[sid].getType() == 'us': 
                            if sid in eating_start: 
                                eating[sid] = eating_start[sid] + foods_eaten
                            else: 
                                eating[sid] = foods_eaten
                        else:
                            # Enemy eating in next N turns 
                            if turn >= 1:  
                                eating[sid] = snakes[sid].getEatingFuture()
                            
                    # print(eating)
                    available = self.isRoutePointv2(dot_loc, turn=dot_length, eating=eating, path=dot_path)
                    # if dot_loc in [[5, 3]]: 
                    #     print("LARGEST", available, rr, dot_loc, dot_length, dot_path)  # eating, 
                        
                    # Check we can route 
                    if available: 
                        # if dot_length >= self.trails[dot_loc[0], dot_loc[1]]:
                        
                        # Check if first path 
                        dot_path += [dot_loc] 
                        dot_length += 1

                        dot_hazard = dot['hazard'] + []
                        # dot_constrain = dot['constrain'] + [] 
                        
                        # Save turn of hazard
                        if dot_loc in self.hazards:
                            dot_hazard.append(dot_length)
                            
                        # Save location of constraint
                        # if dot_loc in self.constrains:
                        #     dot_constrain.append(dot_loc)
                            # FIX:  Temporary until we can work out checkConstrain 

                        # if (dot_weight < CONST.pointThreshold):        
                        #     alive = True
                        alive = True   
                        
                # DEBUG 
                # if (dot_weight > 0 and alive and dot_loc in [[10, 2], [10, 1], [9, 1], [8, 1], [8, 2], [8, 3], [8, 4], [8, 5], [8, 6], [7, 6], [6, 6], [6, 7], [6, 8], [6, 9], [6, 10], [5, 10], [4, 10], [3, 10], [2, 10], [1, 10], [0, 10]] ): 
                #     print("DEBUG DOT LOC ", alive, dot_loc, dot_weight) # , dot_path, t, self.markovs[t][dot_loc[0]][dot_loc[1]]) 

                    # print("DEBUG", alive, dot_loc, dot_weight, dot_path) 
                
                # Put dot back on until all dirns exhausted
                
                if alive: 

                    dot_new = {'loc':dot_loc, 
                        'weight':dot_weight,
                        'length':dot_length, 
                        'path':dot_path,
                        'food':dot_food,          # TODO
                        'hazard':dot_hazard,        # TODO
                        'to':CONST.directions+[]
                    }
                
                    # Create another dot (recursive)
                    dots.append(dot_new)
                    # Skip looking other directions 
                    
            if dot_length > depth:
                dot_omega = dot
                # print("BREAK", rr, dot_omega)
                found = True 
                break
            

        # return dot_omega, rr
        return rr, dot_omega


    # def findLargestPath(self, route, snakes, turn=0, foods=[], depth=CONST.lookAheadPath):
    #     """
    #     Iterate through opath closed space to check volume
    #     ===
    #     self
    #     route
    #     snakes
    #     turn=0
    #     foods=[]
    #     depth=CONST.lookAheadPath
    #     ===
    #     path
    #     weight
    #     """

    #     allpaths = []
    #     newpath = []
    #     weight = CONST.routeThreshold

    #     if (len(route)):
    #         start = route[-1]

    #     else:
    #         return newpath, weight 

    #     # Look in all directions
    #     for d in CONST.directions:
    #         newturn = turn + 0    # copy.copy
    #         step = list(map(add, start, CONST.directionMap[d]))
    #         path = route + []     # copy.copy
    #         newpath = []
    #         newweight = 0 
                    
    #         # Check if food is in past moves
    #         eating = self.findEating(snakes, path + [step], foods)
              
    #         # Check next path is in bounds, available and not already visited**            
    #         found = self.isRoutePointv2(step, newturn, eating, path)
    #         if step in [[3, 4], [4, 4], [5, 4], [5, 5], [5, 6], [5, 7], [5, 8], [5, 9], [4, 9], [3, 9], [2, 9], [1, 9], [0, 9], [0, 8], [1, 8], [2, 8]]:
    #             print("DEBUG FINDLARGETS #1", step, found)

            
    #         if(found):
    #             # print("FIND LARGEST STEP", found, step, newturn, path)
    #             t = min(turn, CONST.lookAheadPathContinue - 1) 
    #             weight = self.markovs[t][step[0]][step[1]]
            
    #             # Increment turn 
    #             newturn += 1
    #             # Recursive 
    #             path.append(step)

    #             # WORKING | CHECK:  if tail AND length 
    #             # Move out of recursion into while loop for better control .. ie rr > rmax ?
    #             # if (path == tail and len(path) < eating)
     
    #             (newpath, newweight) = self.findLargestPath_step(step, snakes, newturn, depth, path, weight)
    #             allpaths.append(newpath)
    #             if (len(newpath) >= depth):
    #                 # Good path found - Exit search
    #                 # TODO: Benefit of checking all paths   
    #                 break

    #     # Return largest path .. 
    #     # DEBUG 
    #     # if step == [2, 1]:
    #     # print("FINDPATH", found, step, newpath, newturn, eating)
    
    #     if len(allpaths):
    #         a_sort = sorted(allpaths, key=len)
    #         newpath = a_sort[-1]

    #     # if len(newpath):
    #     return newpath, newweight

    #     # else:
    #     #     return [], CONST.routeThreshold


    # def findLargestPath_step(self,
    #                          route,
    #                          snakes, 
    #                          turn=0,
    #                          depth=CONST.lookAheadPath,
    #                          path=[],
    #                          weight=0):

        
    #     if (len(path) >= depth):
    #         return path, weight

    #     start = route + []          # copy.copy
    #     pathnew = path + []         # copy.copy
    #     weightnew = weight + 0      # copy.copy

    #     # Look in all directions
    #     for d in CONST.directions:

    #         step = list(map(add, start, CONST.directionMap[d]))

    #         # Check next path is in bounds. 
    #         # Probability of collision less than threshold 
    #         # available and not already visited**

    #         # OPTIMISE: Eating not checked -- too expensive
    #         # eating = self.findEating(snakes, path + [step], foods)
            
    #         if(self.isRoutePointv2(step, turn, path=path)):

    #             # Add to dirns
    #             path.append(step)

    #             # Get turn & weight 
    #             turn = turn + 1
    #             t = min(turn, CONST.lookAheadPathContinue - 1)                 
    #             weight += self.markovs[t][step[0], step[1]]

    #             # Get next step (Recursive)
    #             (pathnew, weightnew) = self.findLargestPath_step(step, snakes, turn, depth, path, weight)
    #             # if(step in [[8, 7], [8, 8], [8, 9], [7, 9], [6, 9], [5, 9], [4, 9], [3, 9], [2, 9], [1, 9], [0, 9], [0, 8], [0, 7], [0, 6], [0, 5], [0, 4], [0, 3], [0, 2], [0, 1], [0, 0]]):
    #             #     print("DEBUG", t, step, self.markovs[t][step[0], step[1]])
    #                 # print(self.markovs[t])
    #             # print("LARGEST STEP", str(pathnew), str(path), str(step))

    #         if (len(pathnew) > depth):
    #             break

    #     return pathnew, weightnew



# == FINDERS ==

    def getEnemyFuture(self, snakes, numfuture=CONST.lookAheadPredictFuture):

        sid_us = self.getIdentity()
        for sid in snakes:
                                    
            snake = snakes[sid]
            head = snake.getHead()
            paths = [] 

            enemy = False 
            if sid_us != snake.getId():
                enemy = True 
            
            # Start point (head)
            paths_final = []
            paths.append([head])
            for turn in range(0, numfuture):
                # for N-1 turns look in each direction for each path
                paths_new = []
                for path in paths:             
                    for dirn in CONST.directions:
            
                        head_n = path[-1]                 
                        step = list(map(add, head_n, CONST.directionMap[dirn]))

                        # TODO: Eating - adjust for past / future eating .. 
                        # eating = self.findEating(snakes, path + [step], foods)   
                        found = self.isRoutePointv2(step, turn, path=path, enemy=enemy)
                        route = path + [step]
                        if (found):    
                            # New path found 
                            if (route[0] == head): 
                                # Pop starting position  
                                route.pop(0)
                                
                            paths_new.append(route)

                # Concatenate new paths 
                paths = paths_new + []
                paths_final += paths_new

                # if(len(paths_final) > 40):
                #     print(len(paths_final), paths_final)

            # print("DEBUG SNAKE PATH", enemy, paths)
            # print("DEBUG SNAKE", snake.getId(), paths)
            snake.setNextSteps(paths_final)


    def findClosestWall(self, start):

        ax = start[1]
        ay = start[0]

        w = self.width - 1
        h = self.height - 1
        target = []
        walls = [
            [ay, 0],  # Left
            [ay, w],  # Right
            [h, ax],  # Up
            [0, ax]
        ]  # Down

        # Possible that snake is on wall
        if start in walls:
            r = []
            # print("A")
        else:
            best = w + h
            for wall in walls:
                # Check path weigth
                distance = fn.distanceToPoint(start, wall)
                if distance < best:
                    best = distance
                    target = wall

        return target


    def findClosestNESW(self, start):
        # TODO: Lowest threat or highest control
        # TODO: Where are other snakes (getQuadrant/SideBy)
        w = self.width
        h = self.height

        cardinals = [[0, int(w / 2)], [int(h / 2), 0], [int(h / 2), w],
                     [h, int(w / 2)]]

        pt = []
        dist_min = h * w
        for c in cardinals:
            dist = fn.distanceToPoint(start, c)
            if (dist < dist_min):
                dist_min = dist
                pt = c

        return pt

    def findDirectionWith(self, t=CONST.legend['empty']):
        # TODO: Update to allow array
        # .. eg. [CONST.legend['hazard'], CONST.legend['food']]

        w = self.width
        h = self.height
        bd = self.combine

        xmid = math.floor((w - 1) / 2)
        ymid = math.floor((h - 1) / 2)

        sides = [0] * 4
        # 0 - Top
        # 1 - Bottom
        # 2 - Left
        # 3 - Right
        side_dict = {
            0: CONST.north,
            1: CONST.south,
            2: CONST.west,
            3: CONST.east
        }

        y = 0
        for row in bd:
            x = 0
            for cell in row:
                if (cell == t):
                    if (y > ymid):
                        sides[0] = sides[0] + 1
                    if (y < ymid):
                        sides[1] = sides[1] + 1
                    if (x < xmid):
                        sides[2] = sides[2] + 1
                    if (x > xmid):
                        sides[3] = sides[3] + 1

                x = x + 1
            y = y + 1

        # return quadrants
        max_value = max(sides)
        max_index = sides.index(max_value)

        return side_dict[max_index]

    def findQuadrantWith(self, t=CONST.legend['empty']):
        # Return quadrant with highest/lowest space
        # Used if cannot reach destination
        w = self.width
        h = self.height
        bd = self.combine

        quad_dict = {
            0: CONST.northwest,
            1: CONST.northeast,
            2: CONST.southwest,
            3: CONST.southeast
        }

        xmid = math.floor((w - 1) / 2)
        ymid = math.floor((h - 1) / 2)

        q1 = bd[(ymid + 1):, :xmid]
        q2 = bd[(ymid + 1):, (xmid + 1):]
        q3 = bd[:ymid, :xmid]
        q4 = bd[:ymid, (xmid + 1):]

        quads = [
            np.count_nonzero(q1 == t),
            np.count_nonzero(q2 == t),
            np.count_nonzero(q3 == t),
            np.count_nonzero(q4 == t)
        ]

        max_value = max(quads)
        max_index = quads.index(max_value)

        return quad_dict[max_index]

    def findCentre(self, head):
        # Return centrepoint location or [] if already in the centre
        h = self.height
        w = self.width

        # TODO: Deprecate & change to using self.paintArea('ce', 3)
        yl = math.floor((h + 1) / 2) - 2
        yh = math.floor((h + 1) / 2) + 1

        xl = math.floor((w + 1) / 2) - 2
        xh = math.floor((w + 1) / 2) + 1

        target = np.zeros([h, w], np.intc)
        target[yl:yh, xl:xh] = 1

        ts = np.nonzero(target > 0)

        # Check if we're already within bounds
        for t in ts:
            if (target == head):
                return []

        else:
            return target

    # Return quadrant with highest/lowest threat
    # def findThreat(self):
    #     pass
    #     # break into quadrants
    #     # return

    def findSnakeBox(self, start, enemy):  # self, snake
        # Return closest three vertices as a box array

        w = self.width
        h = self.height
        #board = np.zeros([w,h], np.intc)

        # body = enemy.getHead() + enemy.getBody()
        body = enemy.getBody()
        body.append(enemy.getHead())

        # print("DEFINESNAKE", str(body))

        xmin = w
        xmax = 0
        ymin = h
        ymax = 0

        # Iterate through points in body to get bounds
        for b in body:
            xmin = min(xmin, b[1])
            xmax = max(xmax, b[1])
            ymin = min(ymin, b[0])
            ymax = max(ymax, b[0])

        # Define bounds
        snakebox = [[ymin, xmin], [ymin, xmax], [ymax, xmin], [ymax, xmax]]

        # Get distance to each point
        snakedist = {}
        for pt in snakebox:
            dist = abs(start[0] - pt[0]) + abs(start[1] - pt[1])
            snakedist[dist] = pt

        # print(str(snakedist))

        # Sort list & return first X points
        snakedist = dict(sorted(snakedist.items(), key=lambda item: item[1]))
        i = 0
        imax = 3
        box = []
        for key in snakedist:
            if i < imax:
                box.append(snakedist[key])
            i = i + 1

        # Pad box if only two vertices (small snake)
        while len(box) < imax:
            box.append(box[-1])

        # print("FINDSNAKEBOX", str(snakedist), str(box))

        # Translate to area
        targets = []
        for i in range(0, imax):
            t = np.zeros([w, h], np.intc)
            t[max(box[i][0]-1, 0):min(box[i][0]+2, h), \
                max(box[i][1]-1, 0):min(box[i][1]+2, w)] = 1
            targets.append(t)

        return targets

        # # Find bounds
        # yb_area = np.zeros([w,h], np.intc)
        # xb_area = np.zeros([w,h], np.intc)

        # # Convert to area
        # if ((h - ymax) > (ymin)) and ((w - xmax) < (xmin)):
        #     # North east
        #     yb_area[max(ymax, 0):min(ymax+3, h), (w-3):(w)] = 1
        #     xb_area[0:3, max(xmin-2, 0):min(xmin+1, h)] = 1
        #     dirn = 'ne'

        # elif ((h - ymax) < (ymin)) and ((w - xmax) < (xmin)):
        #     # South east
        #     yb_area[max(ymin-2, 0):min(ymin+1, h), (w-3):(w)] = 1
        #     xb_area[(h-3):(h), max(xmin-2, 0):min(xmin+1, h)] = 1
        #     dirn = 'se'

        # elif ((h - ymax) > (ymin)) and ((w - xmax) > (xmin)):
        #     # North west
        #     yb_area[max(ymax, 0):min(ymax+3, h), 0:3] = 1
        #     xb_area[0:3, max(xmax, 0):min(xmax+3, h)] = 1
        #     dirn = 'nw'

        # else:
        #     # South west (or catchall)
        #     yb_area[max(ymin-2, 0):min(ymin+1, h), 0:3] = 1
        #     xb_area[(h-3):h, max(xmin, 0):min(xmin+3, h)] = 1
        #     dirn = 'sw+'

        # # print(str(dirn))
        # return yb_area, xb_area

# == HELPERS ==

    def moveBy(self, a, diff):
        # Move point (a) by diff
        # Check if in bounds & not solid
        w = self.width
        h = self.height
        s = self.solid

        b = a + diff

        if (0 <= b[0] < h) \
            and (0 <= b[1] < w) \
            and not (s[b[0], b[1]]):

            return b

        return a


    def isEdge(self, pt):
        w = self.width
        h = self.height

        if(pt[0] == 0 or pt[0] == (h - 1)
            or pt[1] == 0 or pt[1] == (w - 1)):     
            return True 
        
        else: 
            return False


    def inBounds(self, a):
        # Check a point (a = [y,x]) is in map bounds

        # Invalid point -- return false
        # if (not len(a)):
        #     return False

        h = self.height
        w = self.width

        try:
            if (0 <= a[0] < h) and (0 <= a[1] < w):
                return True
            else:
                return False

        except Exception as e:
            self.logger.error('exception', 'inBounds', str(e))

        return False

    def drawMask(self, pts, t="array"):
        # Create as mask

        w = self.width
        h = self.height
        # pmask = np.full((w, h), True)
        pmask = np.zeros((w, h), np.intc)

        for p in pts:
            # px = p[0]
            # py = p[1]
            # pmap['x':px, 'y':py] = False
            if (t == "array"):
                pmask[p[0], p[1]] = 1

        return pmask

    def validateRoute(self, path):
        # Take a route & check if valid (against predict)
        # s = self.solid
        # for p in path:
        #   if s[p[0],p[1]] ...

        # Reroute.  Try to use path X
        # route(a, b, x)
        return

    def invertPoint(self, start):
        w = self.width
        h = self.height

        y = h - start[0]
        x = w - start[1]

        target = [y, x]
        return target

    # def getPoint(self, p: Dict[str, int], t="array"):
    #     try:
    #         if (t == "dict"):
    #             return self.land[p["x"], p["y"]]

    #         elif (t == "array"):
    #             return self.land[p]

    #     except:
    #         return []

    def getEmptyAdjacent(self, head):
        w = self.width
        h = self.height
        s = self.solid

        # Get up / down / left / right
        directions = [[head[0] + 1, head[1]], [head[0] - 1, head[1]],
                      [head[0], head[1] + 1], [head[0], head[1] - 1]]

        # Iterate directions
        for d in directions:
            # Check in bounds & not solid
            if (0 <= d[0] < h) \
                and (0 <= d[1] < w) \
                and not (s[d[0], d[1]]):

                return d

        # Final failure. Return last point
        return d

    def getEdges(self):
        # Return all border / edge cells of the map
        w = self.width
        h = self.height

        edges = []
        edges = edges + fn.getPointsInLine([0,0], [0,w]) + \
                    fn.getPointsInLine([w,0], [h,w]) + \
                    fn.getPointsInLine([h,w], [h,0]) + \
                    fn.getPointsInLine([h,0], [0,0])

        return edges

    def randomPoint(self):
        x = int(self.width * rand.random())
        y = int(self.height * rand.random())
        return [y, x]

    def assignIndices(self, sn, it):
        # DEPRECATE: Not used?
        # Give every item unique index ..

        si = []
        fi = []
        hi = []
        n = 1

        labels = ['you:idzol']
        # s1:crepes
        # s2:..
        # f1:food
        # h1:hazard

        for s in sn:
            si.append(n)
            name = s.getName()
            labels.append("s" + n + ":" + str(name))
            n = n + 1

        fn = 1
        hn = 1
        for i in it:
            t = i.getType()

            if (t == "food"):
                name = s.getLabel()
                labels.append("f" + fn + ":food")
                fn = fn + 1
                fi.append(n)

            elif (t == "hazard"):
                name = s.getLabel()
                labels.append("h" + fn + ":food")
                hn = hn + 1
                hi.append(n)

            n = n + 1

        self.youIndex = 0
        self.snakeIndex = si  # [1, 2]
        self.foodIndex = fi  # [3, 4, 5]
        self.hazardIndex = hi  # [6, 7]
        self.labels = labels

        return 1


    def leastWeightLine(self, a, points):
        # TODO: Rewrite to use self.best
        
        # Find path with smallest dijkstra value
        # paths = [[5, 0], [5, 10], [10, 5], [0, 5]]

        # Set arbitrarily large value
        best = CONST.routeThreshold
        r = []

        for p in points:
            # Check path weigth
            path = fn.getPointsInLine(a, p)
            psum, pmax = self.dijkstraPath(path)

            if psum < best:
                best = psum
                r = p

        # self.logger.log('route-leastline-dsum', str(points), str(a), str(r), best)

        return r

    def paintArea(self, select, radius=0, a=0, b=0):
        # area = ['centre', 'radius', 'no', 'ea', 'so', 'we', 'ne', 'nw', 'se', 'sw', 'custom']
        # radius = squares from edge ('radius' only)
        # self.allowed = []

        h = self.height
        w = self.width

        s = select[:]
        allowed = np.zeros([h, w], np.intc)

        # Max Radius
        if 2 * (radius - 1) >= w:
            radius = int(w / 2)

        # Centre
        cy = math.floor((h + 1) / 2) - 1
        cx = math.floor((w + 1) / 2) - 1
        if (w % 2):  # 1x1 or 2x2 squares
            cpt = 1
        else:
            cpt = 2

        # Edge gap - Space from edge
        rx = math.floor(w / 2 - radius)
        ry = math.floor(h / 2 - radius)

        # Half board
        dx = math.floor(w / 2)
        dy = math.floor(h / 2)

        if ('ra' in s):
            # Paint Radius
            allowed[ry:(h - ry), rx:(w - rx)] = 1
       
        if ('ed' in s):
            allowed[0,:] = 1
            allowed[h-1,:] = 1
            allowed[:,0] = 1
            allowed[:,w-1] = 1

        if ('ce' in s):
            # Paint Centre
            allowed[cy:cy + cpt, cx:cx + cpt] = 1

        if ('sw' in s):
            # Paint Bottom Left (sw)
            allowed[0:dy, 0:dx] = 1

        if ('se' in s):
            # Paint Bottom Right (se)
            allowed[0:dy, (w - dx):w] = 1

        if ('nw' in s):
            # Paint Top Left  (nw)
            allowed[(h - dy):h, 0:w] = 1

        if ('ne' in s):
            # Paint Top Right (ne)
            allowed[(h - dy):h, (w - dx):w] = 1

        if ('so' in s):
            # Paint Bottom (s)
            allowed[0:dy, 0:w] = 1

        if ('no' in s):
            # Paint Top (n)
            allowed[(h - dy):h, 0:w] = 1

        if ('we' in s):
            # Paint Left (w)
            allowed[0:h, 0:dx] = 1

        if ('ea' in s):
            # Paint Right (e)
            allowed[0:h, (w - dx):w] = 1

        if ('cu' in s):
            # Paint Custom
            allowed[a[0]:b[0], a[1]:b[1]] = 1

        # print(w, h, cx, cy, rx, ry, dx, dy)
        # print(str(allowed))
        # self.allowed = allowed

        return copy.copy(allowed)


    def enclosedPrison(self, snake, head=[]):
        """
        Return points that are about to expire in prison 
        Return [] if not a prison 
        == 
        start:	snake head (enemy)
        size:  	size of prison (eg. snake length)
        == 
        returns t:list of weakest points in prison 
        """

        w = self.width
        h = self.height

        enclosed = np.zeros([h, w], np.intc)
        enclosed_size = 0

        head = snake.getHead()
        body = snake.getBody()
        prison_size = 2 * snake.getLength()
        
        prison = []
        dots = [head]

        while(len(dots)):
            dots_next = []
            for dot in dots: 
                # Check enclosed space in four directions from start
                for d in CONST.directions:

                    step = list(map(add, dot, CONST.directionMap[d]))

                    # Mark off point 
                    sy = step[0]
                    sx = step[1]
                    
                    # Check inbounds (copy for performance)
                    if (0 <= sy < h) and (0 <= sx < w):

                        # Check if prison size exceeded
                        if enclosed_size > prison_size: 
                            # Not a prison 
                            # print("PRISON BREAK")
                            break 

                        if (enclosed[sy, sx]):
                            # already been here 
                            continue
                        
                        else: 
                            enclosed[sy, sx] = 1

                            # TODO: add body as prison wall .. 
                            # add sn.getTrails()
                            
                            if(self.trails[sy, sx] == 0) :
                                # Prison cell -- point is routable
                                
                                dots_next.append(step)
                                enclosed_size += 1

                            else:
                                # Prison wall 
                                if not (step in prison) :
                                    expires = self.trails[sy, sx]
                                    bar = {'expires':expires, 'point':step}
                                    # Check not already bar, or not current head 
                                    if not (bar in prison) and not (step in head):
                                        prison.append(bar)


                                
            dots = dots_next + []   # copy.copy
       
        # print("PRISON", enclosed, prison, enclosed_size, prison_size)
        if enclosed_size > prison_size: 
            # Not a prison 
            prison_sorted = []
        else: 
            # Sort prison (ascending)
            prison_sorted = sorted(prison, key=lambda d: d['expires'])
        
        return prison_sorted


    def enclosedSpacev2(self, start):
        # Return volume of enclosed spaces in each direction
        # TODO:  If < lenght AND tail < dist...

        w = self.width
        h = self.height

        sy = start[0]
        sx = start[1]

        enclosed = {}

        # Check enclosed space in four directions from start
        for d in CONST.directions:

            encl = np.zeros([h, w], np.intc)
            encl[sy, sx] = 1

            dirn = list(map(add, start, CONST.directionMap[d]))
            # print(str(dirn))

            if (self.inBounds(dirn)):
                # print("ENCLOSED", str(encl), str(dirn))
                encl = self.enclosedSpace_step(encl, dirn)

            enclosed[d] = encl

        enclsum = {}
        # print("ENCLOSED", str(enclosed))
        for d in CONST.directions:
            # Return array of total spaces by direction (eg. up:10
            enclsum[d] = sum(sum(enclosed[d])) - 1
            # print(d, str(enclosed[d]))

        # self.logger.log('enclosed-sum', str(enclsum))
        return enclsum


    def enclosedSpace_step(self, encl, dirn, turn=1):
        # Iterate through closed space to check volume

        dy = int(dirn[0])
        dx = int(dirn[1])
        # s = self.solid
        s = self.trails

        # Trails not defined yet
        if (not len(s)):
            return encl

        # If the point is not a wall
        # print("ENCLOSED-STEP", str(dx), str(dy), str(s))

        if (turn >= s[dy, dx]):
            # Path available -- add to enclosure
            encl[dy, dx] = 1

            for d in CONST.directions:

                dnext = list(map(add, dirn, CONST.directionMap[d]))
                dny = dnext[0]
                dnx = dnext[1]
                # If point is in map & not already visited
                if (self.inBounds(dnext) and not encl[dny, dnx]):
                    # Recursive
                    self.enclosedSpace_step(encl, dnext)

        else:
            # Path not available
            pass

        return encl


    def closestDist(self, us, them: list, same=False):
        """
        Matrix of who is closest to each square 
        ==
        us = sn.getHead()
        them = enemy.getHead()
        same = include squares where we get there same time 
        ==
        TODO: Assumes no solids in closest distance
        otherwise requires a version of route with dijkstra / gradient (ie. closestDist_complex)
        """

        if str(us + them) + str(same) in self.closest: 
            return self.closest[str(us + them) + str(same)]
            
        w = self.width
        h = self.height
        closest = np.zeros([w, h], np.intc)

        for y in range(0, h):
            for x in range(0, w):
                us_dist = abs(us[0] - y) + abs(us[1] - x)
                them_further = True
                
                # Check distance agains each head 
                for th in them:
                    them_dist = abs(y - th[0]) + abs(x - th[1])
                    if not same and them_dist <= us_dist:
                        them_further = False
                    elif same and them_dist < us_dist:
                        them_further = False

                # if y == 8 and x == 3: 
                #     print("DEBUG CLOSEST", us, them, us_dist, them_dist, same, them_further)

                # If they are further we are closer 
                if them_further:
                    closest[y, x] = 1

        # Save for optimisation 
        self.closest[str(us + them) + str(same)] = closest
        return closest

    

    def findEmptySpace(self, point, path=[], turn=1, dirn=True):
        """
        Look at each direction for an empty square. Only looks at body length, not markov .. 
        
        point:  start location 
        path:   previous turns to include in calculation 
        turn:   len(path) 
        dirn:   True = direction (eg. left), False = point (eg. [10,0])
        
        TODO:  Check if this needs to account for food as well?
        """

        s = self.trails

        dirns_avail = []

        for d in CONST.directions:

            dp = list(map(add, point, CONST.directionMap[d]))
            
            # print("EMPTY SPACE", str(d), str(turn), str(s[dy, dx]), str(dnext), str(path))
            if (not dp in path):
                if(self.inBounds(dp)):
                    if(turn >= s[dp[0], dp[1]]):
                
                        # Add to dirns
                        if (dirn):
                            dirns_avail.append(d)
                        else:
                            dirns_avail.append(dp)

        return dirns_avail


    def showMaps(self):
      
        # Routing maps
        # print(self.bestLength)
        # self.logger.maps('LENGTH', self.bestLength)
        # self.logger.maps('WEIGHT', self.bestWeight)
        
        self.logger.maps('TRAILS', self.trails)
        for i in range(0, 20):
            self.logger.maps('MARKOV', self.markovs[i])

        # print(self.markovs)
        # self.logger.maps('CHANCE', self.chance)
        
        # Visual maps
        self.logger.maps('COMBINE', self.combine)


    def showMapsFuture(self, snakes):

        h = self.height
        w = self.width 

        for sid in snakes:
            sn = snakes[sid]

            # print("SNAKE MOVES: ", sn.getType())
            board = np.zeros([h, w], np.intc)
            moves = sn.getRoute()
            t = 0
            for m in moves:
                t += 1
                # Get first m steps in route
                board[m[0],m[1]] = t

            a = sn.getHead()
            if len(a): # self.inBounds(a):
                board[a[0],a[1]] = "1"

            a = sn.getTarget()
            if len(a): # self.inBounds(a):
                board[a[0],a[1]] = "1"

            self.logger.maps("SNAKE MOVES: %s" % sn.getType(), board)

        # print(self.markovs)
        # print(self.bestLength)
        # print(self.bestWeight)
        

# === DELETE ===

    # def isRoutePoint(self, step, turn, path=[]):
    #     # Get step
    #     dy = step[0]
    #     dx = step[1]
    #     # Get markov 
    #     t = min(turn, CONST.lookAheadEnemy - 1)
    #     markov = copy.copy(self.markovs[t])
    #     # Get tails 
    #     s = copy.copy(self.trails)
    #     # Route logic 
    #     if (self.inBounds(step)):
    #       if ((s[dy, dx] == 0) and 
    #           ((markov[dy, dx] < CONST.pointThreshold) or 
    #           (t >= s[dy, dx] and 
    #           markov[dy, dx] < CONST.pointThreshold)) and 
    #           not (step in path)):
    #         return True
    #     else: 
    #       return False 


    # def updateBoardYou(self, data):
    #     # DEPRECATE: Replace with -- updateBoardClass
    #     # Array of snek (101-head, 100-body)
    #     w = self.width
    #     h = self.height
    #     self.you = np.zeros((h, w), np.intc)

    #     body = data['you']['body']
    #     for pt in body:
    #         px = pt['x']
    #         py = pt['y']
    #         self.you[py, px] = CONST.legend['you-body']

    #     try:
    #         head = data['you']['head']
    #         px_head = head['x']
    #         py_head = head['y']
    #         self.you[py_head, px_head] = CONST.legend['you-head']

    #     except Exception as e:
    #         log('exception', 'updateBoardsYou',
    #             'INFO: Your snake head not defined. ' + str(e))

    #     return self.you

    # def updateBoardSnakes(self, data):
    #     # DEPRECATE: Replace with -- updateBoardClass
    #     # Array of snek (201-head, 200-body)
    #     w = self.width
    #     h = self.height
    #     self.snakes = np.zeros((h, w), np.intc)

    #     yid = data['you']['id']
    #     sks = data['board']['snakes']

    #     for sk in sks:
    #         # ignore my snake
    #         if (sk['id'] != yid):

    #             # print (str(sk))
    #             body = sk['body']
    #             for pt in body:
    #                 px = pt['x']
    #                 py = pt['y']
    #                 # self.snakes[h-py-1, px] = self.legend['enemy-body']
    #                 self.snakes[py, px] = CONST.legend['enemy-body']

    #             try:
    #                 head = sk['head']
    #                 px = head['x']
    #                 py = head['y']
    #                 # self.snakes[h-py-1, px] = self.legend['enemy-head']
    #                 self.snakes[py, px] = CONST.legend['enemy-head']

    #             except Exception as e:
    #                 log('exception', 'updateBoardSnakes', str(e))

    #     return self.snakes

    # def updateBoardItems(self, data):
    #     # DEPRECATE: Replace with -- updateBoardClass
    #     # Array of items (300-food, 301-hazard)
    #     w = self.width
    #     h = self.height
    #     self.items = np.zeros((h, w), np.intc)

    #     fds = data['board']['food']
    #     hds = data['board']['hazards']

    #     for fd in fds:
    #         px = fd['x']
    #         py = fd['y']
    #         # self.items[h-py-1, px] = self.legend['food']
    #         self.items[py, px] = self.legend['food']

    #     for hd in hds:
    #         px = hd['x']
    #         py = hd['y']
    #         # self.items[h-py-1, px] = self.legend['hazard']
    #         self.items[py, px] = self.legend['hazard']

    #     return copy.copy(self.items)


    # == ROUTE == enclosedSpace 

     # Eliminate dead ends
        # TODO:  Replaced by routePadding or route fail logic ..
        # for d in CONST.directions:
        #     a1 = list (map(add, a, CONST.directionMap[d]))
        #     if(self.inBounds(a1)):
        #       move = fn.translateDirection(a, a1)

        #       # Weighted threshold based on available moves
        #       moves_avail = self.enclosed[move]
        #       if (moves_avail < length):
        #           self.dijkstra[0][a1[0], a1[1]] = t * (2 - moves_avail / length)

        #     log('enclosed', str(self.enclosed), str(a1))



    # def predictMove_step(self, target, foods, turn=0):
    #     # Based on markov for one snake, calculate most likely path -- eg. food, killcut, other
    #     # TODO:  Special logic for our snake (known path)
        
    #     # Get current body 
    #     turn = min(turn, CONST.lookAheadPath - 1)

    #     snake = copy.copy(target)      
    #     sn_future = snake.getFuture(turn)
              
    #     body = sn_future['body']
    #     if (not (len(body))):
    #       return body
        
    #     # Get current markov 
    #     markov = snake.getMarkov(turn)
                  
    #     # Select path based on probability (start with highest)
    #     new_head = []
    #     if(snake.getType() == 'us'):
    #         # Special logic for us - we know the way 
    #         route = snake.getRoute()
    #         if (turn < len(route)):
    #           new_head = route[turn]
    #         else:
    #           new_head = []
    #           pass

    #     else:  
    #         # Enemy snake             
    #         probs = np.nonzero((markov < 100) & (markov > 0))
    #         prob_max = 0
    #         prob_max_pt = []

    #         for i in range(0, len(probs[0] - 1)):
    #           prob_pt = [probs[0][i], probs[1][i]]
    #           prob = markov[prob_pt[0], prob_pt[1]]
              
    #           if prob > prob_max:
    #             prob_max = copy.copy(prob)
    #             prob_max_pt = copy.copy(prob_pt)
                
    #         if (self.inBounds(prob_max_pt)):
    #             # Make this new head
    #             # markov[prob_max_pt[0], prob_max_pt[1]] = 100
    #             new_head = copy.copy(prob_max_pt)

        
    #     # If eating -- add Tail 
    #     if snake.getEating(): 
    #       tail = body[-1]
    #       body.append(tail)

    #     # Reduce body length by one
    #     body.pop(-1)
        
    #     # Add new head
    #     new_body = copy.copy(body)
    #     if (len(new_head)):
    #         new_body.insert(0, new_head)

    #     # Update body
    #     return new_body



    # def updateDijkstra(self, snakes, depth=CONST.lookAheadPathContinue):

    #     w = self.width
    #     h = self.height

    #     dijksmap = [None] * depth

    #     for t in range(0, depth):
    #         dijksmap[t] = np.zeros([h, w], np.intc)

    #     # ones = CONST.routeCell * np.ones((w, h), np.intc)

    #     for t in range(0, depth):
    #         # Get relevant predict / threat matrix
    #         markov = self.markovs[t]
    #         try:
    #             # Dijkstra combines solids, foods, hazards (threats)
    #             dijksmap[t] = markov + 1

    #             for sid in snakes:
    #                 sn = snakes[sid]
    #                 head = sn.getHead()
    #                 tail = sn.getTail()
    #                 length = sn.getLength()
    #                 who = sn.getType() 
                    
    #                 if who == "us":
    #                     # This turn only (t=0). 
    #                     # Adjust head & tail location to zero for routing
    #                     dijksmap[0][head[0], head[1]] = 0
                
    #                 # Erase tail unless snake is eating
    #                 if length > 3 : 
    #                     # Check trail == 1 (when eating == 2)
    #                     if self.trails[tail[0], tail[1]] == 1: 
    #                         # Reset to markov value (enemy chance)
    #                         dijksmap[0][tail[0], tail[1]] = markov[tail[0], tail[1]] + 1
                        

    #         except Exception as e:
    #             self.logger.error('exception', 'updateDijkstra#1', str(e))

    #     self.dijkstra = copy.copy(dijksmap)



    # == DEPRECATE - Gradient routing == 

        # a = copy.copy(start)
        # b = copy.copy(dest)

        # route = []
        # weight = -1
        # routetype = ''

        # # self.logger.log('route', 'search', a, b)        # log('time', 'Route', self.getStartTime())

        # # If start / finish not defined, return blank
        # if (not len(a) or not len(b) or a == b):
        #     routetype = 'route_error'
        #     return route, weight

   
        # # try simple, medium, complex route
        # while 1:
        #     # (1) Simple straight line (a->b)
        #     route, weight = self.route_basic(a, b)
        #     if len(route):
        #         routetype = 'route_basic'
        #         break

        #     # (2) Simple dog leg (a->c->b)
        #     route, weight = self.route_corner(a, b)
        #     if len(route):
        #         routetype = 'route_corner'
        #         break

        #     # (3) Complex route
        #     # log('time', 'Route Complex', self.getStartTime())
        #     route, weight = self.route_complex(a, b)
        #     if len(route):
        #         routetype = 'route_complex'
        #         break

        #     else:
        #         routetype = 'route_none'
        #         break

        # # Return sorted path/points or [] if no path
        # # self.logger.log('route', routetype, route, weight)
        # return route, weight


    # def route_basic(self, a, b):

    #     r = []
    #     w = CONST.routeThreshold

    #     if (a[0] == b[0]) or (a[1] == b[1]):
    #         # Get points in line & measure route
    #         path = fn.getPointsInLine(a, b)
    #         w, pmax = self.dijkstraPath(path)
    #         # If weight less than threshold, and not deadend
    #         if (w < CONST.routeThreshold):
    #             # Return path
    #             r = [b]

    #     # log("route", "BASIC", str(r), str(w))
    #     return r, w

    # def route_corner(self, a, b):

    #     r = []
    #     corners = [[a[0], b[1]], [b[0], a[1]]]

    #     # Calculate path routes for two options all the individual legs
    #     w = CONST.routeThreshold 
    #     for c in corners:
    #         path = []
    #         path = fn.getPointsInLine(a, c) + fn.getPointsInLine(c, b)
    #         csum, pmax = self.dijkstraPath(path)
            
    #          # Save path weight (total and point)
    #         if (csum < CONST.routeThreshold) :
              
    #             # Save route 
    #             w = csum
    #             r = c

    #     # self.logger.log('route', 'corner %s %s' % (str(path), csum))

    #     if (len(r)):
    #         # Route found 
    #         return [r, b], w
    #     else:
    #         # Return blank path / max route  
    #         return [], w

    # def route_complex(self, a, b):
    #     # Returns path or point. [] if no path or error

    #     # TODO: route_complex_step to use turn  
    #     # tmax = min(t, CONST.lookAheadEnemy - 1)
    #     markov = self.markovs[0]
    #     gradient = self.gradient
    #     route_table = np.maximum(markov, gradient)

    #     h = self.height
    #     w = self.width

    #     # self.isRoutePoint(step, turn, path)

    #     if (not self.inBounds(a) or not self.inBounds(b)):
    #         return [], CONST.routeThreshold

    #     # Gradient to destination
    #     weight = route_table[b[0], b[1]]
    #     if (weight > CONST.routeThreshold):
    #         # no path
    #         return [], CONST.routeThreshold

    #     else:
    #         # Recurse from destination (bnew/b) back to origin (a) until path reached or exceeds num points
    #         path = []
    #         pathlength = 1
    #         bnew = copy.copy(b)

    #         while 1:
    #             # find lowest gradient route & add to path
    #             # print("ROUTE COMPLEX STEP FXN", str(bnew), str(a))
    #             r, grad = self.route_complex_step(bnew, a, route_table)

    #             if (not len(r)): 
    #                 path = []
    #                 weight = CONST.routeThreshold
    #                 break

    #             # Break once reaching destination (a) or at board limit (h * w).  Do not add start (a)
    #             if (r == a) or (pathlength > h * w):
    #                 break

    #             # Otherwise last step (r) becomes first step  (bnew) for next iteration
    #             bnew = copy.copy(r)
    #             pathlength = pathlength + 1

    #             # Update path
    #             path.insert(0, r)

    #             # If in a loop - burn the path & start again
    #             if (len(path) > 2):
    #                 if (path[0] == path[2]):
    #                     burn = path[1]
    #                     # Burn
    #                     route_table[burn[0], burn[1]] = CONST.routeThreshold
    #                     # Reset variables
    #                     path = []
    #                     bnew = copy.copy(b)
    #                     pathlength = 0

    #     # self.logger.log('route complex %s %s' % (str(path), str(weight)))

    #     return path, weight

    # def route_complex_step(self, a, b, route_table, t=0):
    #     # Return next point in complex path based on least weight. [] if no path or error
    #     # log('route-complex-step', a, b)
    #     # Define walls
    #     gradient = CONST.routeThreshold
    #     route = []
        
    #     # Look in each direction
    #     for d in CONST.directions:
    #         a1 = list(map(add, a, CONST.directionMap[d]))

    #         # Check direction is in bounds

    #         # CHECK: monitor for improvements   
    #         if (self.inBounds(a1)):
    #         # if (self.isRoutePoint(a1, t)):

    #             # Check markov & gradient.  Why?  Gradient may not be complete in timer panic.  Check largest in case wall 
    #             r1 = route_table[a1[0], a1[1]]
                
    #             # Find minimum gradient & update next step
    #             if (r1 < gradient):
    #                 gradient = r1
    #                 route = a1

    #             # End found -- terminate process
    #             if (a1 == b):
    #                 break

    #     return route, gradient

        ## == continuePath == 
        # dot_route = copy.copy(route)
        # dot_length = self.bestLength[str(start)][start[0], start[1]]
        # length_max = self.bestLength[str(start)][sy, sx]
        

        # dot_alpha = {'loc':start, 'weight':0, 'length':dot_length, 'path':dot_route, 'from':''}
        # # print("DEBUG", route, dot_alpha, target)
        
        # # Recursive dots 
        # dots = []
        # dots.append(dot_alpha)

        # # Complexity - O(4wh)
        # rr = 0
        # rr_max = CONST.lookAheadPathContinue   #  w + h  

        # best = {}
        # best[str(start)] = dot_alpha
        # # while(len(dots)):

        # # WORKING:  or minweight = 0 (ie. ideal path found )
        # while(len(dots) and rr < rr_max):

        #     dots_next = []
        #     # Each dot recurses into adjacent cells 
        #     for dot in dots:
                         
        #         alive = False    
        #         for dirn in CONST.directions:
        #             alive = False 
        #             if dot['from'] == dirn:
        #                 # Skip direction we came from 
        #                 next 

        #             dot_length = dot['length'] + 1
        #             if dot_length > length_max:
        #                 next 

        #             # Check next swap 
        #             dot_loc = list(map(add, dot['loc'], CONST.directionMap[dirn]))
        #             dot_path = copy.copy(dot['path'])
        #             turn = dot_length - 1 
                    
        #             # Check in bounds 
        #             if self.inBounds(dot_loc):

        #                 # Check if food is in past moves
        #                 eating = self.findEating(snakes, path + [dot_loc], foods)   
                        
        #                 # if(dot_loc in [[10,10], [9,10], [10,8]]):
        #                 #     print("DEBUG", dot_loc)

        #                 # Check next path is in bounds, available and not already visited**            
        #                 found = self.isRoutePointv2(dot_loc, turn, eating, path)
        #                 if (found):
        #                     # TODO:  Introduce weight once markov extended to N 
        #                     t = min(turn, CONST.lookAheadPathContinue - 1) 
                            
        #                     # DEBUG
        #                     # if step == [8, 5]:
        #                     #     print("DEBUG MARKOV WEIGHT", self.markovs[t][step[0]][step[1]])
        #                     dot_weight = dot['weight'] + self.markovs[t][dot_loc[0]][dot_loc[1]]

        #                     # Check if we can route 
        #                     if dot_length == self.bestLength[str(start)][dot_loc[0], dot_loc[1]]:
        #                         if not str(dot_loc) in best: 
        #                             # print("NEW", dot_loc, best)
        #                             alive = True 

        #                             # Check if better path 
        #                         else: 
        #                             dot_omega = best[str(dot_loc)]
        #                             if ((dot_length < dot_omega['length']) or
        #                                     (dot_length == dot_omega['length'] and dot_weight < dot_omega['weight'])):
                                        
        #                                 alive = True
                
        #             else:
        #                 # Kill dot 
        #                 pass 

        #             # if (dot_loc in [[9,10],[10,9],[10,10]]):
        #                 # print("DEBUG", alive, turn, step, path)

        #             if alive == True: 

        #                 dot_path.append(dot_loc)
        #                 # Create another dot (recursive)
        #                 dot_new = {'loc':dot_loc, 
        #                     'weight':dot_weight,
        #                     'length':dot_length, 
        #                     'path':dot_path,
        #                     'from':dirn}
                        
        #                 # print("ADDED", dot_new)
                        
        #                 if dot_loc == target:
        #                     routes.append(dot_new)

        #                 else:  
        #                     best[str(dot_loc)] = dot_new
        #                     dots_next.append(dot_new)
        #                     # Save new best path 
                        
        #             else: 
        #                 pass 
                        
        #             # return 


        #         dots = dots_next
            
        #     # print("routes", routes)
        #     rr += 1

        # # print("CONTINUE PATH", routes)
        # return copy.copy(routes)

