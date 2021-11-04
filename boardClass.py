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
import numpy as np
# import pandas as pd
# import random as rand
import copy as copy
import time as time 

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
        
        # self.land = np.zeros((height, width), np.intc)
        # self.mask = np.ones((height, width), np.intc)

        # self.win = 0
        # self.loss = 0

        # self.threat = [None] * CONST.lookAhead
        # self.predict = [None] * CONST.lookAhead
        # self.gradient = [None] * CONST.maxPredictTurns

        self.best = {}
        self.bestLength = np.zeros((height, width), np.intc)
        self.bestWeight = np.zeros((height, width), np.intc)
        
        self.dijkstra = [None] * CONST.lookAheadPathContinue
        self.markovs = [None] * CONST.lookAheadPathContinue

        self.turn = 0
        
        self.resetCounters()
        

    def setLogger(self, l):
      # Reference 
      self.logger = l

    def resetCounters(self):
        # Reset start of each turn 
        self.recursion_route = 0
        self.hurry = False
        # self.gradients = {}


    def resetRouting(self):
        # Reset start of each turn 
        h = self.height
        w = self.width 

        markovs = []
        dijkstra = []
        
        depth = CONST.lookAheadPathContinue
        for t in range(0, depth):
            dijkstra.append(np.zeros([h, w], np.intc))
            # Enemy prediction 
            markovs.append(np.zeros([h, w], np.intc))

        self.markovs = copy.copy(markovs)
        self.dijkstra = copy.copy(dijkstra)


# == GETTER / SETTER ==

    def setDimensions(self, x, y):
        if isinstance(x, int) and isinstance(y, int):
            self.width = x
            self.height = y
            # self.land = np.zeros((x, y), np.intc)
            return True

        else:
            return False

    def getDimensions(self):
        return [self.width, self.height]

    def getWidth(self):
        return self.width

    def setIdentity(self, i):
        self.identity = copy.copy(i)

    def getIdentity(self):
        i = copy.copy(self.identity)
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

    def getYou(self):
        return copy.copy(self.you)

    def getSolid(self):
        return copy.copy(self.solid)

    def getCombine(self):
        return copy.copy(self.combine)

    def getThreat(self):
        return copy.copy(self.threat)

    def getSnakes(self):
        return copy.copy(self.snakes)

    def getItems(self):
        return copy.copy(self.items)

    def getDijkstra(self):
        return copy.copy(self.dijkstra)

    def setDijkstra(self, d):
        self.dijkstra = copy.copy(d)

    # # Return future predict matrix
    # def getPredictMatrix(self, t):
    #     return self.predict[t]

    def getTurn(self):
        t = self.turn
        return copy.copy(t)

    def setTurn(self, t):
        self.turn = t


