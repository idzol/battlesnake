## CLEANUP
# log("path-target", str(finish))
# log('time', 'Before Route', bo.getStartTime())
# log('time', 'After Route', bo.getStartTime())

import numpy as np

import time as time 
from time import gmtime, strftime

import constants as CONST 

# import logging 
# TODO: Replace with logger -- https://docs.python.org/3/howto/logging.html


global messages
messages = {
    # Time 
    'time':[3, "TIME"],
    'timer-hurry':[6, "TIME", "Move time reached CONST.timePanic"],

    # Server 
    'healthcheck':[3,"INFO", "Healthcheck - OK"],
    'start':[3,"START", " %s"],
    'end':[3,"END", " %s"],
    'move':[3,"MOVE", " %s"],
    'shout':[3,"SHOUT", " %s"],
    
    # Board 
    'updateboardsnakes-warn':[6, "WARN", "Enemy snake head not defined. %s"],

    'predict-update':[6, "->INFO", "%s"],
    'predict-new':[6,"->PREDICT POINT", "%s: %s: %s"],
    'predict-erase':[6,"->PREDICT ERASE", "%s: %s: %s"],
    
    'enclosed':[6,"->ENCLOSED", "%s %s"],
    'enclosed-sum':[6,"->ENCLOSED SUM", "%s"],

    # Routing 
    'route':[5,"-->ROUTE"," %s r:%s w:%s"],
    'route-fromto':[5,"-->FROM TO", " %s %s"],
    'route-return':[5,"-->ROUTE", " %s %s"],
    'paths':[5,"-->PATH", " %s"],
    'path-target':[5,"-->TARGET", " %s"], 
    'route-dijkstra-sum':[5,"-->DSUM"," %s-%s-%s path:%s = %d"],
    'route-findclosestwall':[5,"-->WALLPATH"," %s %s"],
    'route-leastline-dsum':[5,"-->LDSUM"," %s %s-%s = %d"],
    'route-gradient':[5,"-->PATH", " Gradient %s"],
    'route-complex-step':[5,"-->ROUTE COMPLEX", "from: %s to: %s"],
    'route-complex-path':[5,"-->ROUTE COMPLEX", "path: %s"],

    'make-move':[3,"->MAKE MOVE"," start:%s target:%s next:%s move:%s status:%s"],

    # Strategy 
    'interrupt':[4,"->INTERRUPT","\nInterrupts:%s \nReasons:%s"],
    'strategy':[4,"->STRATEGY", "\nStrategy:%s \n Reason:%s \n Strategylist: %s,  Strategyinfo:%s"],
    'strategy-update':[4,"->STRATEGY", "\n%s"],
    'strategy-eat':[4,"-->EAT", " %s"],
    'strategy-attack':[4,"-->ATTACK", " %s %s %s %s"],
    'strategy-killpath':[4,"-->KILL", "%s head:%s length:%s target:%s"],
    'strategy-defend':[4,"-->DEFEND", " %s %s %s %s"],
    'strategy-control':[4,"-->CONTROL", " %s %s %s"],
    'strategy-survive':[4,"-->SURVIVE", " %s %s %s %s"],
    'strategy-route':[4,"-->ROUTE", " %s: %s %s"],
    'strategy-taunt':[4,"-->SURVIVE", " %s"],
    'strategy-findcentre':[4,"-->FINDCENTRE", " Target %s"],
    'strategy-findwall':[4,"-->FINDWALL", " Target %s"],
    'strategy-trackwall':[4,"-->TRACKWALL", " w:%s h:%s l:%s d:%s r:%s p:%s - Target %s"],

    # Map 
    'map':[3, "%s"],
    'map-predict':[6, "%s"],
    'map-debug':[6, "%s"],

    # Snake
    'snake-showstats':[3, "SNAKE", """
  Health: %d
  Hunger: %d
  Aggro: %d
  Head: %s
  Target: %s
  Route: %s
  Strategy: %s
  Last Move: %s"""],
  
    # Functions 
    # 'findbestpath-usage':[4,"WARN", "findBestPath(self, a, b) - dict received when list array expected"],
    
    # Items 
    'itemclass-typewarning':[4, "WARN","item(t,p) expects location as dict"],
    
    # Exceptions 
    'exception':[2, "WARN","%s: %s"],
    

}

# Logger

def log(src, *vars):
    
    global messages

    llc = CONST.logLevelConsole
    llp = CONST.logLevelPrint
    logfile = CONST.logFile
    
    msg = messages[src]
 
    output = ""

    # Time function 
    if(src == 'time'):
        time.time()
        diff = 1000 * (time.time() - vars[1]) 
        try: 
            output = msg[1] + ": {:.2f} ms | ".format(diff) + vars[0]
        except Exception as e:       
            log('exception', 'log#1', str(vars[0]) + str(e))
  
    # Map function
    elif(src.startswith('map')):
        try: 
          m = vars[1]
          h = len(m)
          w = len(m[0])

          md = np.zeros([h,w],np.intc)
          for y in range(0, h):
            for x in range(0, w): 
              md[h-y-1,x] = m[y,x]
            
          output = str(vars[0]) + "\n" + str(md)
            
        except Exception as e:       
          log('exception', 'log#2', str(vars[0]) + str(e))
  
    # General print function 
    else:          
        try:
          output = msg[1] + ": " + msg[2] % vars
        except Exception as e:       
          log('exception', 'log#3', str(vars[0]) + str(e))
  

    # Print to console 
    if (llc >= msg[0]):
        print(output)
    
    # Print to log 
    if (llp >= msg[0]):
        t = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        f = open(logfile, "a")
        f.write(t+"\t"+output+"\n")
        f.close()

    # except Exception as e :    
    #     print("ERROR: Incorrect number or type of keywords passed to logger(). ", e)
