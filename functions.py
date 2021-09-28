import random as rand
from typing import Dict
# import numpy as np
# import pandas as pd

# move = getMove(pHead, route.pop(0)) 
def getDirection(a, b): 
    
    move = ""

    # X - left, right [0][X]
    # Y - up, down.   [Y][0] 
    try: 
      ay = a[0]
      ax = a[1]
      by = b[0]
      bx = b[1]
      
      if (bx < ax): 
          move = "left"
      if (bx > ax): 
          move = "right"
      if (by < ay): 
          move = "up"
      if (by > ay): 
          move = "down"

    except: 
      pass 
            
    if (move == ""): 
        # Should never happen 
        moves = ["right", "left", "up", "down"]
        move = rand.choice(moves)
    
    return move


def comparePoints(a: Dict[str, int], b: Dict[str, int]): 

    if(a['x'] == b['x'] and a['y'] == b['y']):
        return True
    else:
        return False 



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

 
# def isSamePoint(a: Dict[str, int], b: Dict[str, int])

def chartPath(b, p):    # b = board(), p = point(x,y)
    pass
    
def setPath():
    pass 

## Load game data 
def initialise_snake(data: dict) -> str:
    pass 


# Invert coordinate system 
def printMap(m):
    # Iterate through map array backwards
    md = []
    for i in range(1, len(m)+1): 
        md.append(m[-i])
        print(str(m[-i]))

    return md 

def raiseError(e):
    # error_status = True 
    # error_text = e
    print("ERROR: " + str(e))
    return True