# == BOARDS ==

    def updateBoards(self, data, us, snakes, foods):
        # Enclosed - xx
        # Solid - xx
        # Combine - Array of all layers (snakes, walls, items)

        # Snake Head
        hy = data['you']['head']['y']
        hx = data['you']['head']['x']
        head = [hy, hx]

        # Update game parameters
        width = int(data['board']['width'])
        height = int(data['board']['height'])
        self.setDimensions(width, height)
        self.setTurn(data['turn'])

        self.updateBoardObjects(us, snakes, foods)
        # # Update boards
        # by = self.updateBoardYou(data)
        # bs = self.updateBoardSnakes(data)
        # bi = self.updateBoardItems(data)

        # # Combined boards
        # rs = CONST.routeSolid
        # self.solid = rs * np.ceil(by / (by + 1) + bs / (bs + 1))
        # self.combine = by + bs + bi

        tr = self.updateTrails(snakes)

        # Meta boards
        depth = CONST.lookAheadPathContinue
        
        en = self.enclosedSpacev2(head)
        self.enclosed = copy.copy(en)  # TODO: move to snake object ..

        # Routing Boards - init (blank)
        # predict = []
        # threat = []
        markovs = []
        dijkstra = []
  
        for t in range(0, depth):
            # predict.append(np.zeros([height, width], np.intc))
            # threat.append(np.zeros([height, width], np.intc))
            markovs.append(np.zeros([height, width], np.intc))
            dijkstra.append(np.zeros([height, width], np.intc))

            # self.updateGradient() -- only update when rqd for routing
        self.markovs = copy.copy(markovs)
        self.dijkstra = copy.copy(dijkstra)


        # self.predict = predict
        # self.threat = threat

        # Other meta-boards
        # bt = self.updateThreat(data, snakes) -- needs snakes
        # self.updateDijkstra(fn.XYToLoc(data['you']['head']))
        # gr = self.updateGradient() -- only update when rqd for routing

        # TODO: Clear boards ..
        return True


    def updateBoardObjects(self, us, snakes, foods):     
        w = self.width
        h = self.height

        # SNAKES 
        snakeboard = np.zeros((h, w), np.intc)
        for skid in snakes:

            sk = snakes[skid]
            if sk.getType() != 'us':
                # print (str(sk))
                body = sk.getBody()
                for pt in body:
                    px = pt[1]
                    py = pt[0]

                    snakeboard[py, px] = CONST.legend['enemy-body']

                try:
                    head = sk.getHead()
                    px = head[1]
                    py = head[0]
                    # self.snakes[h-py-1, px] = self.legend['enemy-head']
                    snakeboard[py, px] = CONST.legend['enemy-head']

                except Exception as e:
                    self.logger.error('exception', 'updateBoardSnakes', str(e))

        # YOU 
        youboard = np.zeros((h, w), np.intc)

        body = us.getBody()
        for pt in body:
            px = pt[1]
            py = pt[0]
            youboard[py, px] = CONST.legend['you-body']

        try:
            head = us.getHead()
            px_head = head[1]
            py_head = head[0]
            youboard[py_head, px_head] = CONST.legend['you-head']

        except Exception as e:
            self.logger.error('exception', 'updateBoardsYou',
                'INFO: Your snake head not defined. ' + str(e))

        # ITEMS 
        itemboard = np.zeros((h, w), np.intc)
        for fd in foods:

            px = fd[1]
            py = fd[0]
            # self.items[h-py-1, px] = self.legend['food']
            itemboard[py, px] = self.legend['food']

        # for hd in hds:
        #     px = hd[1]
        #     py = hd[0]
        #     # self.items[h-py-1, px] = self.legend['hazard']
        #     itemboard[py, px] = self.legend['hazard']

        rs = CONST.routeSolid

        # Update boards 
        self.you = copy.copy(youboard)
        self.snakes = copy.copy(snakeboard)
        self.items = copy.copy(itemboard)
        self.solid = rs * np.ceil(youboard / (youboard + 1) + snakeboard / (snakeboard + 1))
        self.combine = youboard + snakeboard + itemboard
        
        return copy.copy(self.combine)


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

        turns = CONST.lookAheadEnemy
        # us = self.getIdentity()

        for snid in snakes:
          sn = snakes[snid]
          head = sn.getHead()
          
          # if (sn.getId() != us):
          for turn in range(0, turns):
            chance = self.pathProbability(head, turn + 1)
            sn.setChance(chance, turn)


    def updateCell(self, cell, chance, turn=0):
        # Paint cell as routable, not routable  
        if(self.inBounds(cell)):
            # Paint markov matrix for turn t + 1
            y = cell[0]
            x = cell[1]
            self.markovs[turn][y, x] = chance
                

    def updateMarkov(self, us, snakes:dict, foods:list, turns=CONST.lookAheadPathContinue): 
      
      w = self.width
      h = self.height
      markovs = []

      turns = min(turns, CONST.lookAheadPathContinue)
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
              
              # BUGFIX:  check/  Body already includes head, ie. function was doubleprinting head?
              # sn_body = sn.getHeadBody()
              sn_body = sn.getBody()
              sn.setFuture(sn_body, 0)
              body = copy.copy(sn_body)

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
            for cell in body: 
                if(self.inBounds(cell)):
                    # Paint markov matrix for turn t + 1
                    y = cell[0]
                    x = cell[1]
                    markov[y, x] = 100
            
            sn.setMarkovBase(copy.copy(markov), t)
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
                    try:
                      markov = markov + chance 

                    except Exception as e:
                      # Get markov from one before 
                      # markov = sn.getMarkov(t - 1)
                      self.logger.error('exception', 'updateMarkov', str(e))
                
                sn.setMarkov(copy.copy(markov), t)
            
            # ===================
            # snakes[sid] = copy.deepcopy(sn)

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
              if sn.getLength() < us.getLength() or t >= CONST.lookAheadEnemy:
                # Remove threat from smaller snakes, or after N turns (because snake threat unknown)
                markov_sn = sn.getMarkovBase(t)
              else:
                markov_sn = sn.getMarkov(t)
                  
              markov = markov + markov_sn 

          # print("LENGTH", len(self.markovs), t)
          self.markovs[t] = copy.copy(markov)
          # self.markovbase[t] = copy.copy(markov)
      
      # self.markovs = copy.copy(markovs)     


    def updateDijkstra(self, snakes, depth=CONST.lookAheadPathContinue):

        w = self.width
        h = self.height

        dijksmap = [None] * depth

        for t in range(0, depth):
            dijksmap[t] = np.zeros([h, w], np.intc)

        # ones = CONST.routeCell * np.ones((w, h), np.intc)

        for t in range(0, depth):
            # Get relevant predict / threat matrix
            markov = self.markovs[t]
            try:
                # Dijkstra combines solids, foods, hazards (threats)
                dijksmap[t] = markov + 1

                for sid in snakes:
                    sn = snakes[sid]
                    head = sn.getHead()
                    tail = sn.getTail()
                    length = sn.getLength()
                    who = sn.getType() 
                    
                    if who == "us":
                        # This turn only (t=0). 
                        # Adjust head & tail location to zero for routing
                        dijksmap[0][head[0], head[1]] = 0
                
                    # Erase tail unless snake is eating
                    if length > 3 : 
                        # Check trail == 1 (when eating == 2)
                        if self.trails[tail[0], tail[1]] == 1: 
                            # Reset to markov value (enemy chance)
                            dijksmap[0][tail[0], tail[1]] = markov[tail[0], tail[1]] + 1
                        

            except Exception as e:
                self.logger.error('exception', 'updateDijkstra#1', str(e))

        self.dijkstra = copy.copy(dijksmap)

       
    def updateBest(self, start):
        # OPTIMISE: Benchmark with/without copy.copy 

        w = self.width 
        h = self.height
        # Find path to all points on the board by length, weight 
      
        dot_alpha = {'loc':start, 'weight':0, 'length':0, 'path':[], 'from':''}
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
        rr_max = CONST.lookAheadPathContinue    #  w + h  

        # while(len(dots)):
        while(len(dots) or rr < rr_max):

            dots_next = []
            # Each dot recurses into adjacent cells 
            # print("NEXT", rr, dots)
            for dot in dots:

                alive = False    
                for dirn in CONST.directions:
                    alive = False 
                    if dot['from'] == dirn:
                        # Skip direction we came from 
                        next 

                    # Check next swap 
                    step = list(map(add, dot['loc'], CONST.directionMap[dirn]))
                    dot_loc = copy.copy(step)
                    dot_path = copy.copy(dot['path'])
                    dot_length = copy.copy(dot['length'] + 1)

                    # Check in bounds 
                    if self.inBounds(step):
                        t = min(dot_length, CONST.lookAheadPathContinue) 
                        dot_weight = dot['weight'] + self.markovs[t-1][step[0]][step[1]]
                        
                        
                        # Check if edge - don't route along walls, save for escapes
                        # if not self.isEdge(step):
                        # Check we can route 
                        if dot_length >= self.trails[dot_loc[0], dot_loc[1]]:
                            # Check if first path 
                            if not str(dot_loc) in best: 
                                # print("NEW", dot_loc, best)
                                alive = True 

                                # Check if better path 
                            else: 
                                dot_omega = best[str(dot_loc)]
                                
                                if (dot_length < dot_omega['length'] or
                                        (dot_length == dot_omega['length'] and
                                        dot_weight < dot_omega['weight'])):

                                    alive = True
          
                    else:
                        # Kill dot 
                        pass 

                    # DEBUG 
                    # if (dot_loc in [[9, 8]]):
                    #     print("DEBUG", alive, dot_loc, dot_weight, self.markovs[t-1][step[0]][step[1]]) 


                    if alive == True: 

                        dot_path.append(dot_loc)
                        # Create another dot (recursive)
                        dot_new = {'loc':copy.copy(dot_loc), 
                            'weight':copy.copy(dot_weight),
                            'length':copy.copy(dot_length), 
                            'path':copy.copy(dot_path),
                            'from':copy.copy(dirn)}
                        # print(dot_new)
                    
                        dots_next.append(dot_new)
                        # Save new best path 
                        best[str(dot_loc)] = dot_new
                        best_length[dot_loc[0], dot_loc[1]] = copy.copy(dot_length)
                        best_weight[dot_loc[0], dot_loc[1]] = copy.copy(dot_weight)
                

                dots = copy.copy(dots_next)
            
            # print("LAST", rr)
            rr += 1

        # Boards 
        # print("BEST LENGTH", best_length)
        self.bestLength = best_length
        self.bestWeight = best_weight
        
        # Save board        
        self.best = best            


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
            self.trailsSnake[sid] = copy.copy(snake)

        # All trails 
        self.trails = copy.copy(trails)
        return trails


    def pathProbability(self, head, depth=CONST.lookAheadEnemy):
        # Calculates the probability assuming random walk from any location on the board (head), given obstacles (trails)
        # Returns probablility board (chance) from 0 - 100 (%)

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
            self.pathProbability_step(chance, path, prob, step, turn, depth)

        # dirn_avail.remove(dirn)
        # print(str(dirn_avail))
        
        # Avoid edges if possible .. 
        # edges = self.paintArea('edges')
        # chance = chance + 5 * edges 

        return chance


    def pathProbability_step(self, chance, path, prob, step, turn=1, depth=CONST.lookAheadEnemy):

        if (len(path) > depth): 
          return chance 

        dy = int(step[0])
        dx = int(step[1])
        s = self.trails

        # Check if not blocked
        if (turn >= s[dy, dx]):

            # Add to enclosure
            chance[dy, dx] = chance[dy, dx] + prob
            dirn_avail = self.findEmptySpace(step, path, turn + 1)
            path_new = copy.copy(path)
            path_new.append(step)
        

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

                    chance = self.pathProbability_step(chance, path_new, prob_new, dnext, turn, depth)

        else:
            pass

        return chance


