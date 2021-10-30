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



    def findLargestPath(self, route, snakes, turn=0, foods=[], depth=CONST.lookAheadPath):
        # Iterate through closed space to check volume
        # **TODO: Include own path as layer in future updateTrails
        # TODO: Introduce panic timers if routing too long
        # TODO: Introduce threat from other snakes into s[dy, dx] -> s[turn][dy, dx] udating predict matrix
        # TODO:  Return best path vs any path (similar to introducing snake threat)
        
        # print("LARGEST", route, snakes, turn, foods, depth)
                

        # print("FINDPATH", str(path), str(turn))
        if (len(route)):
            start = copy.copy(route[-1])

        else:
            return []

        # store all paths 
        allpaths = []

        # Look in all directions
        for d in CONST.directions:
            newturn = copy.copy(turn)
            step = list(map(add, start, CONST.directionMap[d]))
            path = copy.copy(route)
            newpath = []
            
            # Eating next turn:  Compensate body / tail avoidance if eating next turn 
            # TODO: Update trails rather than turn (ie. turn affects markov?) 
            # Check if food is in past moves

            # TODO: Update for each enemy snake 
            eating = self.findEating(snakes, path + [step], foods)
              
            # Check next path is in bounds, available and not already visited**
            found, point = self.isRoutePointv2(step, newturn, eating)
            
            # Check next path is in bounds, available and not already visited**
            if(found):
            # self.isRoutePoint(step, turn_adjust)):
    
                newturn += 1

                path.append(step)
                # found, newpath = 

                self.findLargestPath_step(step, snakes, turn, depth, path, allpaths)

                # if (len(newpath) >= depth):
                #     # Max path found - Exit search
                #     # TODO: This optimises time (first path that meets depth) but is it best path?
                #     break


        lenmax = 0
        finalpath = []
        print("ALL PATHS", allpaths)
        
        for p in allpaths: 
            if len(p) > lenmax:
                lenmax = len(p)
                finalpath = copy.copy(p)
            
        print("FINAL PATHS", finalpath)
        return copy.copy(finalpath) 


    def findLargestPath_step(self,
                             route,
                             snakes, 
                             turn=0,
                             depth=CONST.lookAheadPath,
                             path=[],
                             allpaths=[]):

        # If path meets depth, end recursion
        if (len(path) >= depth):
            return path

        start = copy.copy(route)
        pathnew = copy.copy(path)

        # Look in all directions
        found = False 
        for d in CONST.directions:

            step = list(map(add, start, CONST.directionMap[d]))

            # Check next path is in bounds. 
            # Probability of collision less than threshold 
            # available and not already visited**
            if(self.isRoutePoint(step, turn, path)):
                # path in one direction found (not end of path)
                found = True 
                # Add to dirns
                turn = turn + 1
                path.append(copy.copy(step))
                self.findLargestPath_step(step, snakes, turn, depth, path, allpaths)

                
        if (len(pathnew) >= depth) or not found:
            print("LARGEST STEP", str(pathnew), str(path), str(step))
            allpaths.append(pathnew)
        
        return copy.copy(found), copy.copy(pathnew)



data = {'game': {'id': '609d47ca-e773-49f9-b3f4-2c52afa4a05c', 'ruleset': {'name': 'solo', 'version': 'v1.0.22', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'royale': {'shrinkEveryNTurns': 0}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'timeout': 500, 'source': ''}, 'turn': 4, 'board': {'height': 11, 'width': 11, 'snakes': [], 'food': [], 'hazards': []}, 'you': {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}}

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


route = bo.findLargestPath([path], allSnakes)
print (route)

# path = self.findLargestPath(original, snakes, turn, foods, depth)

print(bo.markovs[0])
print(bo.combine)

targets = [[0,0], [2,0], [3,9], [9,1]]


logger.timer('== Finish Paths ==')

