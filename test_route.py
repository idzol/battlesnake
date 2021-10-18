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

import sys

# Set recursion limit
# TODO: Replace with loop if possible ..
sys.setrecursionlimit(10000)


class board():

    width = 11
    height = 11
    trails = np.zeros([height, width], np.intc)
    trails[3] = 10
    trails[:, 3] = 10

    def inBounds(self, a):
        # Check a point (a = [y,x]) is in map bounds

        # Invalid point -- return false
        if (not len(a)):
            return False

        h = self.height
        w = self.width

        try:
            if (0 <= a[0] < h) and (0 <= a[1] < w):
                return True
            else:
                return False

        except Exception as e:
            log('exception', 'inBounds', str(e))

        return False

    def findLargestPath(self, route, turn=1, depth=CONST.lookAhead):
        # Iterate through closed space to check volume
        # **TODO: Include own path as layer in future updateTrails
        # TODO: Introduce panic timers if routing too long
        # TODO: Introduce threat from other snakes into s[dy, dx] -> s[turn][dy, dx] udating predict matrix
        # TODO:  Return best path vs any path (similar to introducing snake threat)

        # print("FINDPATH", str(path), str(turn))
        if (len(route)):
            start = copy.copy(route[-1])

        else:
            return []

        s = copy.copy(self.trails)

        # Look in all directions
        for d in CONST.directions:
            newturn = copy.copy(turn) 
            step = list(map(add, start, CONST.directionMap[d]))
            path = copy.copy(route)
            newpath = []
            dy = step[0]
            dx = step[1]
            
            # Check next path is in bounds, available and not already visited**
            print("NEWSTEP", step)
            if(self.inBounds(step) and \
                    turn >= s[dy, dx]):

                newturn = newturn + 1

                path.append(step)
                newpath = self.findLargestPath_step(step, turn, depth, path)
                
                print("NEWPATH", newpath)
                if (len(newpath) >= depth):
                    # Max path found - Exit search
                    break

        return copy.copy(newpath)


    def findLargestPath_step(self,
                             route,
                             turn=1,
                             depth=CONST.lookAhead,
                             path=[]):

        # If path meets depth, end recursion
        if (len(path) >= depth):
            return path

        start = copy.copy(route)
        pathnew = copy.copy(path)

        # Basic route table
        s = copy.copy(self.trails)

        # Look in all directions
        for d in CONST.directions:

            step = list(map(add, start, CONST.directionMap[d]))
            dy = step[0]
            dx = step[1]

            # Check next path is in bounds, available and not already visited**
            print("STEP", step, path)
            if(self.inBounds(step) and \
                    turn >= s[dy, dx] and \
                    not step in path):

                # Add to dirns
                turn = turn + 1
                path.append(copy.copy(step))
                pathnew = self.findLargestPath_step(step, turn, depth, path)
                
                # print("LARGEST STEP", str(pathnew), str(path), str(step))

            if (len(pathnew) > depth):
                break

        return copy.copy(pathnew)


bo = board()
path = [2, 2]
route = bo.findLargestPath([path])
print("ROUTE", route)
print(str(bo.trails))
