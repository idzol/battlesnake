from typing import List, Dict

import math
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

    # board matrices
    land = []
    mask = []

    distance = []  # Array of distance
    threat = []  # Array of threat rating
    you = []  # Array of snek (101-head, 100-body)
    you_route = []  # Array of snek (minus head)

    snakes = []  # Array of other snek (201-head, 200-body)
    items = []  # Array of items (300-food, 301-hazard)

    solid = []  # Array of all solids (snakes, walls)
    combine = []  # Array of all layers (snakes, walls, items)

    dijkstra = []
    gradient = []
    gradients = {}  # List of previous gradients
    # 'cell':[turn,gradient]

    predict = []  # Array of board in n moves (prediction)

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
        self.maxpaths = CONST.maxOwnPaths
        self.maxPredictTurns = CONST.maxPredictTurns

        self.startTime = time.time()
        self.win = 0
        self.loss = 0

        self.hurry = False

    def resetCounters(self):
        self.turn = 0
        self.hurry = False
        self.recursion_route = 0
        self.gradients = {}

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

    def getSolid(self):
        return self.solid

    def getCombine(self):
        return self.combine

    def getThreat(self):
        return self.threat

    def getYou(self):
        return self.you

    def getSnakes(self):
        return self.snakes

    def getItems(self):
        return self.items

    def getDijkstra(self):
        return self.dijkstra

    def setMaxDepth(self, d):
        self.maxdepth = d

    def getMaxDepth(self):
        return self.maxdepth

    def getTurn(self):
        t = self.turn
        return copy.copy(t)

    def setTurn(self, t):
        self.turn = t

    def updateBoards(self, data):

        # Update game parameters
        width = int(data['board']['width'])
        height = int(data['board']['height'])
        self.setDimensions(width, height)
        self.setTurn(data['turn'])

        # Update boards
        by = self.updateBoardYou(data)

        bs = self.updateBoardSnakes(data)
        bi = self.updateBoardItems(data)

        # Update meta-boards
        # updateDistance
        # updateThreat(data

        # Combine boards

        # Solid -- Normalise solid to 99, +1 in dijkstra()
        self.solid = CONST.routesolid * np.ceil(by / (by + 1) + bs / (bs + 1))

        self.combine = by + bs + bi  # Array of all layers (snakes, walls, items)

        di = self.updateDijkstra(fn.XYToLoc(data['you']['head']))
        # gr = self.updateGradient() -- only update when rqd for routing

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

    # assign a "threat" value based on distance to enemy snake and size
    def updateThreat(self, data):
        # data -> snake, enemy
        pass

    def updateDijkstra(self, data_you):

        w = self.width
        h = self.height

        ay = data_you[0]
        ax = data_you[1]

        # Default resistance = 1
        ones = CONST.routeresistance * np.ones((w, h), np.intc)

        # Solids weighted @ 100
        # Food / hazards weighted @ 1
        # TODO: include hazards (self.items)
        self.dijkstra = self.solid + ones
        self.dijkstra[ay, ax] = 0

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
                it = self.getClosestItem(items, start, "food")  # ??
                finish = it.getLocation()
                rt = self.route(start, finish)
                # Limit depth to X

                # TODO: Assume strategy is kill (len > X)
                # TODO: Assume strategy is board control / loop etc (eg. circular)

                sn.setRoute(rt)

    def updatePredict(self, snakes):

        w = self.width
        h = self.height
        p = self.predict
        depth = CONST.maxPredictTurns
        full = CONST.routesolid

        # log("predict-update")
        you_len = 10
        you_head = [-1, -1]

        # Get our head
        for identity in snakes:
            sn = snakes[identity]
            if (sn.getType() == "us"):
                you_head = sn.getHead()
                you_len = sn.getLength()

        # Update death zone for
        for identity in snakes:
            if (sn.getType() != "us"):
                # Death zone (+) around larger snakes
                length = sn.getLength()
                head = sn.getHead()

                if length >= you_len:
                    ay = head[0]
                    ax = head[1]
                    ay1 = max(0, ay - 1)
                    ay2 = min(h, ay + 2)
                    ax1 = max(0, ax - 1)
                    ax2 = min(w, ax + 2)

                    # print("AVOID HEAD")
                    # print(ay,ax,ay1,ay2,ax1,ax2)
                    self.solid[ay1:ay2, ax] = full/2
                    self.solid[ay, ax1:ax2] = full/2

                # DEPRECATE:  Use predict matrix rather than solid ...

        # Iterate through next t turns
        for identity in snakes:
            sn = snakes[identity]

            # Get head, body & predicted route
            name = sn.getType()
            head = sn.getHead()
            body = sn.getBody()
            rt = sn.getRoute()
            # TODO:  Check to convert route to points (if not already).
            rt = fn.getPointsInRoute(rt)

            length = len(body) + 1
            # length = sn.getLength()
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

            # Go thorugh next t moves
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
                    # Get next move from route
                    r1 = rt.pop(0)
                    # Update the prediction board
                    # p - predict matrix
                    # t - turn
                    # r1 - point
                    # val - gradient / path weight
                    snakemap[t][r1[0],
                                r1[1]] = p[t][r1[0], r1[1]] + val_predict
                    # Add route to head of body
                    body.insert(0, r1)
                    log('predict-new', str(t), str(rt), str(r1))

                except Exception as e:
                    # end of route
                    print(str(e))
                    pass

                # Erase tail (last point in body)
                try:
                    # Remove tail
                    b1 = body.pop(-1)
                    # Update the prediction board
                    snakemap[t][b1[0],
                                b1[1]] = snakemap[t][b1[0],
                                                     b1[1]] - val_certain
                    log('predict-erase', str(t), str(body), str(b1))

                except Exception as e:
                    # end of body
                    print(str(e))
                    pass

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
            log('map', 'PREDICT', pmap)

        log('map', 'SOLID', self.solid)
        # TODO:  Move this to before it is used, rather than after predict is updated
        self.updateDijkstra(you_head)
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

    def route(self, a, b, threshold=CONST.routeThreshold):

        t = threshold
        r = []

        # TODO: if (not len(a) or not len(b)):
        #   no valid route requested.
        #   try / except
        log('route-fromto', a, b)
        log('map', 'SOLID', self.solid)
        # IF start / finish not defined ..
        if (not len(a) or not len(b)):
            return r

        # try simple, medium, complex route
        while 1:
            # (1) Simple straight line (a->b)
            log('time', 'Before Basic Route', self.getStartTime())
            if (a[0] == b[0]) or (a[1] == b[1]):
                weight = self.dijkstraSum(a, b)
                if (weight < t):
                    # log('route-weight', 'basic', weight)
                    print('WEIGHT 1')
                    print(str(weight))
                    r = [b]
                    break

            # (2) Simple dog leg (a->c->b)
            log('time', 'Before Medium Route', self.getStartTime())
            c2 = [b[0], a[1]]
            c1 = [a[0], b[1]]
            # TODO: Inverted c1 & c2 to fix.  Work out why?

            c1sum = self.dijkstraSum(a, c1) + self.dijkstraSum(c1, b)
            log('route-dijkstra-sum', str(a), str(c1), str(b), c1sum)
            c2sum = self.dijkstraSum(a, c2) + self.dijkstraSum(c2, b)
            log('route-dijkstra-sum', str(a), str(c2), str(b), c2sum)

            if (c1sum <= c2sum) and (c1sum < t):
                r = [c1, b]
                break

            elif (c2sum <= c1sum) and (c2sum < t):
                r = [c2, b]
                break

            print('WEIGHT 2')
            print(str(c1sum), str(c2sum))

            # (3) Complex route
            log('time', 'Before Complex Route', self.getStartTime())

            r = self.route_complex(a, b)
            # r, w = self.route_complex(a, b)
            # weight = w
            # print('WEIGHT 3')
            # print(str(Weight))

            break

        # Return next path/point or [] if no path

        # TODO:  Separate basic/medium/complex route into separate functions so they can be reused ..

        log('route-return', r)
        # fn.printMap(self.dijkstra)
        fn.printMap(self.combine)

        return r

    def route_complex(self, a, b):
        # Return path, point. [] if no path or error

        h = self.height
        w = self.width

        # if (time < timethreshold):
        #   update gradient
        # else:
        #   use existing gradient

        self.gradient = np.full([h, w], CONST.routeThreshold)
        self.gradient[b[0], b[1]] = self.dijkstra[b[0], b[1]]
        log('time', 'Before Gradient', self.getStartTime())

        self.updateGradient(b)
        log('time', 'Updated Gradient', self.getStartTime())

        # Get current turn
        turn = self.getTurn()
        # Save gradient for future turns to optimise search time
        self.gradients[str(b)] = [turn, copy.copy(self.gradient)]
        # log('route-gradient', self.gradient)

        if (self.gradient[a[0], a[1]] > CONST.routeThreshold):
            # no path
            return []

        else:
            # Recurse until destination reached or path exceeds num points
            path = []
            pathlength = 1
            anew = copy.copy(a)

            while 1:
                # find lowest gradient route & add to path
                r = self.route_complex_step(anew, b)

                # No path found / error
                if (not len(r)):
                    path = []
                    break

                # Otherwise append path
                path.append(r)

                # Break once reaching destination or at board limit
                if (path[-1] == b) or (pathlength > h * w):
                    break

                # Last step becomes first step for next iteration
                anew = copy.copy(path[-1])
                pathlength = pathlength + 1

        fn.printMap(self.gradient)
        log('route-complex-path', str(path))
        return path

    def route_complex_step(self, a, b):
        # Return next point. [] if no path or error

        log('route-complex-step', a, b)
        # set up directions to check for
        directions = [[a[0] + 1, a[1]], [a[0] - 1, a[1]], [a[0], a[1] + 1],
                      [a[0], a[1] - 1]]

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

        return c

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

    def updateGradient(self, b):

        # TODO: Change gradient to start searching from a, to work with predict matrices (ie. turns from sn.head())

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

        t = CONST.routeThreshold
        h = self.height
        w = self.width

        directions = [[b[0] + 1, b[1]], [b[0] - 1, b[1]], [b[0], b[1] + 1],
                      [b[0], b[1] - 1]]

        for b1 in directions:
            # Check in bounds
            if (0 <= b1[0] < h) and (0 <= b1[1] < w):

                g0 = self.gradient[b[0], b[1]]
                g1 = self.gradient[b1[0], b1[1]]
                d1 = self.dijkstra[b1[0], b1[1]]
                # TODO:  Use self.predict instead of self.dijkstra
                # d1dist = fn.getDistance(a1, b1)
                # d1 = self.dijkstra[d1dist[]][b1[0], b1[1]]

                # Check path is cheaper
                if ((d1 < t) and (g0 + d1) < g1):

                    # Gradient can't handle negatives
                    if (d1 < 0):
                        d1 = 0

                    # Update point
                    self.gradient[b1[0], b1[1]] = g0 + d1

                    # Recursion
                    self.updateGradient(b1)

    def dijkstraSum(self, a, b, t=CONST.pathThreshold):
        # Sum dijkstra map between two points

        # fn.printMap(self.dijkstra)
        try:
            if (a[0] == b[0] and a[1] != b[1]):
                if (a[1] < b[1]):
                    result = sum(self.dijkstra[a[0], a[1]:b[1] + 1])
                    # print('RESULT1:', str(a), str(b), str(result))
                else:
                    result = sum(self.dijkstra[a[0], b[1]:a[1] + 1])
                    # print('RESULT2:', str(a), str(b), str(result))
            elif (a[1] == b[1] and a[0] != b[0]):
                if (a[0] < b[0]):
                    result = sum(self.dijkstra[a[0]:b[0] + 1, a[1]])
                    # print('RESULT3:', str(a), str(b), str(result))
                else:
                    result = sum(self.dijkstra[b[0]:a[0] + 1, a[1]])
                    # print('RESULT4:', str(a), str(b), str(result))

            else:
                result = t + 1

        except:
            result = t + 1

        return result

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

    def getClosestItem(self, its, loc, t):

        lowest = 100
        name = ""

        if (t == "food"):
            for it in its:
                # print (it)

                itp = it.getLocation()
                d = fn.distanceToPoint(itp, loc)
                if (d < lowest):
                    lowest = d
                    name = it
                    # TODO: if two of same dist, returns top left. do we want to change / randomise this?

        return it

    def getItemByName(self, items, name):

        for it in items:
            if it.getName() == name:
                return it

        return {}

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
            psum = self.dijkstraSum(a, p)
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


