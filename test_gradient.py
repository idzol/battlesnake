
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

    recursion_route = 0

    def updateGradient(self, a, turn=0):

        # Max threshold
        rtmax = CONST.routeThreshold
        h = self.height
        w = self.width

        if (not self.recursion_route):
            # Initialise gradient 
            self.gradient = np.full([h, w], CONST.routeThreshold)
            self.gradient[a[0], a[1]] = 0

        # Max number of turns / boards in prediction matrix
        tmax = CONST.maxPredictTurns - 1
        if (turn > tmax):
            turn = tmax

        dijkstra = self.getDijkstra()
        dt = dijkstra[turn]

        # Exit if timer or recursion exceeded
        rr = self.recursion_route
        self.recursion_route = rr + 1
        if (self.hurry or rr > CONST.maxRecursion):
            return

        if (rr > 0 and not (rr % 500)):
            st = self.getStartTime()
            log('time', 'Gradient 500', st)

            # Timer exceeded
            diff = 1000 * (time.time() - st)
            if diff > CONST.timePanic:
                log('timer-hurry')
                self.hurry = True

        # Iterate through four directions
        for d in CONST.directions:

            a1 = list(map(add, a, CONST.directionMap[d]))

            # Check in bounds
            if (self.inBounds(a1)):

                g0 = self.gradient[a[0], a[1]]
                g1 = self.gradient[a1[0], a1[1]]
                d1 = max(dt[a1[0], a1[1]], 0)

                # Check path is less than route threshold and cheaper than last

                # If target is solid, always solid ..
                # if route_solid()
                if ((d1 < rtmax) and (g0 + d1) < g1):

                    # Update point
                    self.gradient[a1[0], a1[1]] = g0 + d1

                    # Recursion.  Check which prediction matrix to use based on number of turns (t)
                    turn = turn + 1
                    self.updateGradient(a1, turn)

    def updateGradientFix(self, a):
        # BUGFIX: Prevent snake from "seeing through" themselves in predict matrix in a future turn (eg. loop around & think not there)
        for d in CONST.directions:
            a1 = list(map(add, a, CONST.directionMap[d]))
            if (self.inBounds(a1)):
                self.gradient[a1[0], a1[1]] = self.dijkstra[0][a1[0], a1[1]]


bo = board()
path = [2, 2]
route = bo.findLargestPath([path])
print("ROUTE", route)
print(str(bo.trails))