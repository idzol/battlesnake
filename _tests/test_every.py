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

from snakeClass import snake
from boardClass import board

class snakeTest(snake):
    pass 


class boardTest(board):
    
    allpaths = {}


    def initAllPaths(self):
      w = self.width
      h = self.height
      routes = {}
      template = {
            'path': [],
            'length': 0,
            'weight': CONST.routeThreshold,
            'point': CONST.routeThreshold
            # 'threat': CONST.routeThreshold 
      }
      for i in range (0, h): 
        for j in range (0, w):
          point = str([i, j])
          routes[point] = copy.copy(template)

      self.maxpath = copy.copy(template)
      self.allpaths = copy.copy(routes)



    def isRoutePointv2(self, start, turn, eating={}, path=[]):

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
    
        # print("DEBUG", dx, dy, t, step, path)
        # Route logic 
        if (self.inBounds(step)):
          if ((board[dy, dx] == 0) and 
              ((markov[dy, dx] < CONST.pointThreshold) or 
              (t >= board[dy, dx] and 
              markov[dy, dx] < CONST.pointThreshold)) and 
              not (step in path)):

            return (True, copy.copy(markov[dy, dx]))
            
        return (False, CONST.pointThreshold)

      
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


    def hasPath(self):

      # check allpaths for route 
      w = self.width
      h = self.height
      has = np.zeros([h,w], np.intc)
      paths = copy.copy(self.allpaths)
      for i in range(0, h): 
        for j in range(0, w): 
          if len(paths[str([i, j])]['path']):
            has[i, j] = 1 
      
      self.access = copy.copy(has)
      return copy.copy(has) 


    # def __init__():
    def findEveryPath(self, start, 
                             snakes):

        # Calculate path to every point.  Random walk, keep shortest (forwards).  If cheaper point to path exists, ignore other points 
        # TODO: Replace gradient function
        # TODO: Length => 2 * w - 1 assume body is permanent 
        # TODO: Sort by length ... Return longest path (even if no path) 
        # TODO: Link to findBestPath.  eg. choose longer even if we need to survive longer than opponent 

        route = {
            'path': [],
            'weight': 0,
            'point': 0
        }

        # Look in all directions
        for d1 in CONST.directions:
            
            turn = 0 
            step_n = list(map(add, start, CONST.directionMap[d1]))
            
            if (self.inBounds(step_n)):
              # print("STEP EXISTS", step_n)

              route_n = copy.copy(route)
              
              # TODO: Update for each enemy snake 
              eating = self.findEating(snakes, route_n['path'] + [step_n], foods)
                
              # Check next path is in bounds, available and not already visited**
              found, point = self.isRoutePointv2(step_n, turn, eating)
              
              if (found):

                turn += 1
                route_n['weight'] = copy.copy(point)
                route_n['length'] = 1
                route_n['point'] = copy.copy(point)            
                route_n['path'].append(copy.copy(step_n))
                # print('BEFORE STEP',step, snakes, turn, newroute)
                self.findEveryPath_step(route_n, snakes, turn,)

                # Add after find path (checks that step not already in path)
                # print(step, str(self.allpaths))
                
        # return copy.copy(newroute)
        self.hasPath()
      

    def findEveryPath_step(self,
                             route,
                             snakes,
                             turn):


        # Return recursive route / path
        finalroute = []

        # If path meets depth, end recursion
        route_n = copy.copy(route)
        step_n = copy.copy(route_n['path'][-1])
        path_n = copy.copy(route_n['path'])
    
        # Check if this is best path to point 
        path_c = copy.copy(self.allpaths[str(step_n)])
    
        if (not len(route_n) or 
            ((len(route_n['path']) >= len(path_c['path'])) and 
             (route_n['weight'] >= path_c['weight']))):

            return 

        else:
            # Save all paths 
            self.allpaths[str(step_n)] = copy.copy(route_n)
            # Save max path 
            if (route_n['length'] >= self.maxpath['length']) and \
                  (route_n['weight'] <= self.maxpath['weight']):

              self.maxpath = copy.copy(route_n)
                            
        # Last point in path, first point in next step 
        # start = currpath['path'][-1]
         # Look in all directions
        for d2 in CONST.directions:
     
            step_new = list(map(add, step_n, CONST.directionMap[d2]))

            if (self.inBounds(step_new)):
              
              turn_n = turn + 1    
              eating = self.findEating(snakes, path_n, foods)
        
              # Check next path is in bounds.  Probability of collision less than threshold. Available and not already visited**
              found, point = self.isRoutePointv2(step_new, turn_n, eating, path_n)
              
              if (found):  
                  # Add to dir
                  path_new = copy.copy(route_n['path'])
                  path_new.append(step_new)
                  route_n['path'] = copy.copy(path_new) 
                  route_n['length'] = len(path_new)
                  route_n['weight'] += point
                  route_n['point'] = max(point, route_n['point'])

                  route_r = copy.copy(route_n)
                  finalroute = self.findEveryPath_step(route_r, snakes, turn_n)

                 
        return copy.copy(finalroute)


    def pathExists(self, targets):

        exists = []
        access = copy.copy(self.access)
        # Check targets
        for t in targets:
          # Check path exists
          if access[t[0], t[1]]:
            exists.append(t)

        # Return targets with path 
        return copy.copy(exists)


    def pathBacktoBestPath(self, targets):
        
        pass 
        # for t in targets:
        #   bo.route()
        
        return 1



    def selectBestPath(self):
        
        w = self.width
        h = self.height

        # # Lowest threat, highest length
        path_sort = sorted(self.allpaths, key=lambda x: self.allpaths[x]['weight'])
        path_sort = sorted(
            self.allpaths, 
            key=lambda x:(self.allpaths[x]['length']),
            reverse=False)
       
        print(path_sort)
        # for path in path_sort:
        #     print(path_sort[path])

        # # if threat > threshold .. 
        # # Longest dist 
        # sort_length = sorted(adict, key=lambda x: (adict[x]['length'], adict[x]['weight']))

        paths = copy.copy(self.allpaths)
        len_max = w * h

        targets = [[2,3], [4,5], [1,9], [9,1]]

        # Start with "longest" path
        # Consider adding TODO: perform same function from each target (findEveryPath_step)...
        # def pathBackExists(): 
        #   .. 
        # Use route pad??? 
        # or enclose + path (shortcut)?? 

        lmax = w * h 
        best = []
        for i in range(0, h): 
          for j in range(0, w): 
            if l := len(paths[str([i, j])]['path']):
               if l > lmax:
                  best = [i, j] 
                  lmax = l 
          
        return 1 


        # if mutliple paths 
        # if weight < CONST.threshold 
        #   eg. > Total route 
        #   eg. No route
        #   eg. Chase tail
        #   eg. Kill path (100%) vs route padded path 
        #   eg. Certain collision (Body) vs probability 
        #   eg. Some probabiliy vs no probability 
        #     (make sure we're still focused on headon collision)