# == ROUTING ==

# TODO: Fuzzy Routing, ie. get close to an object)

    def fuzzyRoute(self, start, targetmap):
        # Send shape - return best path to any point in shape
        # a = [1, 1]
        # b = np.zeros([h, w], np.intc)
        # b[1:3, 3:6] = 1
        # result, weight = fuzzyRoute(a, b)
        w = self.width
        h = self.height
        
        route = []
        route_weight = CONST.routeThreshold
 
        a = copy.copy(start)
        b = copy.copy(targetmap)
        
        r = np.zeros([h, w], np.intc)
        r = r + b
        r[a[0], a[1]] = 1

        targets = np.nonzero(b > 0)
        
        # Iterate through potential targets
        for i in range(0, len(targets[0] - 1)):
            t = [targets[0][i], targets[1][i]]
            try:
                r, w = self.route(a, t)
                # Save best route 
                if w < route_weight:
                    route = r
                    route_weight = w

            except Exception as e:
                self.logger.error('exception', 'fuzzyRoute', str(e))
                pass

        return copy.copy(route), copy.copy(route_weight)


    def route(self, start, dest, threshold=CONST.routeThreshold):

        # if start != us.getHead()
        #   warning -- ie. best only valid for start 
         
        route = []
        weight = CONST.routeThreshold

        if start == dest: 
            return [start], 0

        if self.inBounds(dest):
            if str(dest) in self.best:
                route = self.best[str(dest)]['path']
                weight = self.best[str(dest)]['weight']
        
        return copy.copy(route), copy.copy(weight)

        # == DEPRECATE - Gradient routing == 

        a = copy.copy(start)
        b = copy.copy(dest)

        route = []
        weight = -1
        routetype = ''

        # self.logger.log('route', 'search', a, b)        # log('time', 'Route', self.getStartTime())

        # If start / finish not defined, return blank
        if (not len(a) or not len(b) or a == b):
            routetype = 'route_error'
            return route, weight

   
        # try simple, medium, complex route
        while 1:
            # (1) Simple straight line (a->b)
            route, weight = self.route_basic(a, b)
            if len(route):
                routetype = 'route_basic'
                break

            # (2) Simple dog leg (a->c->b)
            route, weight = self.route_corner(a, b)
            if len(route):
                routetype = 'route_corner'
                break

            # (3) Complex route
            # log('time', 'Route Complex', self.getStartTime())
            route, weight = self.route_complex(a, b)
            if len(route):
                routetype = 'route_complex'
                break

            else:
                routetype = 'route_none'
                break

        # Return sorted path/points or [] if no path
        # self.logger.log('route', routetype, route, weight)
        return route, weight


    def route_basic(self, a, b):

        r = []
        w = CONST.routeThreshold

        if (a[0] == b[0]) or (a[1] == b[1]):
            # Get points in line & measure route
            path = fn.getPointsInLine(a, b)
            w, pmax = self.dijkstraPath(path)
            # If weight less than threshold, and not deadend
            if (w < CONST.routeThreshold):
                # Return path
                r = [b]

        # log("route", "BASIC", str(r), str(w))
        return r, w

    def route_corner(self, a, b):

        r = []
        corners = [[a[0], b[1]], [b[0], a[1]]]

        # Calculate path routes for two options all the individual legs
        w = CONST.routeThreshold 
        for c in corners:
            path = []
            path = fn.getPointsInLine(a, c) + fn.getPointsInLine(c, b)
            csum, pmax = self.dijkstraPath(path)
            
             # Save path weight (total and point)
            if (csum < CONST.routeThreshold) :
              
                # Save route 
                w = csum
                r = c

        # self.logger.log('route', 'corner %s %s' % (str(path), csum))

        if (len(r)):
            # Route found 
            return [r, b], w
        else:
            # Return blank path / max route  
            return [], w

    def route_complex(self, a, b):
        # Returns path or point. [] if no path or error

        # TODO: route_complex_step to use turn  
        # tmax = min(t, CONST.lookAheadEnemy - 1)
        markov = copy.copy(self.markovs[0])
        gradient = copy.copy(self.gradient)
        route_table = np.maximum(markov, gradient)

        h = self.height
        w = self.width

        # self.isRoutePoint(step, turn, path)

        if (not self.inBounds(a) or not self.inBounds(b)):
            return [], CONST.routeThreshold

        # Gradient to destination
        weight = route_table[b[0], b[1]]
        if (weight > CONST.routeThreshold):
            # no path
            return [], CONST.routeThreshold

        else:
            # Recurse from destination (bnew/b) back to origin (a) until path reached or exceeds num points
            path = []
            pathlength = 1
            bnew = copy.copy(b)

            while 1:
                # find lowest gradient route & add to path
                # print("ROUTE COMPLEX STEP FXN", str(bnew), str(a))
                r, grad = self.route_complex_step(bnew, a, route_table)

                if (not len(r)): 
                    path = []
                    weight = CONST.routeThreshold
                    break

                # Break once reaching destination (a) or at board limit (h * w).  Do not add start (a)
                if (r == a) or (pathlength > h * w):
                    break

                # Otherwise last step (r) becomes first step  (bnew) for next iteration
                bnew = copy.copy(r)
                pathlength = pathlength + 1

                # Update path
                path.insert(0, r)

                # If in a loop - burn the path & start again
                if (len(path) > 2):
                    if (path[0] == path[2]):
                        burn = path[1]
                        # Burn
                        route_table[burn[0], burn[1]] = CONST.routeThreshold
                        # Reset variables
                        path = []
                        bnew = copy.copy(b)
                        pathlength = 0

        # self.logger.log('route complex %s %s' % (str(path), str(weight)))

        return path, weight

    def route_complex_step(self, a, b, route_table, t=0):
        # Return next point in complex path based on least weight. [] if no path or error
        # log('route-complex-step', a, b)
        # Define walls
        gradient = CONST.routeThreshold
        route = []
        
        # Look in each direction
        for d in CONST.directions:
            a1 = list(map(add, a, CONST.directionMap[d]))

            # Check direction is in bounds

            # CHECK: monitor for improvements   
            if (self.inBounds(a1)):
            # if (self.isRoutePoint(a1, t)):

                # Check markov & gradient.  Why?  Gradient may not be complete in timer panic.  Check largest in case wall 
                r1 = route_table[a1[0], a1[1]]
                
                # Find minimum gradient & update next step
                if (r1 < gradient):
                    gradient = r1
                    route = a1

                # End found -- terminate process
                if (a1 == b):
                    break

        return route, gradient

    def dijkstraPath(self, path, turn=0):
        # Sum dijkstra map between two points
        
        # Check which prediction matrix to use
        tmax = min(turn, CONST.lookAheadPathContinue - 1)

        result = 0

        # Capture largest increment (probability of collision)  
        largest_point = 0
        
        # Iterate through path
        dt = self.getDijkstra()

        for p in path:
            if self.inBounds(p):

                # Add dijkstra value
                increment = int(dt[tmax][p[0], p[1]])
                result = result + increment
                tmax = tmax + 1
                if (increment > largest_point):
                  largest_point = increment 

        return copy.copy(result), copy.copy(largest_point)


    def routePadding(self, route, snakes, foods, depth=CONST.lookAheadPathContinue):
        # Make sure there is always a path with N moves (eg. route_complex + random walk)
        
        path = []
        weight = CONST.routeThreshold
        
        # Needs minimum one point to start padding route
        if (not len(route)):
            return path, weight

        # Convert vectors to points
        if (len(route) > 1):
            path_start = fn.getPointsInRoute(route)
        else: 
            path_start = copy.copy(route)

        
        # Confirm we have a path
        if (turn := len(path_start)):

            # Get snake info 
            sid_us = self.getIdentity()
            us = snakes[sid_us]
            length = us.getLength()
            
            # Get turn based on path (past moves)
            start = path_start[-1]

            routefound = False 

            # Routing methods used 
            tailrouting = False     # don't think this works anymore .. 
            bestrouting = True
            randomrouting = True              
            # self.logger.log("route pad", str(path)) 

            # == DEPRECATE == 
            # A) Route to tail for end game control -- NOTE: longest path may NOT always be tail -> head
            if (tailrouting and not routefound): 
                if length > CONST.lengthEndGame:
                    tail = us.getTail()
                    path_padding, weight = self.route(start, tail)  
                    # print("ROUTE TO TAIL", path, weight, original) 
                         
                    if len(path_padding) > 0 and weight < CONST.routeThreshold:
                        # Add rest of body 
                        body = (us.getBody())
                        body.pop(-1)
                        body.reverse()
                        # Return total
                        path = path_start + path_padding + body
                        path = fn.getPointsInRoute(path)
                        routefound = True  
                # print("DEBUG", original, path, body)

            # B) Largest path - using bestPath 
            if (bestrouting and not routefound): 

                routes = self.continuePath(path_start, snakes, foods, depth)

                if (len(routes)):  
                    # TODO: Introduce weight if multiple paths ..
                    # .. for now select least weight 
                    routes_sorted = sorted(routes, key=lambda d: d['weight']) 
                    # Path comes back reversed 
                    weight = routes_sorted[0]['weight']
                    path = routes_sorted[0]['path']
                    # path = copy.copy(path_padding)                        
                    routefound = True 

                else:  
                    path = []
                    weight = CONST.routeThreshold

            # C) Find Largest path in random walk 
            if (randomrouting and not routefound):

                path, weight = self.findLargestPath(path_start, snakes, turn, foods, depth)
                
                if (len(path)):  
                    target = path[-1]
                    # weight = 0 # self.bestWeight[target[0], target[1]]        
                    routefound = True 

                # print("DEBUG", randomrouting, routefound, newpath, weight)
                   
        # self.logger.log("route pad", str(path), str(len(path)), str(depth))
        # Return path = route + path_padding 
        # Remove first point of route (head)
        if (routefound and len(path)):
            if path[0] == start:
                path.pop(0)
            
            return copy.copy(path), copy.copy(weight)

        else:
            # Return original route & zero incremental weight 
            if route[0] == start:
                route.pop(0)
             
            return copy.copy(route), 0



    def isRoutePointv2(self, start, turn, eating={}, path=[], enemy=False):
        # Start - check route points from start location
        # Turn - adjust for future turn state 
        # Eating - adjust for past / future eating 
        # Path - check past path points for collision
        # Enemy - ignore markov threat when predicting enemy moves

        w = self.width
        h = self.height

        step = copy.copy(start)
        # Get step
        dy = step[0]
        dx = step[1]

        # Get markov 
        
        t = min(turn, CONST.lookAheadEnemy - 1)
        markov = copy.copy(self.markovs[t])

        # Get tails 
        trails = copy.copy(self.trailsSnake)
        board = np.zeros([w, h], np.intc)

        for sid in trails:
          # Adjust trails for each snake based on eating
          if sid in eating.keys(): 
              board += np.where(trails[sid], trails[sid] + eating[sid], trails[sid])  

          else: 
              board += trails[sid]
    
        # DEBUG ..
        # if step == [2, 1]:
        #     print("DEBUG", dx, dy, turn, step, path)
        #     print("MARKOV", markov[dy, dx])
        #     print("BOARD", board[dy, dx])
        # if(step in [[4,7]]):
        #     print("DEBUG", markov[dy, dx], turn, board[dy, dx])

        # Route logic 
        if (self.inBounds(step)):
          if ( # Our prediction logic
                ((turn >= board[dy, dx] and 
                markov[dy, dx] < CONST.routeThreshold) and 
                # (((markov[dy, dx] < CONST.pointThreshold) or 
                # (turn >= board[dy, dx] and 
                # markov[dy, dx] >= CONST.routeThreshold)) and 
                not (step in path)) or 
                # Enemy prediction logic 
                (enemy and 
                turn >= board[dy, dx] and 
                not (step in path)) 
              ):

            return True     # copy.copy(markov[dy, dx])
            
        return False        # CONST.pointThreshold)


    def hasEaten(self, snakes, foods):
        # this is taken care of in self.trails 
        pass
        

    def findEating(self, snakes, path, foods):

        eating = {}
        for sid in snakes: 
            
            if (snakes[sid].getType() == "us"): 

              try:
                # Check if food is in future moves
                food_in_route = len(list(filter(lambda x: x in foods, path)))
                eating[sid] = food_in_route
              
              except:
                eating[sid] = 0

            else:  
                # TODO:  Logic for other enemy snakes 
                eating[sid] = 0

        return eating 


    def continuePath(self, route, snakes, foods=[], depth=CONST.lookAheadPathContinue):
   
        w = self.width 

        if not len(route):
            return [], CONST.routeThreshold

        else:
            start = copy.copy(route[-1])
            path = copy.copy(route)
                
        # Look for dots that makes it to longest path..
        routes = []
        weight = 0 

        # Find largest route (usually tail->head)
        # TODO: Check why weight = 100X,  probably because markov limit  
        rfactor = self.bestLength / (self.bestWeight + 1)
        # rfactor = self.bestLength 
        # print ("RFACTOR", rfactor)
        
        smax = np.argmax(rfactor)
        sy = int(smax / w)
        sx = smax % w
        target = [sy, sx]
        # print ("RFACTOR BEST", target)
        dot_route = copy.copy(route)
        dot_length = self.bestLength[start[0], start[1]]
        length_max = self.bestLength[sy, sx]
        
        dot_alpha = {'loc':start, 'weight':0, 'length':dot_length, 'path':dot_route, 'from':''}
        # print("DEBUG", route, dot_alpha, target)
        
        # Recursive dots 
        dots = []
        dots.append(dot_alpha)

        # Complexity - O(4wh)
        rr = 0
        rr_max = CONST.lookAheadPathContinue   #  w + h  

        best = {}
        best[str(start)] = dot_alpha
        # while(len(dots)):

        # WORKING:  or minweight = 0 (ie. ideal path found )
        while(len(dots) and rr < rr_max):

            dots_next = []
            # Each dot recurses into adjacent cells 
            # print("NEXT", rr, dots)
            # print("START", rr, dots)
            
            for dot in dots:
                         
                alive = False    
                for dirn in CONST.directions:
                    alive = False 
                    if dot['from'] == dirn:
                        # Skip direction we came from 
                        next 

                    # Check next swap 
                    step = list(map(add, dot['loc'], CONST.directionMap[dirn]))
                    
                    dot_loc = copy.copy(step)
                    dot_path = copy.copy(dot['path'])
                    dot_length = copy.copy(dot['length']) + 1 
                    turn = dot_length - 1 
                    
                    if dot_length > length_max:
                        next 

                    # Check in bounds 
                    if self.inBounds(dot_loc):

                        # Check if food is in past moves
                        eating = self.findEating(snakes, path + [step], foods)   
                        
                        # if(dot_loc in [[4,7], [2,7], [3,6]]):
                        #     print("DEBUG", dot_loc, eating)

                        # Check next path is in bounds, available and not already visited**            
                        found = self.isRoutePointv2(step, turn, eating, path)
                        if (found):
                            # TODO:  Introduce weight once markov extended to N 
                            t = min(turn, CONST.lookAheadPathContinue - 1) 
                            dot_weight = copy.copy(dot['weight'] + self.markovs[t][step[0]][step[1]]) 
                            # dot_weight = 0 

                            # print ("LOC", dot_length, self.bestLength[dot_loc[0], dot_loc[1]])

                            # Check if we can route 
                            if dot_length == self.bestLength[dot_loc[0], dot_loc[1]]:
                                if not str(dot_loc) in best: 
                                    # print("NEW", dot_loc, best)
                                    alive = True 

                                    # Check if better path 
                                else: 
                                    dot_omega = best[str(dot_loc)]
                                    if ((dot_length < dot_omega['length']) or
                                            (dot_length == dot_omega['length'] and dot_weight < dot_omega['weight'])):
                                        
                                        alive = True
                
                    else:
                        # Kill dot 
                        pass 

                    # if (dot_loc in [[9,10],[10,9],[10,10]]):
                        # print("MERP", alive, turn, step, path)

                    if alive == True: 

                        dot_path.append(dot_loc)
                        # Create another dot (recursive)
                        dot_new = {'loc':copy.copy(dot_loc), 
                            'weight':copy.copy(dot_weight),
                            'length':copy.copy(dot_length), 
                            'path':copy.copy(dot_path),
                            'from':copy.copy(dirn)}
                        
                        # print("ADDED", dot_new)
                        
                        if dot_loc == target:
                            routes.append(dot_new)

                        else:  
                            best[str(dot_loc)] = dot_new
                            dots_next.append(dot_new)
                            # Save new best path 
                        
                    else: 
                        pass 
                        # print("REKECTED", found, step, turn, path)
                    # return 


                dots = copy.copy(dots_next)
            
            # print("routes", routes)
            rr += 1

        # print("CONTINUE PATH", routes)
        return copy.copy(routes)


    def findLargestPath(self, route, snakes, turn=0, foods=[], depth=CONST.lookAheadPath):
        # Iterate through closed space to check volume
        # **TODO: Include own path as layer in future updateTrails
        # TODO: Introduce panic timers if routing too long
        # TODO: Introduce threat from other snakes into s[dy, dx] -> s[turn][dy, dx] udating predict matrix
        # TODO:  Return best path vs any path (similar to introducing snake threat

        allpaths = []
        newpath = []
        weight = CONST.routeThreshold

        if (len(route)):
            start = copy.copy(route[-1])

        else:
            return newpath, weight 

        # Look in all directions
        for d in CONST.directions:
            newturn = copy.copy(turn)
            step = list(map(add, start, CONST.directionMap[d]))
            path = copy.copy(route)
            newpath = []
                    
            # Check if food is in past moves
            eating = self.findEating(snakes, path + [step], foods)
              
            # Check next path is in bounds, available and not already visited**            
            found = self.isRoutePointv2(step, newturn, eating, path)
            
            
            if(found):
                # print("FIND LARGEST STEP", found, step, newturn, path)
                t = min(turn, CONST.lookAheadPathContinue - 1) 
                weight = self.markovs[t][step[0]][step[1]]
            
                # Increment turn 
                newturn += 1
                # Recursive 
                path.append(step)

                # WORKING | CHECK:  if tail AND length 
                # Move out of recursion into while loop for better control .. ie rr > rmax ?
                # if (path == tail and len(path) < eating)
     
                newpath = self.findLargestPath_step(step, snakes, turn, depth, path)
                
                allpaths.append(newpath)
                if (len(newpath) >= depth):
                    # Good path found - Exit search
                    # TODO: Benefit of checking all paths   
                    break

        # Return largest path .. 
        # DEBUG 
        # if step == [2, 1]:
        # print("FINDPATH", found, step, newpath, newturn, eating)
    
        if len(allpaths):
            a_sort = sorted(allpaths, key=len)
            newpath = a_sort[-1]

        # if len(newpath):
        return copy.copy(newpath), copy.copy(weight)

        # else:
        #     return [], CONST.routeThreshold


    def findLargestPath_step(self,
                             route,
                             snakes, 
                             turn=0,
                             depth=CONST.lookAheadPath,
                             path=[]):

        # If path meets depth, end recursion
        if (len(path) >= depth):
            return path

        start = copy.copy(route)
        pathnew = copy.copy(path)

        # Look in all directions
        for d in CONST.directions:

            step = list(map(add, start, CONST.directionMap[d]))

            # Check next path is in bounds. 
            # Probability of collision less than threshold 
            # available and not already visited**

            # OPTIMISE: Eating not checked -- too expensive
            # eating = self.findEating(snakes, path + [step], foods)
            if(self.isRoutePointv2(step, turn, path=path)):

                # Add to dirns
                turn = turn + 1
                path.append(copy.copy(step))
                pathnew = self.findLargestPath_step(step, snakes, turn, depth, path)

                # print("LARGEST STEP", str(pathnew), str(path), str(step))

            if (len(pathnew) > depth):
                break

        return copy.copy(pathnew)


