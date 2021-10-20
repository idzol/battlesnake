import random as rand

# from typing import Dict
import numpy as np

from operator import add
from collections import OrderedDict
      
import time as time 
import copy as copy 

import functions as fn
from logger import log

import constants as CONST

from snakeClass import snake
from boardClass import board

# === STATE MACHINE ===
# Core decision making engine

    # Eat -- focus on maximising snake size and restoring health
    # Attack -- larger size, full health, stay close to head, intercept food, look for kill
    # Kill -- opportunity to kill (eg. head to head collision)
    # Defend -- smaller snake .. 
    # Survive -- limited moves left 
    # .. 
    
# Changes strategy (state machine) based on external influence 
def checkInterrupts(bo:board, snakes):

    # Return your snake 
    you = bo.getIdentity()
    sn = snakes[you]
    health = sn.getHealth() 
    aggro = sn.getAggro()
    path = sn.getRoute()
    length = sn.getLength()

    strategylist, strategyinfo = sn.getStrategy() 
    interruptlist = []

    numsnakes = len(snakes)
    minlength = CONST.controlMinLength
    larger = CONST.controlLargerBy
    
    reason = []

    # Kill interrupt -- larger than 
    t = killPath(bo, snakes)
    if (len(t)):
        interruptlist.insert(0, ['Kill', 'Collide'])
        strategyinfo['killpath'] = t
        reason.append('killpath was identified')

    # Kill interrupt -- cut off path 
    t = enemyEnclosed(bo, sn, snakes)
    if (len(t)):
        interruptlist.append(['Kill', 'Cutoff'])
        strategyinfo['killcut'] = t
        reason.append('enclosed enemy was identified')

    # t = foodNearby(bo, sn, snakes)
    # if (len(t)):
    #   interruptlist.insert(0, ['Eat', ''])

    # Critical health interrupt -- get food
    if (health < CONST.healthCritical):
        interruptlist.insert(0, ['Eat', ''])
        reason.append('health was critical')



    # Control interrupt -- control board 
    if (health > CONST.healthLow and largestSnake(bo, snakes, minlength, larger) and numsnakes == 2):
        interruptlist.append(['Control', 'Box'])
        for sndata in snakes: 
          sid = snakes[sndata].getId() 
          if sid != you:
            strategyinfo['enemy'] = snakes[sndata]

        reason.append('duel, '+str(minlength)+' length and larger by '+str(larger))


    if (largestSnake(bo, snakes, minlength, larger) and health > CONST.healthMed):
        interruptlist.append(['Idle', 'Centre'])
        reason.append('largest snake by '+str(minlength)+' length and larger by '+str(larger))

    # Growth interrupt when small
    if (health < CONST.healthHigh and length < CONST.growLength): 
        interruptlist.append(['Eat', ''])
        reason.append('health is less than high and length less than '+str(CONST.growLength))

    # # No threats & high health
    # if (health >= CONST.healthLow): 
    #     interruptlist.append(['Idle', 'Centre'])
    #     reason.append('health is high')

    # Health interrupt general 
    if (health < CONST.healthLow): 
        interruptlist.append(['Eat', ''])
        reason.append('health is less than high')

    # Survive interuupt 
    if (numMovesAvailable(bo, sn) < length):
        interruptlist.append(['Survive', ''])
        reason.append('less than X moves available')

    # Interrupt triggered
    if (len(interruptlist)):     
        log('interrupt', str(interruptlist), str(reason))

    sn.setStrategy(strategylist, strategyinfo) 
    sn.setInterrupt(interruptlist) 
    # return (strategy, strategyinfo)

        # PREDICTION 
        # One path - certainty 100% 
        
        # GENERAL 
        # [intent] - moves that reduce # enemy paths
        
        # SURVIVE 
        # [intent] - paths that have most options 
        # pathTree() -> path branches by length

        # TRAPS 
        # Crawl Wall 
        # [10,9],  wall 
        # [0,1] -> [1,w] -> [h, w-1] -> [h-1, 0]
      
        # STALK 
        # Stay within 2 - 8 squares 
        # Find food 
        # Stay within 2... 

        # WALL OF DOOM 
        # patrol A - B - C ...
        # simple mode 
        # if dist > 2 to body, +1 each turn  

        # Collision & enemy larger
        # elif (pathThreat(bo, start, path, aggro)): 
        #     strategy = ['Idle', 'Wall']
        #     interrupt = True 



bo = board() 
sn = snake()
snakes = ()
foods = [[1, 1], [2, 2]]

depth = CONST.lookAhead   
foodsort = fn.findClosestItem(foods, start)


# No food -- change strategy
# Sort by closest food
if(len(foodsort)):
    target = findBestFood(foods, bo, sn, snakes)
    if(not len(target)):
        # Try next food 
        foodsort.pop(0)
        strategylist.insert(0, strategy)
    

