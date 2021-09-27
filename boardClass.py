from typing import List, Dict

import numpy as np
import pandas as pd
import random as rand

# from functions import distanceToPoint
# TODO: move updateDistance / distanceToPoint into functions? 

# board.py
class board(): 
    
    legend = {
        'you-head':10,
        'you-body':11,
        'you-tail':12,
        'enemy-head':20,  # Snake ID * value .. 
        'enemy-body':21,
        'enemy-body':22,
        'food':-30,       
        'hazard':31
    }
    # routing algorithm avoids positive values & attracted to negative values 
        
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
    

    def __init__(self, width=0, height=0, maxdepth=3, maxpaths=100):
      # globals 
      self.height = width
      self.width = height

      self.land = np.zeros((height, width), np.intc) 
      self.mask = np.ones((height, width), np.intc)

      self.maxdepth = maxdepth
      # search depth for moves.  
      # why does 4 fail. Latency, loop?
      
      self.maxpaths = maxpaths


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
   

    def setPoint(self, p: Dict[str, int]):
        self.land[p["x"], p["y"]] = 1
        return True 
    
    def getPoint(self, x, y):
        return self.land[x, y]
    
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
        # w = self.width 
        h = self.height

        if(isinstance(pt, dict)):
          px = pt['x']
          py = pt['y']
          return [h-py-1, px]
          
        else:
          return pt

    def updateBoardYou(self, data):
        # Array of snek (101-head, 100-body)
        w = self.width 
        h = self.height
        self.you = np.zeros((h, w), np.intc) 

        body = data['you']['body']
        for pt in body: 
            px = pt['x']
            py = pt['y']
            self.you[h-py-1, px] = self.legend['you-body']

        head = data['you']['head']
        px = head['x']
        py = head['y']
        self.you[h-py-1, px] = self.legend['you-head']

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
                    self.snakes[h-py-1, px] = self.legend['enemy-body']

                head = sk['head']
                px = head['x']
                py = head['y']
                self.snakes[h-py-1, px] = self.legend['enemy-head']

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
            self.items[h-py-1, px] = self.legend['food']

        for hd in hds: 
            px = hd['x']
            py = hd['y']
            self.items[h-py-1, px] = self.legend['hazard']

        return self.items
 
 
    def updateDistance(self, data):
             
        w = self.width 
        h = self.height
        self.distance = np.zeros((h, w), np.intc) 
        
        head = data['you']['head']

        for i in range(0,w):
            for j in range(0,h):
                d = distanceToPoint(head, {'x':i, 'y':j}, "point")
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

  
    # TODO: work in progress
    # Check for collission in x rounds time 
    def checkCollisionPredict(bo, route):
        # for r in route:
        #   i = i + 1 
        #   board = predict[i]
        #   checkCollision(board, r)
        # return coll
        pass
  
  
    def findBestPath(self, a, b):  
        
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
        print(str(self.combine))

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

                
    def findPossiblePathPoints(self, a):

        w = self.width 
        h = self.height
        
        ax = a[0]
        ay = a[1]
        
        nodes = []
        
        # get paths
        for wx in range(0, w):
            if wx != ax: 
                # nodes.append([{'x':wx, 'y':ay}])
                nodes.append([wx, ay])
        
        for hy in range(0, h):
            if hy != ay:
                nodes.append([ax, hy])

        # TODO:  Eliminate any with collisions to improve performance if rqd
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
                    pts = pts + getPointsInLine(va, vb)

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



    def leastWeightPath(self, paths, target):

        # paths = [ [[0, 0]], [[0, 0], [1, 0]], [[0, 0], [2, 0]] ...
        # ...  [[0, 0], [2, 0], [2, 0]] ]
         
        # Find path with smallest dijkstra value 
        # Set arbitrarily large value 
        bestpath = []
        bestdij = []
        dijlast = 1000000
        
        for path in paths:
            
            # Check path actually made it to the target
            if (path[-1] != target):
                pass 
            
            else: 
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
                        pts = pts + getPointsInLine(va, vb)

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
        print(str(bestdij))
        return bestpath 
    
    
    def drawMask(self, pts):
        # Create as mask 
                
        w = self.width 
        h = self.height
        # pmask = np.full((w, h), True)
        pmask = np.zeros((w, h), np.intc)

        for p in pts: 
            # px = p[0]
            # py = p[1]          
            # pmap['x':px, 'y':py] = False
            pmask[p[0], p[1]] = 1
              
        return pmask

# TODO:  Move to functions.py or other (solve for recursion error..)

def getPointsInLine(a, b):
    # a = [0, 0], b = [2, 0]
    # a = [2, 0], b = [2, 2]
    
    # print("LINE POINTS")
    # print(str(a) + str(b))
    
    ax = a[0]
    ay = a[1]
    bx = b[0]
    by = b[1]

    line = []

    # Point (not a line)
    if (ax == bx) & (ay == by): 
        return [] 
    
    # Line along Y 
    elif (ax == bx):
        # Decide up or down 
        if (ay > by):
            inc = -1
        else:
            inc = 1
        
        ayd = ay
        while (ayd != by):
            ayd = ayd + inc
            line.append([ax, ayd])

    # Line along X
    elif (ay == by):
        # Decide up or down 
        if ax > bx: 
            inc = -1
        else:
            inc = 1
        
        axd = ax    
        while (axd != bx):
            axd = axd + inc
            line.append([axd, ay])
            
    # Not a perpendicular line 
    else:
        return []

    # line.append(b)
    # print("LINE")
    # print(str(line))
    return line

  
def distanceToPoint(a, b, type="array"):
    
    try: 

      if(type=="point"):
        ax = a['x']
        bx = b['x']
        ay = a['y']
        by = b['y']
      else:
        ax = a[1]
        bx = b[1]
        ay = a[0]
        by = b[0]
    
      dx = abs(ax - bx)
      dy = abs(ay - by)
      d = dx + dy
      return d

    except: 
      return -1
  