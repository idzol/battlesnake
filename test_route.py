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

from snakeClass import snake
from boardClass import board

class snakeTest(snake):
    pass 


class boardTest(board):
    pass 
    # def __init__():
    
    def selectBestPath(self, routes):

    if weight < CONST.threshold 
    
    min route ..?


      selectBestPath()
      eg. > Total route 
      eg. No route
      eg. Chase tail
      eg. Kill path (100%) vs route padded path 
      eg. Certain collision (Body) vs probability 
      eg. Some probabiliy vs no probability 
         (make sure we're still focused on headon collision)



data = {'game': {'id': '609d47ca-e773-49f9-b3f4-2c52afa4a05c', 'ruleset': {'name': 'solo', 'version': 'v1.0.22', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'royale': {'shrinkEveryNTurns': 0}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'timeout': 500, 'source': ''}, 'turn': 4, 'board': {'height': 11, 'width': 11, 'snakes': [], 'food': [], 'hazards': []}, 'you': {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}}


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

bo.setStartTime()

log('time', '== Update Boards ==', bo.getStartTime())
bo.updateBoards(data, us, allSnakes, foods) 
bo.updateChance(allSnakes, foods)
bo.updateMarkov(us, allSnakes, foods)
bo.updateDijkstra(us)
log('time', '== Finish Boards ==', bo.getStartTime())

path = [2, 2]
route = bo.findLargestPath([path])
print("ROUTE", route)