# == FINDERS ==

    def getEnemyFuture(self, snakes, turns=2):

        sid_us = self.getIdentity()
        for sid in snakes:
                                    
            snake = snakes[sid]
            head = snake.getHead()
            paths = [] 

            enemy = False 
            if sid_us != snake.getId():
                enemy = True 
            
            for dirn in CONST.directions:
                # initial step in each direction 
                step = list(map(add, head, CONST.directionMap[dirn]))
        
                found = self.isRoutePointv2(step, 0, eating={}, path=[], enemy=enemy)
                # found = self.isRoutePointv2(step, 0, eating={}, path=[], enemy=enemy)
                if (found):    
                    paths.append(copy.copy([step]))

            # print("FUTURE", head, paths)

            for turn in range(0, turns - 1):
                # for N-1 turns look in each direction for each path
                paths_new = []
                for path in paths:             
                    for dirn in CONST.directions:
            
                        head_n = path[-1]                 
                        step = list(map(add, head_n, CONST.directionMap[dirn]))

                        # TODO: Eating - adjust for past / future eating .. 
                        # eating = self.findEating(snakes, path + [step], foods)   
                        found = self.isRoutePointv2(step, turn, path=path)
                        route = path + [step]
                        if (found):    
                            # New path found 
                            paths_new.append(copy.copy(route))

                # Concatenate new paths 
                paths = paths + paths_new

            # print("DEBUG SNAKE PATH", enemy, paths)
            # print("SNAKE", snake.getId(), paths)
            snake.setNextSteps(paths)


    def findClosestWall(self, start):

        ax = start[1]
        ay = start[0]

        w = self.width - 1
        h = self.height - 1
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
            r = self.leastWeightLine(start, walls)
            # print("B")

        # self.logger.log('route-findclosestwall', str(walls), r)
        return r

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

            enclosed[d] = copy.copy(encl)

        enclsum = {}
        # print("ENCLOSED", str(enclosed))
        for d in CONST.directions:
            # Return array of total spaces by direction (eg. up:10
            enclsum[d] = sum(sum(enclosed[d])) - 1
            # print(d, str(enclosed[d]))

        # self.logger.log('enclosed-sum', str(enclsum))
        return copy.copy(enclsum)


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

    def closestDist(self, us, them: list):
        # us = sn.getHead(), them = enemy.getHead()
        # TODO: Assumes no solids in closest distance, otherwise requires a version of route with dijkstra / gradient (ie. closestDist_complex)

        w = self.width
        h = self.height
        closest = np.zeros([w, h], np.intc)

        for y in range(0, h):
            for x in range(0, w):
                us_dist = abs(us[0] - y) + abs(us[1] - x)
                them_further = True

                for th in them:
                    them_dist = abs(y - th[0]) + abs(x - th[1])
                    if them_dist <= us_dist:
                        them_further = False

                if them_further:
                    closest[y, x] = 1

        return closest

    def findEmptySpace(self, point, path=[], turn=1):
        # Iterate through closed space to check volume

        s = self.trails

        dirns_avail = []

        for d in CONST.directions:

            dnext = list(map(add, point, CONST.directionMap[d]))
            dy = dnext[0]
            dx = dnext[1]

            # print("EMPTY SPACE", str(d), str(turn), str(s[dy, dx]), str(dnext), str(path))
            if(self.inBounds(dnext) and \
                    turn >= s[dy, dx] and \
                    not dnext in path):
                # Add to dirns
                dirns_avail.append(d)

        return dirns_avail

    def showMaps(self):
      
        # Routing maps
        # log('map', 'PREDICT', self.predict[0])
        # log('map', 'THREAT', self.threat[0])
        # log('map', 'SOLID', self.solid)
        # self.logger.maps('GRADIENT', self.gradient)
        self.logger.maps('LENGTH', self.bestLength)
        self.logger.maps('WEIGHT', self.bestWeight)
        
    
        self.logger.maps('TRAILS', self.trails)
        t = CONST.lookAheadEnemy - 1

        self.logger.maps('MARKOV0', self.markovs[0])
        
        # self.logger.maps('MARKOV1', self.markovs[1])
        # self.logger.maps('MARKOV2', self.markovs[2])
        self.logger.maps('MARKOV MAX', self.markovs[t])
        self.logger.maps('DIJKSTRA 0', self.dijkstra[0])
        # log('map', 'DIJKSTRA1', self.dijkstra[1])
        # log('map', 'DIJKSTRA2', self.dijkstra[2])
        #  t = CONST.lookAheadEnemy - 1
        # self.logger.maps('CHANCE', self.chance)
        
        # Visual maps
        self.logger.maps('COMBINE', self.combine)

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
