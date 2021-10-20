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

import sys

# Set recursion limit
# TODO: Replace with loop if possible ..
sys.setrecursionlimit(50000)


class board():

    ## == INIT ==

    legend = CONST.legend  # Import map values

    # distance = []  # Array of distance
    # you = []  # Array of snek (101-head, 100-body)
    # you_route = []  # Array of snek (minus head)

    # snakes = []  # Array of other snek (201-head, 200-body)
    # items = []  # Array of items (300-food, 301-hazard)

    # solid = []  # Array of all solids (snakes, walls)
    # combine = []  # Array of all layers (snakes, walls, items)
    # trails = []  # Array of all trails where N = time to expiry

    # gradient = []  # Array of gradient normalised to turn 0

    # gradients = {}  # List of previous gradients for future calc
    # 'cell':[turn,gradient]

    # enclosed = {}  # Dict of enclosed space volume by direction

    recursion_route = 0
    turn = 0

    def __init__(self, height=0, width=0):

        # globals
        # height = data['board']['height']
        # width = data['board']['width']
        self.identity = "" 
        self.height = height
        self.width = width

        self.land = np.zeros((height, width), np.intc)
        self.mask = np.ones((height, width), np.intc)

        # Routing limits
        self.maxdepth = CONST.maxSearchDepth

        self.startTime = time.time()
        self.win = 0
        self.loss = 0

        # self.threat = [None] * CONST.lookAhead
        # self.predict = [None] * CONST.lookAhead
        # self.gradient = [None] * CONST.maxPredictTurns

        self.dijkstra = [None] * CONST.lookAhead
        self.markovs = [None] * CONST.lookAhead



        self.hurry = False
        

    def resetCounters(self):
        # Reset start of each turn 
        self.turn = 0
        self.hurry = False
        self.recursion_route = 0
        # self.gradients = {}

# == GETTER / SETTER ==

    def setDimensions(self, x, y):
        if isinstance(x, int) and isinstance(y, int):
            self.width = x
            self.height = y
            self.land = np.zeros((x, y), np.intc)
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

    def setPoint(self, p: Dict[str, int], t="array"):
        try:
            if (t == "dict"):
                self.land[p["x"], p["y"]] = 1
                return True

            elif (t == "array"):
                self.land[p] = 1
                return True

        except:
            return False

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

    # Start time of every move
    def setStartTime(self):
        self.startTime = time.time()

    # Get start time of move -- used for logging
    def getStartTime(self):
        return self.startTime

