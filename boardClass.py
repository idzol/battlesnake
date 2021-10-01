from typing import List, Dict

import math 

import numpy as np
# import pandas as pd
# import random as rand

import constants as CONST
import functions as fn 

# board.py
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
            # self.you[h-py-1, px] = CONST.legend['you-body']
            self.you[py, px] = CONST.legend['you-body']

        head = data['you']['head']
        px = head['x']
        py = head['y']
        # self.you[h-py-1, px] = CONST.legend['you-head']
        self.you[py, px] = CONST.legend['you-head']

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

                head = sk['head']
                px = head['x']
                py = head['y']
                # self.snakes[h-py-1, px] = self.legend['enemy-head']
                self.snakes[py, px] = CONST.legend['enemy-head']

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
        
        # TODO: Improve .. 
        w = self.width 
        h = self.height
        ones = np.ones((w, h), np.intc)

        self.dijkstra = 100 * self.solid + ones 
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
            
            rt = self.findBestPath(start, finish)
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
  
  
    def findBestPath(self, a, b):  
        if (isinstance(a, dict) or isinstance(b, dict)):
          print("ERROR: findBestPath(self, a, b) - dict received when list array expected") 
          return -1


        paths = [[a]]  
        # paths = [ [ [0, 0], .. ], .. ]
        
        # Get next point in path until reaching destination (recursive) 
        for d in range(0, self.maxdepth):
            newpaths = []
            
            for p in paths:
                # p = [ [0, 0], .. ] 
                newpaths = newpaths + self.definePaths(p, b)
                # TODO:  Minidijkstra
                # newpaths = self.removeHighWeightPath(newpaths)
                
            paths = paths + newpaths
            # print(paths)
        
        bestpath = self.leastWeightPath(paths, b)

        print("COMBINE-MAP")
        fn.printMap(self.combine)

        print("BEST-PATH")
        print(str(bestpath))
        return bestpath 

    
    def definePaths(self, a, b):
        
        paths = []
        # a = [ [0, 1] ] or [ [0, 0], [1, 0] ]
        try:
            # Last point in route
            afin = a[-1]
            # afin = [1, 0]
            
            # Check if we've reached destination
            if (afin == b):
                pass 

            else:                 
                # Get next possible move 
                points = self.findPossiblePathPoints(afin)
                # print("PATHS")
                # print(str(points))
                for point in points:
                    paths.append(a + [point])

        except:
            pass
        
        # print("Next Path")
        # print(str(paths))    
        return paths 


    def findClosestWall(self, sn):
    
        start = sn.getLocation("head")
        ax = start[1]
        ay = start[0]

        w = self.width
        h = self.height
        walls = [[ay, 0], # Left
              [ay, w],    # Right
              [h, ax],    # Up
              [0, ax]]    # Down

        # Possible that snake is on wall 
        paths = []
        for w in walls: 

            path = fn.getPointsInLine(start,w)
            if(path != []):
              paths.append(path)

        # TODO: 
        # * Split out dijkstra function
        # * Modify leastWeightPath to optionnl target
        # return leastWeightPath(paths)


    def findPossiblePathPoints(self, a):

        w = self.width 
        h = self.height
        
        ax = a[1]
        ay = a[0]
        
        nodes = []
        
        # get paths
        for wx in range(0, w):
            if wx != ax: 
                # nodes.append([{'x':wx, 'y':ay}])
                nodes.append([ay, wx])
        
        for hy in range(0, h):
            if hy != ay:
                nodes.append([hy, ax])

        # TODO:  Eliminate any with collisions to improve performance 
        # for n in nodes:
        #    .. 
        
        # print(str(a) + ":" + str(nodes))
        return nodes 


    def removeHighWeightPath(self, paths):

        dijmax = 1000
        pathlow = []
        pathhigh = []

        for path in paths:
            
            # Translate vectors into points 
            pts = []
            va = []
            
            for vb in path:
                
                # Skip first point (need two points for line)  
                if (len(va)):
                    # Add points in line 
                    # print(str(va)+str(vb))
                    pts = pts + fn.getPointsInLine(va, vb)

                va = vb 
            
            # calculate path weight    
            pmask = self.drawMask(pts)                
            dij = self.dijkstra
            pdij = dij * pmask
            dijtotal = sum(map(sum,pdij)) 

            # save best path  
            if (dijtotal > dijmax):
                pass
                # Ignore path 
                # pathhigh.append(path)
            else: 
                pathlow.append(path)

        # print("PATH-HIGH")
        # print(str(pathhigh))
        # print("PATH-LOW")
        # print(str(pathlow))

        return pathlow


    def leastWeightPath(self, paths, target=[]):

        # paths = [ [[0, 0]], [[0, 0], [1, 0]], [[0, 0], [2, 0]] ...
        # ...  [[0, 0], [2, 0], [2, 0]] ]
         
        # Find path with smallest dijkstra value 
        # Set arbitrarily large value 
        bestpath = []
        bestdij = []
        dijlast = 1000000
        
        for path in paths:
            
            # Check path actually made it to the target, or invoked without target 
            try: 
              finish = path[-1]
            except: 
              finish = []

            if (finish == target or len(target) == 0): 
                # Translate vectors into points 
                pts = []
                va = []
                
                # print ("VECTORS")
                # print (str(path))               
                
                for vb in path:
                    
                    # Skip first point (need two points for line)  
                    if (len(va)):
                        # Add points in line 
                        # print(str(va)+str(vb))
                        pts = pts + fn.getPointsInLine(va, vb)

                    va = vb 

                # print ("VECTOR-POINTS")
                # print (str(pts))
               
                # calculate path weight    
                pmask = self.drawMask(pts)                
                dij = self.dijkstra
              
                # print("DIJKSTRA")
                # print (str(dij))
                # print ("MASK")
                # print (str(pmask))
                pdij = dij * pmask
                
                # print ("DIJMASK")
                # print (str(pdij))

                dijtotal = sum(map(sum,pdij)) 

                # save best path  
                if (dijtotal < dijlast):
                    bestpath = pts 
                    bestdij = pdij
                    dijlast = dijtotal


        print ("DIJKSTRA-PATH")
        print("Value: " + str(dijlast))
        fn.printMap(bestdij)
        return bestpath 
    
    
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

        # break into quadrants 
        y = h
        x = 0
        for row in bd: 
          y = y - 1
          for cell in row: 
            x = x + 1
            if(cell == t): 
              if (y < ymid):
                i = 0
              elif (y > ymid):
                i = 1
              elif (x < xmid):
                i = 2
              elif (x > xmid):
                i = 3
              else:
                pass 
                # on the line 
                # ie. inbetween quadrants
        
            sides[i] = sides[i] + 1

        # return quadrants 
        return sides


def findQuadrantWith(self, t=CONST.legend['empty']):

    # Return quadrant with highest/lowest space 
    # Used if cannot reach destination
    def findQuadrantWith(self, t=CONST.legend['empty']):
        w = self.width 
        h = self.height
        bd = self.combine
        
        xmid = math.floor((w-1)/ 2)
        ymid = math.floor((h-1)/ 2)

        quads = [0] * 4
        # 0 - NW top left 
        # 1 - NE top right 
        # 2 - SW bottom left
        # 3 - SE bottom right 

        # break into quadrants 
        y = h
        x = 0
        for row in bd: 
          y = y - 1
          for cell in row: 
            x = x + 1
            if(cell == t): 
              if (x < xmid & y > ymid):
                i = 0
              elif (x > xmid & y > ymid):
                i = 1
              elif (x < xmid & y < ymid):
                i = 2
              elif (x > xmid & y < ymid):
                i = 3
              else:
                pass 
                # on the line 
                # ie. inbetween quadrants
        
            quads[i] = quads[i] + 1

        # return quadrants 
        return quads 
      
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

