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


class boardTest(board):

    pass 
    # def __init__():


data = {'game': {'id': '609d47ca-e773-49f9-b3f4-2c52afa4a05c', 'ruleset': {'name': 'solo', 'version': 'v1.0.22', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'royale': {'shrinkEveryNTurns': 0}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'timeout': 500, 'source': ''}, 'turn': 4, 'board': {'height': 11, 'width': 11, 'snakes': [], 'food': [], 'hazards': []}, 'you': {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}}

h = 11
w = 11 

us = snake()
us2 = snake()
them = snake()

us.setHead([3,3])
us.setBody([[3,2], [3,1], [3,0], [2,0]])
us2.setHead([6,2])
us2.setBody([[6,1], [6,0], [5,0], [4,0]])
them.setHead([7,7])
them.setBody([[7,6], [7,5]])

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

foods = [[1, 1]]

bo = boardTest()

# trails = np.zeros([h, w], np.intc)
# trails[3] = 10
# trails[:, 3] = 10
# bo.trails = trails 
# print(str(bo.trails))

path = [2, 2]

bo.updateBoards(data, allSnakes) 
bo.updateChance(allSnakes, foods)
bo.updateMarkov(us, allSnakes, foods)


route = bo.findLargestPath([path])

print("ROUTE", route)