# == BOARDS ==

    def updateBoards(self, data, snakes):
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

        # Update boards
        by = self.updateBoardYou(data)
        bs = self.updateBoardSnakes(data)
        bi = self.updateBoardItems(data)
        tr = self.updateTrails(snakes)

        # Combined boards
        rs = CONST.routeSolid
        self.solid = rs * np.ceil(by / (by + 1) + bs / (bs + 1))
        self.combine = by + bs + bi

        # Meta boards
        depth = CONST.lookAhead
        
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

    def updateBoardYou(self, data):
        # Array of snek (101-head, 100-body)
        w = self.width
        h = self.height
        self.you = np.zeros((h, w), np.intc)

        body = data['you']['body']
        for pt in body:
            px = pt['x']
            py = pt['y']
            self.you[py, px] = CONST.legend['you-body']

        try:
            head = data['you']['head']
            px_head = head['x']
            py_head = head['y']
            self.you[py_head, px_head] = CONST.legend['you-head']

        except Exception as e:
            log('exception', 'updateBoardsYou',
                'INFO: Your snake head not defined. ' + str(e))

        return self.you

    def updateBoardSnakes(self, data):
        # Array of snek (201-head, 200-body)
        w = self.width
        h = self.height
        self.snakes = np.zeros((h, w), np.intc)

        yid = data['you']['id']
        sks = data['board']['snakes']

        for sk in sks:
            # ignore my snake
            if (sk['id'] != yid):

                # print (str(sk))
                body = sk['body']
                for pt in body:
                    px = pt['x']
                    py = pt['y']
                    # self.snakes[h-py-1, px] = self.legend['enemy-body']
                    self.snakes[py, px] = CONST.legend['enemy-body']

                try:
                    head = sk['head']
                    px = head['x']
                    py = head['y']
                    # self.snakes[h-py-1, px] = self.legend['enemy-head']
                    self.snakes[py, px] = CONST.legend['enemy-head']

                except Exception as e:
                    log('exception', 'updateBoardSnakes', str(e))

        return self.snakes

    def updateBoardItems(self, data):
        # Array of items (300-food, 301-hazard)
        w = self.width
        h = self.height
        self.items = np.zeros((h, w), np.intc)

        fds = data['board']['food']
        hds = data['board']['hazards']

        for fd in fds:
            px = fd['x']
            py = fd['y']
            # self.items[h-py-1, px] = self.legend['food']
            self.items[py, px] = self.legend['food']

        for hd in hds:
            px = hd['x']
            py = hd['y']
            # self.items[h-py-1, px] = self.legend['hazard']
            self.items[py, px] = self.legend['hazard']

        return copy.copy(self.items)

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


    def updateMarkov(self, us, snakes:dict, foods:list, turns=CONST.lookAhead): 
          # TODO: Assumes no solids, otherwise requires a version of route with gradient = 1..
          w = self.width
          h = self.height
          
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
          for sn in snakes:
            for t in range(0, turns - 1): 

              markov = np.zeros([w, h], np.intc)
              for snid in snakes:
                  sn = snakes[snid]
                  # markov_sn = sn[identity].getMarkov()
                  markov_sn = sn.getMarkov(t)
                  markov = markov + markov_sn

              self.markovs[t] = copy.copy(markov)
          
          # self.markovs = copy.copy(markovs)
          

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
        if(snake.getType() == 'us'):
            # TODO: special logic for us 
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
        if (len(new_head)):
            new_body.insert(0, new_head)

        # Update body
        return new_body


    def updateMarkov_step(self, target, snakes:dict, foods:list, turn=1): 

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
            # TODO: special logic for us 
            pass
        else: 
            # Enemy snake  
            sides = CONST.directionSides[dirn] 
            i = 0
            for side in sides: 
              
              prob_pt = list(map(add, head, side))
              if (self.inBounds(prob_pt)):
                if(dirn == 'none'):
                  probability = 25           
                else:
                  if i == 0:
                    probability = 50 
                  else: 
                    probability = 25 
            
                current = markov[prob_pt[0], prob_pt[1]]
                if (current < 100):
                  markov[prob_pt[0], prob_pt[1]] = current + probability

              i = i + 1

        # # TODO:  Introduce logic based on other snakes  
        # for sn in snakes: 
        #   # Get heads .. 
        #   pass 

        # # TODO:  Introduce logic based on food  
        # for fo in foods:
        #   # Get
        #   pass  

        target.setMarkov(markov, turn)


    def updateDijkstra(self, sn):

        depth = CONST.lookAhead


        w = self.width
        h = self.height

        head = sn.getHead()
        tail = sn.getTail()
        length = sn.getLength()

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
                # Adjust head & tail location to zero for routing
                dijksmap[0][head[0], head[1]] = 0
                
                # Erase tail unless we are eating
                if (length > 3) and not sn.getEating():
                    dijksmap[0][tail[0], tail[1]] = 0
                
                
            except Exception as e:
                print('exception', 'updateDijkstra#1', str(e))

        self.dijkstra = copy.copy(dijksmap)


    def updateGradient(self, a, turn=0):

        # Max threshold
        rtmax = CONST.routeThreshold
        h = self.height
        w = self.width

        if (not self.recursion_route):
            # Initialise gradient -- MOVED TO SERVER.PY
            self.gradient = np.full([h, w], CONST.routeThreshold)
            self.gradient[a[0], a[1]] = 0

        # Max number of turns / boards in prediction matrix
        tmax = CONST.lookAhead - 1
        if (turn > tmax):
            turn = tmax

        dijkstra = self.getDijkstra()
        dt = dijkstra[turn]

        # Exit if timer or recursion exceeded
        rr = self.recursion_route
        self.recursion_route = rr + 1

        if (self.hurry or rr > CONST.maxRecursion):
            return

        if (rr > 0 and not (rr % 1000)):
            # TODO: Remove limit to N recursions 
            st = self.getStartTime()
            log('time', 'Gradient 1000', st)
            log('timer-hurry')
            
            # Timer exceeded
            diff = 1000 * (time.time() - st)
            if diff > CONST.timePanic:
                log('timer-hurry')
                self.hurry = True

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

        for snid in snakes:

            sn = snakes[snid]
            body = sn.getHeadBody()
            l = len(body)

            # If eating tail takes one more turn
            # if sn.getEating():
            #   l = l + 1

            # Mark each point
            for pt in body:
                trails[pt[0], pt[1]] = l
                # Descending from head = N to tail = 1
                l = l - 1

        self.trails = copy.copy(trails)
        return trails

    def pathProbability(self, head):
        # Calculates the probability assuming random walk from any location on the board (head), given obstacles (trails)
        # Returns probablility board (chance) from 0 - 100 (%)

        w = self.width
        h = self.height
        chance = np.zeros([w, h], np.intc)

        enclosed = self.enclosedSpacev2(head)
        dirn_avail = dict(filter(lambda elem: elem[1] > 0, enclosed.items()))

        # Calculate random walk probabiliy of each square
        for dirn in dirn_avail:
            path = [head]
            prob = 100 / len(dirn_avail)
            turn = 1
            step = list(map(add, head, CONST.directionMap[dirn]))
            self.pathProbability_step(chance, path, prob, step, turn)

        # dirn_avail.remove(dirn)
        # print(str(dirn_avail))

        return chance

    def pathProbability_step(self, chance, path, prob, step, turn=1):

        # print("PATH PROBABILITY" + str(step))
        dy = int(step[0])
        dx = int(step[1])
        s = self.trails

        # Check if not blocked
        if (turn >= s[dy, dx]):

            # Add to enclosure
            chance[dy, dx] = chance[dy, dx] + prob
            dirn_avail = self.findEmptySpace(path, step, turn + 1)
            path.append(step)

            # print("PATH PROB", str(turn), str(step), str(dirn_avail))

            for d in dirn_avail:

                dnext = list(map(add, step, CONST.directionMap[d]))
                # dny = dnext[0]
                # dnx = dnext[1]

                # Reduces based on # directions
                prob = prob * 1 / len(dirn_avail)

                # If point is in map & prob > threshold to prevent loop
                if (self.inBounds(dnext) and prob > 5):
                    # Recursive
                    turn = turn + 1

                    # print("PATH PROB STEP", str(path), str(prob), str(dnext), str(turn))
                    chance = self.pathProbability_step(chance, path, prob,
                                                       dnext, turn)

        else:
            pass

        return chance