# === DEPRECATED ===

# def findBestPath(self, a, b):
#     if (isinstance(a, dict) or isinstance(b, dict)):
#       log('findbestpath-usage')
#       # print("ERROR: findBestPath(self, a, b) - dict received when list array expected")
#       return -1

#     paths = [[a]]
#     # paths = [ [ [0, 0], .. ], .. ]

#     # Get next point in path until reaching destination (recursive)
#     for d in range(0, self.maxdepth):
#         newpaths = []

#         for p in paths:
#             # p = [ [0, 0], .. ]
#             newpaths = newpaths + self.definePaths(p, b)
#             # TODO:  Minidijkstra
#             # newpaths = self.removeHighWeightPath(newpaths)

#         paths = paths + newpaths
#         # print(paths)
#     log('time', 'Define Paths', self.getStartTime())

#     bestpath = self.leastWeightPath(paths, b)
#     log('time', 'Least Weight Path', self.getStartTime())

#     print("COMBINE-MAP")
#     fn.printMap(self.combine)

#     print("BEST-PATH")
#     print(str(bestpath))
#     return bestpath

# def definePaths(self, a, b):

#     paths = []
#     # a = [ [0, 1] ] or [ [0, 0], [1, 0] ]
#     try:
#         # Check if we've reached destination
#         if (a[-1] == b):
#             pass

