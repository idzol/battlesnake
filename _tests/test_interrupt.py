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
    
        # print("DEBUG", dx, dy, t, step, path)
        # Route logic 
        if (self.inBounds(step)):
          if ( # Our prediction logic 
                (((markov[dy, dx] < CONST.pointThreshold) or 
                (t >= board[dy, dx] and 
                markov[dy, dx] >= CONST.routeThreshold)) and 
                not (step in path)) or 
                # Enemy prediction logic 
                (enemy and 
                t >= board[dy, dx] and 
                not (step in path)) 
              ):

            return (True, copy.copy(markov[dy, dx]))
            
        return (False, CONST.pointThreshold)


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
                found, point = self.isRoutePointv2(step, 0, {}, [], enemy)
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
                        found, point = self.isRoutePointv2(step, turn)
                        route = path + [step]
                        if (found):    
                            # New path found 
                            paths_new.append(copy.copy(route))

                # Concatenate new paths 
                paths = paths + paths_new

            # print("SNAKE", snake.getId(), paths)
            snake.setNextSteps(paths)


    # def isRoutePoint_simulate(step, turn, us, them):
    #     if (them):
    #         simulate = np.zeros([h, w], np.intc) 
    #         for t in them: 
    #             simulate[t[1],t[0]] = CONST.routeThreshold


    def simulateBoard_basic(snakes):
        # Set enemy step (outside fxn) 
        # Simulate step 
        pass 

    # check if enemy head / our head on same square 
    # if we are larger, win 


def enemyStrategy(bo, snakes): 
    # (1) select possible paths for enemy
    future = 2 
    dirn_avoid = []
    
    paths = bo.getEnemyFuture(snakes, future)
    # O(dirs * future * snakes)

    oursteps = us.getNextSteps()
    
    sid_us = bo.getIdentity()
    length_us = snakes[sid_us].getLength()
    steps_us = snakes[sid_us].getNextSteps()
    
    for sid in snakes:
        if sid != sid_us:     
            snake = snakes[sid]
            length = snake.getLength()
            steps = snake.getNextSteps()

            
            for ourstep in steps_us:
            # Iterate through our steps 
                for step in steps:
                # Check against enemy steps 
                    safe = True
                    reason = ""
                        
                    if len(step) == len(ourstep):
                    # Look for same turn (same length)

                        # print("STEPS us:%s them:%s" % (ourstep, step)) 
            
                        if step == ourstep:
                            if length > length_us:
                            # Check for collision (we are same / smaller) 
                                safe = False 
                                reason = "head on collision"

                        else: 

                            # Check moves available 
                            turn = len(step)
                            start = ourstep[-1]
                            future = ourstep + step 
                            future.remove(start)

                            found = bo.findEmptySpace(start, future, turn)
        
                            # print("FOUND start:%s turn:%s future%s found %s" % (start, turn, future, found)) 
                
                            # No paths
                            if (not found):
                                safe = False 
                                reason = "no path for us"
            
                
                    if (not safe):
                    # One of the enemy steps is not safe for our step.  Abandon all paths in that direction (overcautious)
                    # TODO: less agressive if we see a path out

                        print ("STEP sid:%s us:%s them:%s reason:%s" % (sid, ourstep, step, reason))
                        for s in steps_us:
                            if ourstep[0] in s: 
                                steps_us.remove(s)
                                dirn_avoid.append(ourstep[0])
                                # dy = ourstep[0][0]
                                # dx = ourstep[0][1]
                                # self.markov[dy,dx] = CONST.routeThreshold

    snakes[sid_us].setNextSteps(steps_us)
    # print("FINAL PATHS", dirn_avoid, steps_us)
    # return directions to avoid (mark as not reachable)
    return dirn_avoid


# def enemyStrategy_chance(self):
    # (2) if our path = 100% (ie. single path)
    # and enemy head < us head distance
        # (stay off wall -- leave space for retreat / exit)

    # (3) logic that says they are 1x square from wall 
    # if each point in probability cloud 
    # then enclosed drops to zero .. 
    # or intersects wtih our path @ 100% 


data = {'game': {'id': '609d47ca-e773-49f9-b3f4-2c52afa4a05c', 'ruleset': {'name': 'solo', 'version': 'v1.0.22', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'royale': {'shrinkEveryNTurns': 0}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'timeout': 500, 'source': ''}, 'turn': 4, 'board': {'height': 11, 'width': 11, 'snakes': [], 'food': [], 'hazards': []}, 'you': {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}}

logger = log()

us = snakeTest()
us2 = snakeTest()
them = snakeTest()

us.setHead([0,6])
us.setBody([[0,7], [0,8], [0,9], [0,10], [1,10]])
us.setBody(us.getBody())

us2.setHead([1, 4])
us2.setBody([[1, 5], [2, 5], [3, 5], [3, 4]])
us2.setHistory(us2.getBody())

them.setHead([7,7])
them.setBody([[7,6],[7,5],[6,5],[6,4],[7,4],[7,3]])
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


#bo.getEnemyFuture(allSnakes, 2)
# print("US", us.getNextSteps())
# print("US2", us2.getNextSteps())
# print("ENEMY", them.getNextSteps())

route = enemyStrategy(bo, allSnakes)
print ("ROUTE", route)


logger.timer('== Finish Strategy ==')

# print(bo.markovs[0])
print(bo.combine)

targets = [[0,0], [2,0], [3,9], [9,1]]

logger.timer('== Finish Paths ==')