# == ROUTING ==

# TODO: Fuzzy Routing, ie. get close to an object)

    def fuzzyRoute(self, start, targetmap, length):
        # Send shape - return best path to any point in shape
        # a = [1, 1]
        # b = np.zeros([h, w], np.intc)
        # b[1:3, 3:6] = 1
        # result, weight = fuzzyRoute(a, b)
        w = self.width
        h = self.height
        
        a = copy.copy(start)
        b = copy.copy(targetmap)
        l = copy.copy(length)

        r = np.zeros([h, w], np.intc)
        r = r + b
        r[a[0], a[1]] = 1

        targets = np.nonzero(b > 0)
        rt = []
        wmin = CONST.routeThreshold
        # Iterate through potential targets
        for i in range(0, len(targets[0] - 1)):
            t = [targets[0][i], targets[1][i]]
            try:
                r, w = self.route(a, t, l)
                if w < wmin:
                    rt = r
            except Exception as e:
                log('exception', 'fuzzyRoute', str(e))
                pass

        return rt, wmin


    def route(self, start, dest, length=0, threshold = CONST.routeThreshold):

        a = copy.copy(start)
        b = copy.copy(dest)

        route = []
        weight = -1
        routetype = ''

        log('route-fromto', a, b)
        # log('time', 'Route', self.getStartTime())

        # If start / finish not defined, return blank
        if (not len(a) or not len(b) or a == b):
            routetype = 'route_error'
            return route, weight

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
            route, weight = self.route_complex(a, b, length)
            if len(route):
                routetype = 'route_complex'
                break

            else:
                routetype = 'route_none'
                break

        # Return sorted path/points or [] if no path
        log('route', routetype, route, weight)
        return route, weight

    def route_basic(self, a, b):

        r = []
        w = CONST.routeThreshold

        if (a[0] == b[0]) or (a[1] == b[1]):
            # Get points in line & measure route
            path = fn.getPointsInLine(a, b)
            w, pmax = self.dijkstraPath(path)
            # If weight less than threshold, and not deadend
            if (w < CONST.routeThreshold) and (pmax < CONST.pointThreshold):
                # Return path
                r = [b]

        # log("route", "BASIC", str(r), str(w))
        return r, w

    def route_corner(self, a, b, w = CONST.routeThreshold):

        r = []
        corners = [[a[0], b[1]], [b[0], a[1]]]

        # Calculate path routes for two options all the individual legs
        for c in corners:
            path = []
            path = fn.getPointsInLine(a, c) + fn.getPointsInLine(c, b)
            csum, pmax = self.dijkstraPath(path)
            if csum < w:
                w = csum
                r = c
                log('route-dijkstra-sum', str(a), str(c), str(b), str(path),
                    csum)

        # Check if path exceeds probability thresholds
        if (csum < CONST.routeThreshold) and (pmax < CONST.pointThreshold):
            return [r, b], w
        else:
            return [], CONST.routeThreshold

    def route_complex(self, a, b, length=0):
        # Returns path or point. [] if no path or error
        # TODO def route_complex(self, a, b, c, response='path'|'weight'):
        # TODO: Optimise. Save previous dijkstra calcs to optimise.. eg.

        h = self.height
        w = self.width
        if (not self.inBounds(a) or not self.inBounds(b)):
            return [], CONST.routeThreshold

        # Gradient to destination
        weight = self.gradient[b[0], b[1]]
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
                r, grad = self.route_complex_step(bnew, a)

                # No path found / error or dead end
                # If deadend, abandon route
                move = fn.translateDirection(bnew, r)
                if (not len(r) or length > self.enclosed[move]):
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
                        self.gradient[burn[0], burn[1]] = CONST.routeThreshold
                        # Reset variables
                        path = []
                        bnew = copy.copy(b)
                        pathlength = 0

        # log("route", "COMPLEX", str(path), str(weight))

        return path, weight

    def route_complex_step(self, a, b, t=0):
        # Return next point in complex path based on least weight. [] if no path or error
        log('route-complex-step', a, b)

        # Define walls
        gmin = CONST.pointThreshold
        c = []

        # Look in each direction
        for d in CONST.directions:
            a1 = list(map(add, a, CONST.directionMap[d]))

            # Check direction is in bounds
            if (self.inBounds(a1)):
                g1 = self.gradient[a1[0], a1[1]]

                # Find the minimum gradient & update next step
                if (g1 < gmin):
                    gmin = g1
                    c = a1

                # End found -- terminate process
                if (a1 == b):
                    break

        return c, gmin

    def dijkstraPath(self, path, turn=0):
        # Sum dijkstra map between two points
        tmax = CONST.lookAhead - 1

        result = 0

        # Capture largest increment (probability of collision)  
        largest_point = 0
        
        # Iterate through path
        dt = self.getDijkstra()

        for p in path:
            if self.inBounds(p):
                # Check which prediction matrix to use
                if (turn > tmax):
                    turn = tmax

                # Add dijkstra value
                increment = int(dt[0][p[0], p[1]])
                result = result + increment
                turn = turn + 1
                if (increment > largest_point):
                  largest_point = increment 

        return copy.copy(result), copy.copy(largest_point)


    def routePadding(self, route, depth=CONST.lookAhead):
        # Make sure there is always a path with N moves (eg. route_complex + random walk)
        # Else return []

        path = []
        found = False

        # Needs minimum one point to start padding route
        if (not len(route)):
            return path, found

        # Convert vectors to points
        if (len(route) > 1):
            path = fn.getPointsInRoute(route)

        turns_found = len(path)
        # start = route[-1]

        # TODO:  Increase depth as snake increases rather than fixed amount
        # CONFIRM:  If no path == depth, return max lenght
        # depth = sn.getLength() * 2

        # Confirm we have a path
        if (turns_found):
            # Confirm any path exists.  Pad path to N turns using random walk
            turn = len(path)
            print("ROUTE PAD#1", str(path))
            original = copy.copy(path)
            path = self.findLargestPath(original, turn, depth)
            if len(path) >= depth:
                # Max path found
                found = True

            print("ROUTE PAD#2", str(path), str(len(path)), str(depth))

        # Return path (list) & wheth max depth found (boolean)
        # route = route + path
        # Remove first point of route (head)
        route.pop(0)
        return copy.copy(route), copy.copy(found)

    def findLargestPath(self, route, turn=1, depth=CONST.lookAhead):
        # Iterate through closed space to check volume
        # **TODO: Include own path as layer in future updateTrails
        # TODO: Introduce panic timers if routing too long
        # TODO: Introduce threat from other snakes into s[dy, dx] -> s[turn][dy, dx] udating predict matrix
        # TODO:  Return best path vs any path (similar to introducing snake threat)

        # print("FINDPATH", str(path), str(turn))
        if (len(route)):
            start = copy.copy(route[-1])

        else:
            return []

        s = copy.copy(self.trails)

        # Look in all directions
        for d in CONST.directions:
            newturn = copy.copy(turn)
            step = list(map(add, start, CONST.directionMap[d]))
            path = copy.copy(route)
            newpath = []
            dy = step[0]
            dx = step[1]
            
            # Get future markov matrix 
            turn_max = min(CONST.lookAhead - 1, turn)
            markov = copy.copy(self.markovs[turn_max])
            # Check next path is in bounds, available and not already visited**
            if(self.inBounds(step) and \
                    turn >= s[dy, dx] and 
                    markov[dy, dx] < CONST.pointThreshold):

                newturn = newturn + 1

                path.append(step)
                newpath = self.findLargestPath_step(step, turn, depth, path)

                if (len(newpath) >= depth):
                    # Max path found - Exit search
                    break

        if len(newpath):
          return copy.copy(newpath)

        else:
          return []

    def findLargestPath_step(self,
                             route,
                             turn=1,
                             depth=CONST.lookAhead,
                             path=[]):

        # If path meets depth, end recursion
        if (len(path) >= depth):
            return path

        start = copy.copy(route)
        pathnew = copy.copy(path)

        # Basic route table
        s = copy.copy(self.trails)

        # Look in all directions
        for d in CONST.directions:

            step = list(map(add, start, CONST.directionMap[d]))
            dy = step[0]
            dx = step[1]

            # Check next path is in bounds, available and not already visited**
            if(self.inBounds(step) and \
                    turn >= s[dy, dx] and \
                    not step in path):

                # Add to dirns
                turn = turn + 1
                path.append(copy.copy(step))
                pathnew = self.findLargestPath_step(step, turn, depth, path)

                # print("LARGEST STEP", str(pathnew), str(path), str(step))

            if (len(pathnew) > depth):
                break

        return copy.copy(pathnew)

