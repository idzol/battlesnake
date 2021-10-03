from typing import List, Dict

import math 
import random as rand 
import numpy as np
# import pandas as pd
# import random as rand

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
    
    distance = []   # Array of distance 
    threat = []     # Array of threat rating 
    you = []     # Array of snek (101-head, 100-body)
    snakes = []  # Array of other snek (201-head, 200-body)
    items = []   # Array of items (300-food, 301-hazard)
    
    solid = []   # Array of all solids (snakes, walls)
    combine = [] # Array of all layers (snakes, walls, items)
 
    dijkstra = []
    gradient = []
    predict = []  # Array of board in n moves (prediction)
    

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


    def setDimensions(self, x, y):
        if isinstance(x, int) and isinstance(y, int):
            self.width = x
            self.height = y
            self.land = np.zeros((x,y), np.intc)
            return True 

        else:
            return False 
  
    def getDimensions(self):
        return [self.width, self.height]
   

    def setPoint(self, p: Dict[str, int], t="array"):
      try:
        if (t=="dict"):
          self.land[p["x"], p["y"]] = 1
          return True 

        elif (t=="array"):
          self.land[p] = 1
          return True

      except:
        return False

    # def getPoint(self, x, y):
    #     return self.land[x, y]
    
    def getPoint(self, p: Dict[str, int], t="array"):
      try:
        if (t=="dict"):
          return self.land[p["x"], p["y"]]
          
        elif (t=="array"):
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
    

    def updateBoards(self,data):
        
        # Update dimensions 
        # setDimensions -- if Royale 

        # Update boards
        by = self.updateBoardYou(data)
        bs = self.updateBoardSnakes(data)
        bi = self.updateBoardItems(data)
        
        # Update meta-boards
        # updateDistance 
        # updateThreat(data

        # Combine boards
        self.solid = by + bs           # Array of all solids (snakes, walls)
        self.combine = by + bs + bi    # Array of all layers (snakes, walls, items)
         
        di = self.updateDijkstra()
        # gr = self.updateGradient() -- only update when rqd for routing
        
        return True


    def XYToLoc(self, pt):

        if(isinstance(pt, dict)):
          px = pt['x']
          py = pt['y']
          return [py, px]
          
        elif(isinstance(pt, list)):
          return pt

        else:
          return [-1,-1]

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
          px = head['x']
          py = head['y']
          self.you[py, px] = CONST.legend['you-head']

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

        return self.items
 
 
    def updateDistance(self, data):
             
        w = self.width 
        h = self.height
        self.distance = np.zeros((h, w), np.intc) 
        
        # Distances from snake head 
        head = self.XYtoLoc(data['you']['head'])

        for i in range(0,w):
            for j in range(0,h):
                d = fn.distanceToPoint(head, [j, i])
                self.distance[i, j] = d

    # assign a "threat" value based on distance to enemy snake and size
    def updateThreat(self, data):
        # data -> snake, enemy
        pass 
  

    def updateDijkstra(self):
        
        w = self.width 
        h = self.height

        # Default resistance = 1
        ones = np.ones((w, h), np.intc)

        # Solids weighted @ 100 
        # Food / hazards weighted @ 1 
        self.dijkstra = 100 * self.solid + 1 * self.items + ones 

        return self.dijkstra

    
    # TODO: work in progress
    def predictBoard(self, data): 
        ## Array of board in n moves (prediction)

        bd = self.combine

        # while -- next X moves 
        # Us -- Update for our route
        # Enemy -- 
        #  If (close to food). Assume food path  
        #  If (attack play). Assume attack
        #  Else.  Assume straight (recursive)
        
        self.predict.append(bd)
        # solid = you & snakes & items 


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
            labels.append("s" + n + ":"+str(name))
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
        self.snakeIndex = si # [1, 2]
        self.foodIndex = fi # [3, 4, 5]
        self.hazardIndex = hi # [6, 7]
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
    def predictEnemyMoves(self, snakes, items):
        
        # get foods
        w = self.width
        h = self.height
        
        fs = self.foodIndex
        predict = []
        
        for sn in snakes:
            
            # Assume strategy is food 
            start = sn.getHead()
            
            iname = self.getClosestItem(sn, items, "food") # ?? 
            it = self.getItemByName(items, iname)

            finish = it.getLocation()
            
            rt = self.route(start, finish)
                # Set depth to 2 or 3 .. 
                # findBestPath.  start with no prediction? 

            sn.setRoute(rt)
  

    def predictMatrix(self, snakes):
      
      depth = self.predictDepth
      w = self.width
      h = self.height
      
      predict = []
      # predict = [turns][w, h]  # np.zeros((w, h), np.intc) 
      
      turns = self.maxPredictTurns

      for sn in snakes:
          for t in range(0, turns):
      
              # get route for snake
              rt = sn.getRoute()
              # snake as array 
              # eraseTail (getTail)
              # eraseHead (getHead)
              # newHead (turns[t])
              # newTail () 
              # paintNewSnake
              # sn.predict[i][r[0], r[1]] = 1:
          
      for t in range(0, turns): 
          for sn in snakes:
            pass 
            # sum all pred matrices 
            # p[t] = p[t] + sn.getPredict(t)
      # self.predict[t] = p[tt 

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
      
        # try simple route
        while 1:
            # (1) Simple straight line (a->b)  
            
            # Set start to zero 
            # TODO: fix in updateDijkstra?
            self.dijkstra[a[0], a[1]] = 0 

            log('time', 'Before Basic Route', self.getStartTime())
            if (a[0] == b[0]) or (a[1] == b[1]):
                if (self.dijkstraSum(a, b) < t):
                    r = [b]
                    break

            # (2) Simple dog leg (a->c->b) 
            log('time', 'Before Medium Route', self.getStartTime())
            c1 = [b[0], a[1]] 
            c2 = [a[0], b[1]]
            
            c1sum = self.dijkstraSum(a, c1) + self.dijkstraSum(c1, b)
            c2sum = self.dijkstraSum(a, c2) + self.dijkstraSum(c2, b)
            
            if (c1sum <= c2sum) and (c1sum < t):
                r = [c1, b]
                break
                
            elif (c2sum <= c1sum) and (c2sum < t): 
                r = [c2, b]
                break
                
            # (3) Complex route 
            log('time', 'Before Complex Route', self.getStartTime())
            r = self.route_complex(a, b)
            break 
        
        # Return next path/point or [] if no path
        
        log('route-return', r)
        fn.printMap(self.dijkstra)

        return r 


    def route_complex(self, a, b):
                    
        h = self.height
        w = self.width 
        c = []
        
        # if (time < timethreshold):  
        #   update gradient
        # else: 
        #   use existing gradient 
  
        self.gradient = np.full([h,w], CONST.routeThreshold)
        self.gradient[b[0], b[1]] = self.dijkstra[b[0], b[1]] 
        log('time', 'Before Gradient', self.getStartTime())
        self.updateGradient(b)
        log('time', 'Updated Gradient', self.getStartTime())
        # log('route-gradient', self.gradient) 
        
        if (self.gradient[a[0],a[1]] > CONST.routeThreshold): 
            # no path 
            return []
        
        else:
            directions = [[a[0] + 1, a[1]], 
                [a[0] - 1, a[1]],
                [a[0], a[1] + 1],
                [a[0], a[1] - 1]]

            gmin = CONST.routeThreshold
            for a1 in directions:
                
                # Check in bounds 
                if (0 <= a1[0] < h) and (0 <= a1[1] < w):
                    g1 = self.gradient[a1[0], a1[1]]
                    
                    if (g1 < gmin):
                        gmin = g1
                        c = [a1]
        
        # Return next point or [] if no path               
        fn.printMap(self.gradient)
        return c


    def updateGradient(self, b):
        # global recursionCount 

        t = CONST.routeThreshold
        h = self.height
        w = self.width 
        
        directions = [[b[0] + 1, b[1]], 
            [b[0] - 1, b[1]],
            [b[0], b[1] + 1],
            [b[0], b[1] - 1]]

        for b1 in directions:
            # Check in bounds 
            if (0 <= b1[0] < h) and (0 <= b1[1] < w):

                g0 = self.gradient[b[0], b[1]]
                g1 = self.gradient[b1[0], b1[1]]
                d1 = self.dijkstra[b1[0], b1[1]]

                # Check path is cheaper 
                if ((d1 < t) and (g0  + d1) < g1):

                    # Update point 
                    self.gradient[b1[0], b1[1]] = g0 + d1 
                    # Recursion 
                    self.updateGradient(b1)


    def dijkstraSum(self, a, b, t=CONST.pathThreshold):
    # Sum dijkstra map between two points
        try: 
          if(a[0] == b[0] and a[1] != b[1]):
            if(a[1] < b[1]): 
                result = sum(self.dijkstra[a[0], a[1]:b[1]])
            else:
                result = sum(self.dijkstra[a[0], b[1]:a[1]])

          elif (a[1] == b[1] and a[0] != b[0]):  
            if(a[0] < b[0]): 
                result = sum(self.dijkstra[a[0]:b[0], a[1]])
            else:
                result = sum(self.dijkstra[b[0]:a[0], a[1]])

          else:
            result = t + 1
        
        except: 
          result = t + 1
            
        return result


    def findClosestWall(self, start):
    
        ax = start[1]
        ay = start[0]

        w = self.width-1
        h = self.height-1
        walls = [[ay, 0], # Left
              [ay, w],    # Right
              [h, ax],    # Up
              [0, ax]]    # Down

        # Possible that snake is on wall 
        paths = []
        for w in walls: 
            if(w != start):
              paths.append([start, w])
  
        print("WALL-PATHS")
        print(str(walls))
        return self.leastWeightPath(paths)

    
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
            if (t=="array"):
              pmask[p[0], p[1]] = 1

        return pmask


    def findDirectionWith(self, t=CONST.legend['empty']):
      # TODO: Update to allow array
      # .. eg. [CONST.legend['hazard'], CONST.legend['food']]

        w = self.width 
        h = self.height
        bd = self.combine
        
        xmid = math.floor((w-1)/ 2)
        ymid = math.floor((h-1)/ 2)

        sides = [0] * 4
        # 0 - Top 
        # 1 - Bottom
        # 2 - Left
        # 3 - Right 
        side_dict = {
            0:CONST.north,
            1:CONST.south,
            2:CONST.west,
            3:CONST.east
        }

        y = 0
        for row in bd: 
          x = 0
          for cell in row: 
            if(cell == t): 
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
            0:CONST.northwest,
            1:CONST.northeast,
            2:CONST.southwest,
            3:CONST.southeast
        }

        xmid = math.floor((w-1)/ 2)
        ymid = math.floor((h-1)/ 2)
                
        q1 = bd[(ymid+1):,:xmid]
        q2 = bd[(ymid+1):,(xmid+1):]
        q3 = bd[:ymid,:xmid]
        q4 = bd[:ymid,(xmid+1):]
       
        quads = [np.count_nonzero(q1 == t),
                np.count_nonzero(q2 == t),
                np.count_nonzero(q3 == t),
                np.count_nonzero(q4 == t)]

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
                    name = it.getName()
                    # TODO: if two of same dist, returns top left. do we want to change / randomise this? 

        return name


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


    # def leastWeightPath(self, paths, target=[]):

    #     # paths = [ [[0, 0]], [[0, 0], [1, 0]], [[0, 0], [2, 0]] ...
    #     # ...  [[0, 0], [2, 0], [2, 0]] ]
         
    #     # Find path with smallest dijkstra value 
    #     # Set arbitrarily large value 
    #     bestpath = []
    #     bestdij = []
    #     dijlast = 1000000
        
    #     for path in paths:
            
    #         # Check path actually made it to the target, or invoked without target 
    #         try: 
    #           finish = path[-1]
              
    #         except: 
    #           finish = []

    #         if (finish == target or len(target) == 0): 
    #             # Translate vectors into points 
    #             pts = []
    #             va = []
                
    #             # print ("VECTORS")
    #             # print (str(path))               
                
    #             for vb in path:
                    
    #                 # Skip first point (need two points for line)  
    #                 if (len(va)):
    #                     # Add points in line 
    #                     # print(str(va)+str(vb))
    #                     pts = pts + fn.getPointsInLine(va, vb)

    #                 va = vb 

    #             # print ("VECTOR-POINTS")
    #             # print (str(pts))
               
    #             # calculate path weight    
    #             pmask = self.drawMask(pts)                
    #             dij = self.dijkstra
              
    #             # print("DIJKSTRA")
    #             # print (str(dij))
    #             # print ("MASK")
    #             # print (str(pmask))
    #             try:
    #               pdij = dij * pmask
    #             except Exception as e: 
    #               print(str("ERROR: Boards not initialised.  Try bo.updateBoards(data). " + str(e)))

    #             # print ("DIJMASK")
    #             # print (str(pdij))

    #             dijtotal = sum(map(sum,pdij)) 

    #             # save best path  
    #             if (dijtotal < dijlast):
    #                 bestpath = pts 
    #                 bestdij = pdij
    #                 dijlast = dijtotal


    #     print ("DIJKSTRA-PATH")
    #     print("Value: " + str(dijlast))
    #     fn.printMap(bestdij)
    #     return bestpath 
     