def findBestFood(foods, bo, us, snakes): 
    # Check if bigger snakes are closer to the food 
    #  # REWRITE .. 
    #  Eat strategy
    #     Closest 
    #     # Work out how many food we can get to before enemy 
    #     Faster than enemies  
    #     Multiples 
    #        Most items 
    #     Safest 
    #        Big snakes 
    #        Corners 
    #     Waiting 
    #        Least threat quadrant 
    #     etc..


    start = us.getHead()
    length = us.getLength()

    foodsort = copy.copy(foods)
    target = []
   
    # 1) Closest food 
    # Abandon closest if enemy snakes are closer & larger 
    while not len(target) and len(foodsort): 

      # Gen next food  
      f = foodsort.pop(0) 
      target = copy.copy(f) 
      
      # Check we can route to location 
      r, w = bo.route(start, f)
      
      if (len(r)): 
        # Route exists 
        reason = 'route exists'
        usdist = len(fn.getPointsInRoute(r))

        # Check each snake to see if larger / closer snake  
        # Find furthest food from other snakes 
        for sid in snakes:
          fsnake = snakes[sid]
          ftype = fsnake.getType()
          flen = fsnake.getLength()   
          if (ftype == 'enemy'):
            fhead = fsnake.getHead()
            # Append to heads -- used later if no path found 
            fdist = fn.distanceToPoint(fhead, f)

            # Enemy is same / larger and equal / closer 
            if (fdist < CONST.foodThreat and fdist <= usdist and flen > length):
              # Ignore , live to fight another day 
              reason = 'enemy larger & very close'
              target = []

            # Enemy is closer 
            elif(fdist < usdist):  
              reason = 'enemy is closer'
              # Ignore , enemy will beat us there 
              target = []

      else:
        reason = 'no route'

    # 2) Uncontested food 
    # Find food furthest from enemy snakes 
    # TODO: Check if covered by above

    # 3) Empty space -- Maximise control and wait for next food spawn.  See ['Control', 'Space']
 
    # print("EAT AVOID")
    # print(str(fsnake), str(ftype), str(flen), str(fdist))
    print("EAT STRATEGY", target, reason) 
    return copy.copy(target)

 
def controlSpace(bo, us, snakes):
 
    start = us.getHead()
    target = [] 

    # Find all enemy heads 
    heads = []
    # Find distance to closest head 
    dist_min = bo.width * bo.height

    for sid in snakes:
      fsnake = snakes[sid]
      ftype = fsnake.getType()   
      if (ftype == 'enemy'):
        fhead = fsnake.getHead()
        heads.append(fhead)
        distance = fn.distanceToPoint(fhead, start)
        dist_min = min(dist_min, distance)

    # Look for each location 
    control_max = 0
    dist_final = []
    for d in CONST.directions: 
        # maximise board control - stepwise max 
        step = list(map(add, start, CONST.directionMap[d]))
        if (bo.inBounds(step)):
          # Return board control matrix 
          dist = bo.closestDist(step, heads)
          control = np.sum(dist)

          # Save location wtih max control 
          if control > control_max:
              control_max = control
              target = copy.copy(step) 
              dist_final = copy.copy(dist)
              # board_dist = copy.copy(dist)

          if dist_min < CONST.foodThreat: 
              # If too close to enemy, abandon 
              target = [] 


    # Board max - brute force search   
    # control_max = 0
    # for h in range(0, height):
    #     for w in range(0, width):
    #       start = [h, w]
    #       dist = bo.closestDist(start, heads)
    #       control = np.sum(dist)
    #       # Save location wtih max control 
    #       if control > control_max:
    #           control_max = control
    #           target = copy.copy(start) 
    #           # board_dist = copy.copy(dist) 

    return copy.copy(target)


# == GET / SET == 

data = {'game': {'id': '609d47ca-e773-49f9-b3f4-2c52afa4a05c', 'ruleset': {'name': 'solo', 'version': 'v1.0.22', 'settings': {'foodSpawnChance': 15, 'minimumFood': 1, 'hazardDamagePerTurn': 0, 'royale': {'shrinkEveryNTurns': 0}, 'squad': {'allowBodyCollisions': False, 'sharedElimination': False, 'sharedHealth': False, 'sharedLength': False}}}, 'timeout': 500, 'source': ''}, 'turn': 4, 'board': {'height': 11, 'width': 11, 'snakes': [{'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}], 'food': [{'x': 2, 'y': 6}, {'x': 5, 'y': 5}], 'hazards': []}, 'you': {'id': 'gs_VYFDmY6qCM6MH6KJ7jKKybg3', 'name': 'idzol-dev', 'latency': '326', 'health': 96, 'body': [{'x': 1, 'y': 9}, {'x': 1, 'y': 8}, {'x': 1, 'y': 7}], 'head': {'x': 1, 'y': 9}, 'length': 3, 'shout': '', 'squad': ''}}

identity = data['you']['id']

# Set up snake 
us = snake()
us.__init__()
bo.setIdentity(identity)
us.setId(identity)
us.setType("us")

# Set up other snakes 
# allSnakes[copy.copy(identity)] = ourSnek
snakes = data['board']['snakes']
for sndata in snakes: 
    if sndata['id'] != ourSnek.getId():
      sn = snake() 
      identity = sndata['id']
      sn.setId(identity)
      sn.setType("enemy")
      sn.setEnemy(sndata)
      allSnakes[copy.copy(identity)] = copy.deepcopy(sn)

bo = board()
path = [2, 2]
route = bo.findLargestPath([path])
print("ROUTE", route)
print(str(bo.trails))