
# import random as rand
# import constants as CONST 
# from typing import Dict
# import pandas as pd

import numpy as np
import copy as copy 

from logger import log


def distanceToPoint(a, b):
    if(isinstance(a,dict) or isinstance(b,dict)):
      print("ERROR: distanceToPoint(a,b) expecting array list, received dict)")
      return -1 

    try:

      ax = a[1]
      bx = b[1]
      ay = a[0]
      by = b[0]
    
      dx = abs(ax - bx)
      dy = abs(ay - by)
      d = dx + dy
      return d

    except Exception as e:
      log('exception', distanceToPoint, str(e))  
      return -1


# def distanceToPointComplex(a, b):
    # if objects in the way .. 
    

def findClosestItem(foods, start):
  # Return sorted list of items (foods) closest to point (start)

  # print("FIND CLOSEST ITEM")
  # print(str(start), str(foods))

  fooddict = {}
  for food in foods:
      dist = distanceToPoint(start, food)
      fooddict[str(food)] = dist
          
  foodsort = dict(sorted(fooddict.items(), key=lambda item: item[1]))
  
  foodlist = []
  for fs in foodsort:
      try: 
          y, x = fs.strip('][').split(', ')
          y = int(y)
          x = int(x)
          foodlist.append([y, x])
      except Exception as e:
          log('exception', 'findClosestItem', str(e))

  # print(str(foodlist))
  
  return copy.copy(foodlist)

# == DEPRECATE / DELETE == 

foods = [[5, 5], [2, 1], [1, 2], [9, 3]]
start = [2, 2]
closest = findClosestItem(foods, start)
print(closest)