# == FINDERS ==

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

        log('route-findclosestwall', str(walls), r)
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

    def getPoint(self, p: Dict[str, int], t="array"):
        try:
            if (t == "dict"):
                return self.land[p["x"], p["y"]]

            elif (t == "array"):
                return self.land[p]

        except:
            return []

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

        # print(str(labels))
        # print(str(si))
        # print(str(fi))
        # print(str(hi))

        return 1

    def leastWeightLine(self, a, points):
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

        log('route-leastline-dsum', str(points), str(a), str(r), best)

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

        # TODO: Assess where else this is used (optimise).  Save to snake (setEnclose/getEnclose), ie. self.enclosed
        # self.enclosed = copy.copy(enclsum)

        log('enclosed-sum', str(enclsum))
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

    def findEmptySpace(self, path, dirn, turn=1):
        # Iterate through closed space to check volume

        s = self.trails

        dirns_avail = []

        for d in CONST.directions:

            dnext = list(map(add, dirn, CONST.directionMap[d]))
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
        log('map', 'GRADIENT', self.gradient)
        log('map', 'TRAILS', self.trails)
        log('map', 'MARKOV0', self.markovs[0])
        log('map', 'MARKOV1', self.markovs[1])
        log('map', 'MARKOV2', self.markovs[2])
        log('map', 'DIJKSTRA0', self.dijkstra[0])
        # Visual maps
        log('map', 'COMBINE', self.combine)