#         else:
#             # Get next possible move
#             print("TEST", str(a))

#             if(len(a) > 1):
#               points = self.findPossiblePathPoints(a[-1], a[-2])
#             else:
#               points = self.findPossiblePathPoints(a[-1])

#             # log('paths', points)
#             for point in points:
#                 paths.append(a + [point])

#     except:
#         pass

#     # print("Next Path")
#     # print(str(paths))
#     return paths

# def findPossiblePathPoints(self, a1, a2=[-1,-1]):
#     w = self.width
#     h = self.height

#     ax = a1[1]
#     ay = a1[0]
#     ax2 = a2[1]
#     ay2 = a2[0]

#     nodes = []

#     # Make sure we don't search X twice in a row
#     # get paths
#     if (ax != ax2):
#       for wx in range(0, w):
#           if wx != ax:
#               # nodes.append([{'x':wx, 'y':ay}])
#               nodes.append([ay, wx])

#     # Make sure we don't search Y twice in a row
#     if (ay != ay2):
#       for hy in range(0, h):
#           if hy != ay:
#               nodes.append([hy, ax])

#     print("TEST4", str(nodes))
#     # Eliminate any immediate collisions to improve performance
#     for n in nodes:
#       # if (self.solid[n[1],n[0]] != 0):
#       # print("TEST5", str(nodes))
#       if(self.dijkstraSum(a1, n) > 10):
#         nodes.remove(n)

#     print("TEST5", str(nodes))
#     # log('findbestpath-debug', str(a2), str(a1), str(nodes))
#     return nodes

# def removeHighWeightPath(self, paths):

#     dijmax = 1000
#     pathlow = []
#     pathhigh = []

#     for path in paths:

#         # Translate vectors into points
#         pts = []
#         va = []

#         for vb in path:

#             # Skip first point (need two points for line)
#             if (len(va)):
#                 # Add points in line
#                 # print(str(va)+str(vb))
#                 pts = pts + fn.getPointsInLine(va, vb)

#             va = vb

#         # calculate path weight
#         pmask = self.drawMask(pts)
#         dij = self.dijkstra
#         pdij = dij * pmask
#         dijtotal = sum(map(sum,pdij))

#         # save best path
#         if (dijtotal > dijmax):
#             pass
#             # Ignore path
#             # pathhigh.append(path)
#         else:
#             pathlow.append(path)

#     # print("PATH-HIGH")
#     # print(str(pathhigh))
#     # print("PATH-LOW")
#     # print(str(pathlow))

#     return pathlow
