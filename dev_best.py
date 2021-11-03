
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

# from snakeClass import snake

from boardClass import board
from snakeClass import snake


class snakeTest(snake):
    pass 


class boardTest(board):
    
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
        rr_max = 2 # w + h  

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
                    if bo.inBounds(step):
                        dot_weight = copy.copy(dot['weight'] + self.markovs[dot_length][step[0]][step[1]])
                    
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
        print(best_length)
        print(best_weight)
        
        # Routing 
        target = [10,0]
        print(best[str(target)]['path'], best[str(target)]['weight'])

        # Save board        
        self.best = best            

data = {'game': {'id': '609d47ca-e773-49f9-b3f4-2c52afa4a05c', 'ruleset': {'name': 'solo', 'version': 'v1.0.22', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'royale': {'shrinkEveryNTurns': 0}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'timeout': 500, 'source': ''}, 'turn': 4, 'board': {'height': 11, 'width': 11, 'snakes': [], 'food': [], 'hazards': []}, 'you': {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}}

# Snakes -- {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}
# Food -- {'x': 2, 'y': 6}, {'x': 5, 'y': 5}

us = snakeTest()
us2 = snakeTest()
them = snakeTest()

us.setHead([3,3])
us.setBody([[3,2], [3,1], [3,0], [2,0]])
us.setHistory([[3,2], [3,1], [3,0], [2,0]])
us2.setHead([6,3])
us2.setBody([[6,2], [6, 1], [6,0], [5,0], [4,0]])
# us2.setHistory([[6,1], [6,0], [5,0], [4,0]])
us2.setHistory([[6,2], [6,1], [6,0], [5,0], [4,0]])

them.setHead([7,7])
them.setBody([[7,6], [7,5]])
# them.setHistory([[7,6], [7,5]])
them.setHistory([[7,6], [7,5], [7,4]])

sn_body = us.getBody()
enemy_body = them.getBody()

us.setType('us')
us.setId('ourSnek')
us2.setId('enemySnek1')
them.setId('enemySnek2')
them.setBody([[7,6], [7,5]])

allSnakes = {
  'ourSnek1':us,
  'enemySnek1':us2,
  'enemySnek2':them
}

# foods = [[6,6]]
foods = [[2,2], [4,4], [6,6]]

bo = board()

CONST.minProbability = 1

bo.updateBoards(data, us, allSnakes, foods) 
# sboard, fboard = bo.updateBoardClass(self, snakes, foods)
# combine = bo.updateBoardObjects(us, allSnakes, foods)

bo.updateChance(allSnakes, foods)
bo.updateMarkov(us, allSnakes, foods)
bo.updateDijkstra(allSnakes)

ma = copy.copy(bo.markovs)
bo.updateBest(us.getHead())

routes = bo.continuePath([us.getHead()], allSnakes, foods)

r_sort = sorted(routes, key=lambda d: d['weight']) 

# r_sort = sorted(routes, key='weight')
for r in r_sort:
    print(r['weight'], r['length'])


print("COMBINE")
print(str(bo.combine))

  #  Eat 

  #     * if snek targeting AND larger 
  #     * then abandon 

  #     * Food strat (corner)