data = {'game': {'id': '609d47ca-e773-49f9-b3f4-2c52afa4a05c', 'ruleset': {'name': 'solo', 'version': 'v1.0.22', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'royale': {'shrinkEveryNTurns': 0}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'timeout': 500, 'source': ''}, 'turn': 4, 'board': {'height': 11, 'width': 11, 'snakes': [], 'food': [], 'hazards': []}, 'you': {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}}

# test_routes = [{data}, 'up', {data}, 'down']
# for test_data in test_routes  
#   data = data[0]
#   expected = data[1] 
#   # load data
#   # make move 
# data

logger = log()

us = snakeTest()
us2 = snakeTest()
them = snakeTest()

us.setHead([4,3])
us.setBody([[3,3], [3,2], [3,1], [3,0], [2,0]])
us.setHistory([[3,2], [3,1], [3,0], [2,0]])
us2.setHead([6,3])
us2.setBody([[6,2], [6, 1], [6,0], [5,0]])
# us2.setHistory([[6,1], [6,0], [5,0], [4,0]])
us2.setHistory([[6,2], [6,1], [6,0], [5,0]])

them.setHead([7,7])
them.setBody([[7,6],[7,5],[6,5],[6,4],[7,4],[7,3]])
# them.setHistory([[7,6], [7,5]])
them.setHistory(them.getBody())

sn_body = us.getBody()
enemy_body = them.getBody()

us.setType('us')
us.setId('ourSnek')
us2.setId('enemySnek1')
them.setId('enemySnek2')

allSnakes = {
  us.getId():us,
  us2.getId():us2,
  them.getId():them
}

# foods = [[6,6]]
foods = [[2,2], [4,4], [6,6]]

bo = boardTest()
bo.setIdentity(us.getId())

CONST.minProbability = 1

logger.timer('== Update Boards ==')
bo.updateBoards(data, us, allSnakes, foods) 
bo.updateChance(allSnakes, foods)
bo.updateMarkov(us, allSnakes, foods)
bo.updateDijkstra(us)
logger.timer('== Finish Boards ==')

path = [10, 10]

# route = bo.findLargestPath([path])
route = bo.initAllPaths()

# Calculate paths .. 
route = bo.findEveryPath(path, allSnakes)

# Find target (statemachine)


# Check path (ie. longest path) 
# else recalc path @ target
# else abandon .. 

# print(bo.combine)
# print(bo.trailsSnake)
print(bo.markovs[0])

bo.hasPath()

targets = [[0,0], [2,0], [3,9], [9,1]]

print(bo.pathExists(targets))

# print(bo.selectBestPath())
print (bo.maxpath)

logger.timer('== Finish Paths ==')

