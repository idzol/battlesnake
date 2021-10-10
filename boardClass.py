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


class board():

    # Import map values
    legend = CONST.legend

    identity = ""   # Identity of your snake 

    # board matrices
    land = []
    mask = []

    distance = []      # Array of distance
    you = []           # Array of snek (101-head, 100-body)
    you_route = []     # Array of snek (minus head)

    snakes = []         # Array of other snek (201-head, 200-body)
    items = []          # Array of items (300-food, 301-hazard)

    solid = []  # Array of all solids (snakes, walls)
    combine = []  # Array of all layers (snakes, walls, items)

    predict = []    # List of Array of board in n moves (prediction)
    threat = []     # List of Array of threat rating
    dijkstra = []   # List of Array of route complexity 

    gradient = []   # Array of gradient normalised to turn 0 

    # gradients = {}  # List of previous gradients for future calc
                    # 'cell':[turn,gradient]
   
    enclosed = {}   # Dict of enclosed space volume by direction 

    recursion_route = 0
    turn = 0

    def __init__(self, height=0, width=0):

        # globals
        # height = data['board']['height']
        # width = data['board']['width']

        self.height = height
        self.width = width

        self.land = np.zeros((height, width), np.intc)
        self.mask = np.ones((height, width), np.intc)

        # Routing limits
        self.maxdepth = CONST.maxSearchDepth
        
        self.startTime = time.time()
        self.win = 0
        self.loss = 0

        self.threat = [None] * CONST.maxPredictTurns
        self.predict = [None] * CONST.maxPredictTurns
        self.dijkstra = [None] * CONST.maxPredictTurns
        # self.gradient = [None] * CONST.maxPredictTurns

        self.hurry = False

    def resetCounters(self):
        self.turn = 0
        self.hurry = False
        self.recursion_route = 0
        # self.gradients = {}

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

    def getPoint(self, p: Dict[str, int], t="array"):
        try:
            if (t == "dict"):
                return self.land[p["x"], p["y"]]

            elif (t == "array"):
                return self.land[p]

        except:
            return []

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

    # DEPRECATE
    # def setMaxDepth(self, d):
    #     self.maxdepth = d

    # DEPRECATE
    # def getMaxDepth(self):
    #     return self.maxdepth

    def getTurn(self):
        t = self.turn
        return copy.copy(t)

    def setTurn(self, t):
        self.turn = t

    def updateBoards(self, data):
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

        # Combined boards
        rs = CONST.routeSolid
        self.solid = rs * np.ceil(by / (by + 1) + bs / (bs + 1))
        self.combine = by + bs + bi  
        
        # Meta Boards 
        depth = CONST.maxPredictTurns
        en = self.enclosedSpace(head)
        
        threat = []
        dijkstra = []
        for t in range(0, depth):
          threat.append(np.zeros([height, width], np.intc))
          dijkstra.append(np.zeros([height, width], np.intc))
          # self.updateGradient() -- only update when rqd for routing
        
        self.threat = threat
        self.dijkstra = dijkstra

        # Other meta-boards
        # bt = self.updateThreat(data, snakes) -- needs snakes 
        # di = self.updateDijkstra(fn.XYToLoc(data['you']['head']))
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
            print("INFO: Your snake head not defined. " + str(e))

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
                    log('updateboardsnakes-warn', str(e))

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

    def updateThreat(self, snakes, hazards):
    # Assign "threat" value based on prediction model, distance to enemy snake and size etc..
        w = self.width
        h = self.height
        
        full = CONST.routeSolid
        depth = CONST.maxPredictTurns
        
        threatmap = [None] * (depth + 1)
        for t in range(0, depth):
            threatmap[t] = np.zeros([w, h], np.intc)

        # log("predict-update")
        you_len = 10

        # Get our head
        for identity in snakes:
            sn = snakes[identity]
            if (sn.getType() == "us"):
                you_len = sn.getLength()

        # Optional: Stay away from four corners
        if(False):
            threatmap[:][0, 0] = full / 4
            threatmap[:][0, w-1] = full / 4
            threatmap[:][h-1, 0] = full / 4
            threatmap[:][h-1, w-1] = full / 4
      
        # Update hazard board 
        for hz in hazards: 
            try:
              threatmap[:][hz['y'], hz['x']] = CONST.routeHazard 
            except Exception as e: 
              log('exception', 'updateThreat', str(e))

        # Head on collisions 
        for identity in snakes:
            if (sn.getType() != "us"):
              
                # s = np.zeros([h, w], np.intc)
                # Death zone (+) around larger snakes
                length = sn.getLength()
                head = sn.getHead()
                lasthead = copy.copy(head)
                path = sn.getPath()
        
                for t in range(0, depth - 1): 
                
                  if (len(path)):
                    # Use next path as head 
                    head = path.pop(0)
                    if (not len(head)):
                      # If point is blank
                      head = lasthead 

                  else: 
                    # Use original / last head 
                    pass 

                  # print("SNAKE LENGTH")
                  # print(str(length),str(you_len))
                  if length >= you_len:
                      ay = head[0]
                      ax = head[1]
                      ay1 = max(0, ay - 1)
                      ay2 = min(h, ay + 2)
                      ax1 = max(0, ax - 1)
                      ax2 = min(w, ax + 2)

                      # Update threat matrix used for routing
                      threatmap[t][ay1:ay2, ax] = threatmap[t][ay1:ay2, ax] + full / 2
                      threatmap[t][ay, ax1:ax2] = threatmap[t][ay, ax1:ax2] + full / 2 
                  
                  lasthead = head

        self.threat = copy.copy(threatmap) 
        log('map','THREAT',self.threat)
        

    def updateDijkstra(self, data_you):

        depth = CONST.maxPredictTurns

        w = self.width
        h = self.height

        ay = data_you[0]
        ax = data_you[1]

        # TODO: Check self.predict[0] is the same as self.solid 
        # TODO: determine if we need to zero start loc
        # TODO:  Make sure predict/threat[t] exist & are non-zero 

        log('map', 'SOLID COMPARE', str(self.solid))
        log('map', 'PREDICT[0] COMPARE', str(self.predict[0]))
        
        dijksmap = [None] * (depth + 1)
          
        for t in range(0, depth):
            dijksmap[t] = np.zeros([h, w], np.intc)

        ones = CONST.routeCell * np.ones((w, h), np.intc)

        for t in range(0, depth):
          # Get relevant predict / threat matrix 
          predict = self.predict[t]
          threat = self.threat[t]
          
          # Dijkstra combines solids, foods, hazards (threats)
          dijksmap[t] = predict + threat + ones
          # Adjust head location to zero - not rqd for routin (alerady here)
          dijksmap[0][ay, ax] = 0
          # dijksmap[0][ay, ax] = threat[0][ay, ax]
          
        # log('map','DIJKSTRA', self.dijkstra)
        self.dijkstra = copy.copy(dijksmap)
        return copy.copy(self.dijkstra)


    # Give every item unique index ..
    def assignIndices(self, sn, it):

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

        print(str(labels))
        print(str(si))
        print(str(fi))
        print(str(hi))

        return 1

    def calculateDistances(self, snakes, items):

        n = len(snakes) + len(items)
        dists = np.zeros((n, n), np.intc)

        things = snakes
        things = things.append(items)

        for t1 in range(0, things):
            for t2 in range(0, things):
                t1loc = things[t1].getLocation()
                t2loc = things[t2].getLocation()
                d = fn.calculateDistance(t1loc, t2loc)
                dists[t1, t2] = d

        self.distances = dists

        print(str(dists))

        return dists
        # eg.
        # [ 0, 5, 9, 3, 6 ]  - you to you,s1,s2,f1,h1
        # [ 5, 0, 3, 2, 1 ]  - s1 to you,s1,s2,f1,h1
        # [ 9, 3, 0, 4, 2 ]

    # Go through snakes and estimate most likely path
    def predictSnakeMoves(self, snakes, items):
      
        for identity in snakes:
            # Iterate through dict (id:snake)
            sn = snakes[identity]
            if (sn.getType() == "us"):
                # Path loaded after route()
                # Use previous route or update afterwards?
                # sn.get/setRoute()
                pass

            else:
                # Assume strategy is food
                start = sn.getHead()
                its = self.findClosestItem(items, start)  # ??
                finish = its.pop(0).getLocation()
                rt, weight = self.route(start, finish)
                # Limit depth to X

                # TODO: Assume strategy is kill (len > X)
                # TODO: Assume strategy is board control / loop etc (eg. circular)
                print("SNAKE HEAD", str(start))
                sn.setRoute(rt)
                sn.setPath(rt)
              

    def updatePredict(self, snakes):
        # Update the prediction board
        # p - predict matrix
        # t - turn
        # r1 - point
        # val - gradient / path weight
        
        w = self.width
        h = self.height
        p = self.predict
        depth = CONST.maxPredictTurns
        full = CONST.routeSolid

        # log("predict-update")
        you_head = [-1, -1]

        # Get our head
        for identity in snakes:
            sn = snakes[identity]
            if (sn.getType() == "us"):
                you_head = sn.getHead()
                
        # Iterate through next t turns
        for identity in snakes:
            sn = snakes[identity]

            # Get head, body & predicted route
            name = sn.getType()
            head = sn.getHead()
            body = sn.getBody()
            vector = sn.getRoute()
            # TODO:  Check to convert route to points (if not already).
            vector.insert(0, head)
            rt = fn.getPointsInRoute(vector)

            # print("PREDICT ROUTE", str(name), str(rt))
            
            body.insert(0, head)

            # Ignore dead or invalid snakes
            if (head == [-1, -1]):
                break

            # Create blank template
            snakemap = [None] * (depth + 1)

            for t in range(0, depth):
                snakemap[t] = np.zeros([w, h], np.intc)

            # Paint body
            snakemap[0][head[0], head[1]] = full
            for r1 in body:
                snakemap[0][r1[0], r1[1]] = full

            # Go through next t moves
            for t in range(1, depth):
                # Copy template from last move
                snakemap[t] = copy.copy(snakemap[t - 1])
                # Prediction values for partial or full matches
                if (name == "us"):
                    val_predict = full
                    val_certain = full
                else:
                    val_predict = int(full * (depth - t) / depth)
                    val_certain = full

                try:
                    if (name != "us"):
                        if (len(rt)):
                          # Get next move from route
                          r1 = rt.pop(0)

                        else:
                          # Continue moving in current direction 
                          diff = CONST.directionMap[sn.getDirection()]
                          head = self.moveBy(head, diff)
                          r1 = copy.copy(head)

                        # Add to prediction matrix 
                        snakemap[t][r1[0], r1[1]] = p[t][r1[0], r1[1]] + val_predict
                        # Add route to head of body
                        body.insert(0, r1)
                        log('predict-new', str(t), str(rt), str(r1))
                      
                except Exception as e:
                    # end of route
                    log('exception','updatePredict#1', str(e))
                    pass

                # Erase tail (last point in body)
                try:
                    # Remove tail
                    b1 = body.pop(-1)
                    # Update the prediction board
                    snakemap[t][b1[0], b1[1]] = snakemap[t][b1[0],
                                                     b1[1]] - val_certain
                    log('predict-erase', str(t), str(body), str(b1))

                except Exception as e:
                    # end of body
                    log('exception','updatePredict#2', str(e))
                    pass

            # Update predict matrix for snake 
            sn.setPredict(snakemap)

        # Sum all snakes into final prediction matrix
        p = [None] * (depth + 1)
        for t in range(0, depth):
            p[t] = np.zeros([w, h], np.intc)

            for identity in snakes:
                psnake = snakes[identity].getPredict()
                p[t] = p[t] + psnake[t]

        for pmap in p:
            # print("PREDICT")
            log('map-debug', 'PREDICT', pmap)

        self.predict = p
        return p

    # Return future predict matrix
    def getPredictMatrix(self, t):
        return self.predict[t]

    # TODO: work in progress
    # Check for collision in x rounds time
    def predictCollisionFuture(bo, route):
        # for r in route:
        #   i = i + 1
        #   board = predict[i]
        #   checkCollision(board, r)
        # return coll
        pass

    # TODO: Fuzzy Routing, ie. get close to an object)
    # def fuzzyroute(a, blist): 
        # log('time', 'Before Complex Route', self.getStartTime())
        # r = self.route_complex(a, b)
        # r, w = self.route_complex(a, b)
        # weight = w
        # print('WEIGHT 3')
        # print(str(Weight))
        # return []


    def route(self, a, b, length=0):
        # TODO: Split into routeBasic, routeVector, routeComplex... 

        t = CONST.routeThreshold
        r = []
        weight = -1

        # TODO: if (not len(a) or not len(b)):
        #   no valid route requested.
        #   try / except
        log('route-fromto', a, b)
        log('map', 'SOLID', self.solid)
        # If start / finish not defined, return blank
        if (not len(a) or not len(b)):
            return r, weight 

        # try simple, medium, complex route
        while 1:
            # (1) Simple straight line (a->b)
            log('time', 'Before Basic Route', self.getStartTime())
            if (a[0] == b[0]) or (a[1] == b[1]):
                # Get points in line & measure route 
                path = fn.getPointsInLine(a, b)
                move = fn.translateDirection(a, b)              
                weight = self.dijkstraPath(path)
                # If weight less than threshold, and not deadend 
                if (weight < t and length < self.enclosed[move]):
                    # Return path 
                    log('route-basic', weight)
                    r = [b]
                    break

            # (2) Simple dog leg (a->c->b)
            # TODO: Split into function.  Inverted c1 & c2 to fix -- work out why?  Optimise code 

            log('time', 'Before Medium Route', self.getStartTime())
            c2 = [b[0], a[1]]
            c1 = [a[0], b[1]]
            
            # Calculate all the individual legs 
            path = fn.getPointsInLine(a, c1)            
            weight_a_c1 = self.dijkstraPath(path)
            
            path = fn.getPointsInLine(c1, b)            
            weight_c1_b = self.dijkstraPath(path)
            
            path = fn.getPointsInLine(a, c2)            
            weight_a_c2 = self.dijkstraPath(path)
            
            path = fn.getPointsInLine(c2, b)            
            weight_c2_b = self.dijkstraPath(path)

            # Sum the path routes 
            c1sum = weight_a_c1 + weight_c1_b
            c2sum = weight_a_c2 + weight_c2_b
            
            log('route-dijkstra-sum', str(a), str(c1), str(b), c1sum)
            log('route-dijkstra-sum', str(a), str(c2), str(b), c2sum)

            # See if path exists & less than threshold 
            if (c1sum <= c2sum) and (c1sum < t):
                # CHeck not dead end 
                move = fn.translateDirection(a, c1)             
                if (length < self.enclosed[move]):
                  r = [c1, b]
                  weight = c1sum
                  break

            elif (c2sum <= c1sum) and (c2sum < t):
                # Check not dead end 
                move = fn.translateDirection(a, c2)             
                if (length < self.enclosed[move]):
                  r = [c2, b]
                  weight = c2sum
                  break

            # print('WEIGHT 2')
            # print(str(c1sum), str(c2sum))

            # (3) Complex route
            log('time', 'Before Complex Route', self.getStartTime())

            r, weight = self.route_complex(a, b, length)
            # r, w = self.route_complex(a, b)
            # weight = w
            # print('WEIGHT 3')
            # print(str(Weight))

            break

        # Return next path/point or [] if no path

        # TODO:  Separate basic/medium/complex route into separate functions so they can be reused ..

        log('route-return', r)
        # fn.printMap(self.dijkstra)
        log('map', 'COMBINE', self.combine)
        
        return r, weight


    def route_complex(self, a, b, length=0):
        # Returns path or point. [] if no path or error
        # TODO def route_complex(self, a, b, c, response='path'|'weight'):
        
        h = self.height
        w = self.width

      # TODO: Optimise. Save previous dijkstra calcs to optimise 
        # Save gradient for future turns to optimise search time
        # self.gradients[str(a)] = [turn, copy.copy(self.gradient)]
        # if (time < timethreshold):
        #   update gradient
        # else:
        #   use existing gradient
        
        self.gradient = np.full([h, w], CONST.routeThreshold)
        log('time', 'Before Gradient', self.getStartTime())

        self.updateGradient(a)
        log('time', 'Updated Gradient', self.getStartTime())
        # log('map', 'GRADIENT', str(self.gradient))

        # Gradient to destination 
        weight = self.gradient[b[0], b[1]]
        if (weight > CONST.routeThreshold):
            # no path
            return [], -1

        else:
            # Recurse until destination reached or path exceeds num points
            path = []
            pathlength = 1
            bnew = copy.copy(b)

            while 1:
                # find lowest gradient route & add to path
                r, grad = self.route_complex_step(bnew, a)
               
                # No path found / error or dead end 
                # If deadend.. abandon route 
                move = fn.translateDirection(a, r)  
                if (not len(r) or length > self.enclosed[move]):
                    path = []
                    weight = CONST.routeThreshold
                    break

                # Otherwise insert to path
                # path.insert(0, r)
                path.append(r)

                # Break once reaching destination or at board limit
                if (r == b) or (pathlength > h * w):
                    break

                # Last step becomes first step for next iteration
                bnew = copy.copy(r)
                pathlength = pathlength + 1

        log('map','GRADIENT',self.gradient)

        log('route-complex-path', str(path))
        return path, weight


    def route_complex_step(self, a, b, t=0):
        # Return next point. [] if no path or error

        log('route-complex-step', a, b)
        # set up directions to check for
        # TODO: Replace with CONST.directions, directionMap
        directions = [[a[0] + 1, a[1]], [a[0] - 1, a[1]], [a[0], a[1] + 1], [a[0], a[1] - 1]]

        # Define walls
        gmin = CONST.routeThreshold
        c = []

        # Look in each direction
        for a1 in directions:

            # Check direction is in bounds
            if (self.inBounds(a1)):
                g1 = self.gradient[a1[0], a1[1]]

                # Find the minimum gradient & update next step
                if (g1 < gmin):
                    gmin = g1
                    c = a1

        return c, gmin


    def getEdges():
        # Return all border / edge cells of the map
        global h
        global w

        edges = []
        edges = edges + fn.getPointsInLine([0,0], [0,w]) + \
                    fn.getPointsInLine([w,0], [h,w]) + \
                    fn.getPointsInLine([h,w], [h,0]) + \
                    fn.getPointsInLine([h,0], [0,0])

        return edges

    def inBounds(self, a):
        # Check a point (a = [y,x]) is in map bounds
        h = self.height
        w = self.width

        if (0 <= a[0] < h) and (0 <= a[1] < w):
            return True
        else:
            return False


    def updateGradient(self, b, turn=0):

        # Check which prediction matrix to use   
        tmax = CONST.maxPredictTurns - 1
        if(turn > tmax): 
          turn = tmax
        dt = self.dijkstra[turn]
        
        # Exit if timer or recursion exceeded
        rr = self.recursion_route
        self.recursion_route = rr + 1
        if (self.hurry or rr > CONST.maxRecursion):
            return

        if (rr > 0 and not (rr % 1000)):
            st = self.getStartTime()
            log('time', 'Gradient 1000', st)

            # Timer exceeded
            diff = 1000 * (time.time() - st)
            if diff > CONST.timePanic:
                log('timer-hurry')
                self.hurry = True

        rtmax = CONST.routeThreshold
        h = self.height
        w = self.width

        directions = [[b[0] + 1, b[1]], [b[0] - 1, b[1]], [b[0], b[1] + 1],
                      [b[0], b[1] - 1]]

        for b1 in directions:
            # Check in bounds           
            if (0 <= b1[0] < h) and (0 <= b1[1] < w):
            
                g0 = self.gradient[b[0], b[1]]
                g1 = self.gradient[b1[0], b1[1]]
                d1 = dt[b1[0], b1[1]]
                # d1dist = fn.getDistance(a1, b1)
                # d1 = self.dijkstra[d1dist[]][b1[0], b1[1]]

                # Check path is less than route threshold and cheaper than last 
                if ((d1 < rtmax) and (g0 + d1) < g1):

                    # Gradient can't handle negatives
                    if (d1 < 0):
                        d1 = 0

                    # Update point
                    self.gradient[b1[0], b1[1]] = g0 + d1

                    # Recursion
                    # Check which prediction matrix to use based on number of turns (t)
                    turn = turn + 1 
                    self.updateGradient(b1, turn)

  
    def dijkstraPath(self, path, turn=0):
        # Sum dijkstra map between two points
        tmax = CONST.maxPredictTurns - 1
        
        result = 0 
        # Iterate through path
        for p in path: 
            if self.inBounds(p):
              # Check which prediction matrix to use 
              if(turn > tmax): 
                turn = tmax 
              
              # print("DIJKSTRA PREDICT LEN", len(self.dijkstra), turn)
              dt = self.dijkstra[turn]
              turn = turn + 1 

              # Add dijkstra value 
              result = result + dt[p[0], p[1]]
              
        else:
          pass 

        # log('map', 'DIJSUM', str(dt))
        return result



    # def dijkstraSum(self, a, b, turn=0):
    #     # Sum dijkstra map between two points
    #     # TODO:  Update to use predict[t] ... currently based off dijkstra[0] 
        
    #     maxpath = CONST.routeThreshold

    #     # Check which prediction matrix to use 
    #     tmax = CONST.maxPredictTurns
    #     if(turn > tmax): 
    #       turn = tmax
    #     dt = self.dijkstra[turn]

    #     # log('map', 'DIJSUM', str(dt))
        
    #     try:
    #         # TODO: Simplify by sorting a, b for array search ..

    #         # Check whether horizontal or vertical route
    #         if (a[0] == b[0] and a[1] != b[1]):
    #             # Get correct ordering for array sum 
    #             if (a[1] < b[1]):
    #                 result = sum(dt[a[0], a[1]:b[1] + 1])
    #                 # print('RESULT1:', str(a), str(b), str(result))
    #             else:
    #                 result = sum(dt[a[0], b[1]:a[1] + 1])
    #                 # print('RESULT2:', str(a), str(b), str(result))

    #         elif (a[1] == b[1] and a[0] != b[0]):
    #             if (a[0] < b[0]):
    #                 result = sum(dt[a[0]:b[0] + 1, a[1]])
    #                 # print('RESULT3:', str(a), str(b), str(result))
    #             else:
    #                 result = sum(dt[b[0]:a[0] + 1, a[1]])
    #                 # print('RESULT4:', str(a), str(b), str(result))

    #         else:
    #             # Cannot be reached by 
    #             result = maxpath + 1

    #     except:
    #         result = maxpath + 1

    #     return result

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
        


    def findClosestNESW(self, start):
        # TODO: Lowest threat or highest control
        # TODO: Where are other snakes (getQuadrant/SideBy)  
        w = self.width
        h = self.height

        cardinals = [[0,int(w/2)],
                      [int(h/2),0],
                      [int(h/2), w],
                      [h, int(w/2)]]
        
        pt = []
        dist_min = h * w
        for c in cardinals: 
            dist =  fn.distanceToPoint(start, c)
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

    # Return quadrant with highest/lowest space
    # Used if cannot reach destination

    # TODO:
    # a = self.combine(:xmid, :ymid)
    # Ref: Numpy subrange array

    def findQuadrantWith(self, t=CONST.legend['empty']):
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

    # Return quadrant with highest/lowest threat
    def findThreat(self):
        pass
        # break into quadrants
        # return

    def findClosestItem(self, items, start):
        
        itemsort = []
        itemlist = []
        
        # if (types == "food"):
        for it in items:
            b = it.getLocation()
            d = fn.distanceToPoint(start, b)
            itemlist.append({'dist':d, 'item':it})
      
        # Return sorted list by distance
        itemlist.sort(key=operator.itemgetter('dist'))
        for i in itemlist: 
          itemsort.append(i['item'])
          
        return itemsort


    def getItemByName(self, items, name):

        for it in items:
            if it.getName() == name:
                return it

        return {}


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


    def getEmptyAdjacent(self, head): 
        w = self.width
        h = self.height  
        s = self.solid

        # Get up / down / left / right 
        directions = [[head[0] + 1, head[1]],
                [head[0] - 1, head[1]], 
                [head[0], head[1] + 1],
                [head[0], head[1] - 1]]

        # Iterate directions 
        for d in directions:
            # Check in bounds & not solid 
            if (0 <= d[0] < h) \
                and (0 <= d[1] < w) \
                and not (s[d[0], d[1]]):

                return d

        # Final failure. Return last point 
        return d


    def randomPoint(self):
        x = int(self.width * rand.random())
        y = int(self.height * rand.random())
        return [y, x]

    # Start time of every move
    def setStartTime(self):
        self.startTime = time.time()

    # Get start time of move -- used for logging
    def getStartTime(self):
        return self.startTime

    # def leastweightPath(self, paths):
    # paths = [[[5, 4], [5, 0]], [[5, 4], [5, 10]], [[5, 4], [10, 4]], [[5, 4], [0, 4]]] ...
    # return path

    def leastWeightLine(self, a, points):
        # Find path with smallest dijkstra value
        # paths = [[5, 0], [5, 10], [10, 5], [0, 5]]
        
        # Set arbitrarily large value
        best = CONST.routeThreshold
        r = []

        for p in points:
            # Check path weigth
            path = fn.getPointsInLine(a, p)
            psum = self.dijkstraPath(path)
            
            if psum < best:
                best = psum
                r = p

        log('route-leastline-dsum', str(points), str(a), str(r), best)

        return r

    def paintArea(self, select, radius=0, a=0, b=0):
        # area = ['centre', 'radius', 'no', 'ea', 'so', 'we', 'ne', 'nw', 'se', 'sw', 'custom']

        self.allowed = []
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
        self.allowed = allowed
        return copy.copy(allowed)



    def enclosedSpace(self, start): 
        # Return volume of enclosed spaces in each direction 
        w = self.width
        h = self.height
     
        sy = start[0]
        sx = start[1]
        
        enclosed = {} 
        
        # Check enclosed space in four directions from start 
        for d in CONST.directions:
            
            encl = np.zeros([h, w], np.intc)
            encl[sy, sx] = 1
        
            dirn = list( map(add, start, CONST.directionMap[d]) )
            # print(str(dirn))
            
            if (self.inBounds(dirn)):
                # print("ENCLOSED", str(encl), str(dirn))
                self.enclosedSpace_step(encl, dirn) 
                                  
            enclosed[d] = copy.copy(encl)
            
        enclsum = {}
        for d in CONST.directions: 
            # Return array of total spaces by direction (eg. up:10
            enclsum[d] = sum(sum(enclosed[d])) - 1
            # print(d, str(enclosed[d]))
        
        self.enclosed = copy.copy(enclsum)
        log('enclosed-sum', str(enclsum))
        return enclsum 


    def enclosedSpace_step(self, encl, dirn): 
        # Iterate through closed space to check volume 

        dy = int(dirn[0])
        dx = int(dirn[1])
        s = self.solid

        # If the point is not a wall 
        # # print("ENCLOSED-STEP", str(dx), str(dy))
        
        if(not s[dy, dx]): 
            # Add to enclosure 
            encl[dy, dx] = 1
    
            for d in CONST.directions:
                
                dnext = list( map(add, dirn, CONST.directionMap[d]) )
                dny = dnext[0]
                dnx = dnext[1]
                # If point is in map & not already visited 
                if (self.inBounds(dnext) and not encl[dny, dnx]):
                    # Recursive  
                    self.enclosedSpace_step(encl, dnext)
        
        else:
            pass
            
        
        return 