bo = board()
start = [2, 2]
finish = [4, 4]
path = fn.getPointsInRoute([start, finish]) 

# == 

data = {'game': {'id': '609d47ca-e773-49f9-b3f4-2c52afa4a05c', 'ruleset': {'name': 'solo', 'version': 'v1.0.22', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'royale': {'shrinkEveryNTurns': 0}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'timeout': 500, 'source': ''}, 'turn': 4, 'board': {'height': 11, 'width': 11, 'snakes': [{'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}], 'food': [{'x': 2, 'y': 6}, {'x': 5, 'y': 5}], 'hazards': []}, 'you': {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}}

foods = data['board']['food']
# food_lastturn = copy.copy(theFoods)
theFoods = []
for f in foods:
  food = [f['y'], f['x']]
  theFoods.append(food)

# Refresh enemy snakes. Remove dead sneks
snakes = data['board']['snakes']
ourSnek.setAll(data['you'])
        
    aliveSnakes = {}
    for alive in snakes:
      identity = alive['id']
      if (identity == ourSnek.getId()):
        # We are alive! 
        aliveSnakes[identity] = ourSnek
    
      else:
        try: 
          # Enemy snake alive 
          aliveSnakes[identity] = allSnakes[identity]
          aliveSnakes[identity].setEnemy(alive)
          
        except Exception as e:
          # Create new snake -- shouldn't happen .. 
          log('exception','handle_move',str(e))
          sn = snake() 
          sn.setEnemy(alive)
          aliveSnakes[identity] = copy.deepcopy(sn)
    
    allSnakes = aliveSnakes
    
    # Update predict & threat matrix  
    hazards = data['board']['hazards']
    theBoard.updateBoards(data, allSnakes)
us.
them = 
snakes = 
bo.updateMarkov(us, snakes, foods)
bo.updateDijkstra(us)
bo.updateGradient(us.getHead()) 
bo.updateGradientFix(ourSnek.getHead())

route = bo.findLargestPath(path)
print(route)

route = bo.route(start, finish)
print(route)


print("ROUTE", route)
print(str(bo.trails))