
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

# from snakeClass import snake

from boardClass import board
from snakeClass import snake

global perf

perf = {}
perf['pathProbability_markov_step'] = 0
perf['pathProbability_markov'] = 0
perf['predictMove_step'] = 0
perf['updateMarkov_step'] = 0

class snakeTest(snake):
    pass 


class boardTest(board):
    pass 

    def updateBoardClass(self, us, snakes, foods):
        
        w = self.width
        h = self.height

        # SNAKES 
        snakeboard = np.zeros((h, w), np.intc)
        for skid in snakes:

            sk = snakes[skid]
            if sk.getType() != 'us':
                # print (str(sk))
                body = sk.getBody()
                for pt in body:
                    px = pt[1]
                    py = pt[0]

                    snakeboard[py, px] = CONST.legend['enemy-body']

                try:
                    head = sk.getHead()
                    px = head[1]
                    py = head[0]
                    # self.snakes[h-py-1, px] = self.legend['enemy-head']
                    snakeboard[py, px] = CONST.legend['enemy-head']

                except Exception as e:
                    log('exception', 'updateBoardSnakes', str(e))

        # YOU 
        youboard = np.zeros((h, w), np.intc)

        body = us.getBody()
        for pt in body:
            px = pt[1]
            py = pt[0]
            youboard[py, px] = CONST.legend['you-body']

        try:
            head = us.getHead()
            px_head = head[1]
            py_head = head[0]
            youboard[py_head, px_head] = CONST.legend['you-head']

        except Exception as e:
            log('exception', 'updateBoardsYou',
                'INFO: Your snake head not defined. ' + str(e))

        # ITEMS 
        itemboard = np.zeros((h, w), np.intc)
        for fd in foods:

            px = fd[1]
            py = fd[0]
            # self.items[h-py-1, px] = self.legend['food']
            itemboard[py, px] = self.legend['food']

        # for hd in hds:
        #     px = hd[1]
        #     py = hd[0]
        #     # self.items[h-py-1, px] = self.legend['hazard']
        #     itemboard[py, px] = self.legend['hazard']

        rs = CONST.routeSolid
        self.you = copy.copy(youboard)
        self.snakes = copy.copy(snakeboard)
        self.items = copy.copy(itemboard)
        self.solid = rs * np.ceil(youboard / (youboard + 1) + snakeboard / (snakeboard + 1))
        self.combine = youboard + snakeboard + itemboard
        
        return copy.copy(self.combine)


def findBestFood(foods, bo, us, snakes): 

    # How many moves until we believe a target
    targetConfidence = 2 
    # Check if food under threat (ie. snake enroute) 
    foodthreat = {}
    # Init dict - empty => null 
    for food in foods: 
        foodthreat[str(food)] = []

    start = us.getHead()
    length = us.getLength()
    
    foodsort = copy.copy(foods)
    target = []
    
    # FIX:  Temporary - return closest 
    # f = foodsort[0] 
    # target = copy.copy(f) 
    # print("EAT STRATEGY", f, foods) 
    # return f 

    # Check which sneks are targeting which food  
    for snid in snakes:
        # Get snake
        sn = snakes[snid] 
        head = sn.getHead()
        if sn.getType() != 'us': 
            # Reset target
            sn.setTarget([])
            # Check each food 
            for food in foods:
              history = sn.getHistory()
              history.insert(0, sn.getHead())
              a = []
              # If last three paths to food are descending
              if (len(history) > targetConfidence): 
                for i in range(0, targetConfidence + 1):
                  a.append(fn.distanceToPoint(food, history[i]))

              # Check ascending - ie. recent locations are closser 
              dist_sort = copy.copy(a)
              dist_sort.sort() 
                  
              
              if (a == dist_sort):
                  # Check if closer than existing target 
                  target_last = sn.getTarget()
                  dist_last = bo.height + bo.width
                  if (len(target_last)):
                    dist_last = fn.distanceToPoint(history[0], target_last)

                  # Check new target is closer 
                  if a[0] < dist_last or not len(target_last):
                    dist_enemy = copy.copy(a[0])
                    len_enemy = sn.getLength()
                    foodthreat[str(food)].append({'length':len_enemy, 'dist':dist_enemy})
                    sn.setTarget(food)
                    print("FOOD TARGET", sn.getId(), sn.getTarget())
                    
    # Check foods for the closest without threat 
    target = []
    for food in foods: 
        # Route exists   
        r, w = bo.route(start, food)
        if (len(r)): 

            reason = 'route exists'
            dist = len(fn.getPointsInRoute(r))
        
            # Threat, enemy closer & smaller - pursue??
            # Threat, enemy closer 
            abandon = False 
            if str(food) in foodthreat:
                # t = [len_enemy, dist_enemy]
                threats = foodthreat[str(food)]
                for t in threats:
                    print("FOOD", food, t)

                    len_enemy = t['length']
                    dist_enemy = t['dist']
                    
                    # Check other snakes targeting food 
                    if (len(t)):
                        if dist_enemy < dist:
                            abandon = True
                            reason = 'abandon - enemy closer'
                            
                        elif len_enemy >= length and dist_enemy <= dist:
                            abandon = True
                            reason = 'abandon - enemy larger & same dist' 

            if not (abandon):
                # Exit search (ie. for food in foods)
                target = food 
                break
                
        else:
            reason = 'no route'
        
        return copy.copy(target)

    #  Ignore Food in corners
    #  * IF enemy approacing AND dist < N (closeby)

    # Empty space -- Maximise control and wait for next food spawn. 
    #  * See ['Control', 'Space']
    print("EAT STRATEGY", food, reason)        
    return copy.copy(target)


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

bo = boardTest()

CONST.minProbability = 1

bo.setStartTime()

log('time', '== Update Boards ==', bo.getStartTime())
bo.updateBoards(data, us, allSnakes, foods) 
# sboard, fboard = bo.updateBoardClass(self, snakes, foods)
# combine = bo.updateBoardObjects(us, allSnakes, foods)

bo.updateChance(allSnakes, foods)
bo.updateMarkov(us, allSnakes, foods)
bo.updateDijkstra(us)
log('time', '== Finish Boards ==', bo.getStartTime())

ma = copy.copy(bo.markovs)

food = findBestFood(foods, bo, us, allSnakes)

print("COMBINE")
print(str(bo.combine))
print("FOOD")
print(food)

  #  Eat 

  #     * if snek targeting AND larger 
  #     * then abandon 

  #     * Food strat (corner)
