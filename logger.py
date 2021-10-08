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
    'def':[1, "ERROR", "Test. %d %d %s"],

    'time':[2, "TIME"],

    'timer-hurry':[2, "INFO", "Move time reached CONST.timePanic"],

    # Server 
    'healthcheck':[5,"INFO", "Healthcheck - OK"],
    'interrupt':[3,"INTERRUPT"," %s"],
    'start':[3,"START", " %s"],
    'end':[3,"END", " %s"],
    'move':[3,"MOVE", " %s"],
    'shout':[3,"SHOUT", " %s"],
    
    # Board 
    'updateboardsnakes-warn':[3, "WARN", "Enemy snake head not defined. %s"],

    'predict-update':[3, "INFO", "%s"],
    'predict-new':[6,"PREDICT POINT", "%s: %s: %s"],
    'predict-erase':[6,"PREDICT ERASE", "%s: %s: %s"],
    
    # Routing 
    'route-fromto':[6,"FROM TO", " %s %s"],
    'route-return':[6,"ROUTE", " %s"],
    'paths':[6,"PATH", " %s"],
    'path-target':[6,"TARGET", " %s"],
    'route-dijkstra-sum':[6,"DSUM"," %s-%s-%s = %d"],
    'route-findclosestwall':[6,"WALLPATH"," %s %s"],
    'route-leastline-dsum':[6,"DSUM"," %s %s-%s = %d"],
    'route-gradient':[3,"PATH", " Gradient %s"],
    'route-complex-step':[6,"ROUTE COMPLEX", "from: %s to: %s"],
    'route-complex-path':[6,"ROUTE COMPLEX", "path: %s"],

    # Strategy 
    'strategy-update':[5,"STRAT", "%s\n%s"],
    'strategy-iterate':[5,"STRAT", "Updated - %s"],
    'strategy-eat':[6,"EAT", " %s %s %s %s"],
    'strategy-attack':[6,"ATTACK", " %s %s %s %s"],
    'strategy-kill':[6,"KILL", " %s %s %s %s"],
    'strategy-defend':[6,"DEFEND", " %s %s %s %s"],
    'strategy-survive':[6,"SURVIVE", " %s %s %s %s"],
    'strategy-findwall':[5,"FINDWALL", " Target %s"],
    'strategy-trackwall':[5,"TRACKWALL", " w:%s h:%s l:%s d:%s r:%s p:%s - Target %s"],

    # Map 
    'map':[2, "%s"],

    # Snake
    'snake-showstats':[2, "SNAKE", """
  Health: %d
  Hunger: %d
  Aggro: %d
  Threat: %d
  Head: %s
  Target: %s
  Route: %s
  Strategy: %s
  Direction: %s"""],
  
    # Functions 
    # 'findbestpath-usage':[4,"WARN", "findBestPath(self, a, b) - dict received when list array expected"],
    
    # Items 
    'itemclass-typewarning':[4, "WARN","item(t,p) expects location as dict"],
    

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
        output = msg[1] + ": {:.2f} ms | ".format(diff) + vars[0]

    # Map function
    elif(src == 'map'):   
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
          print(e)
  
    # General print function 
    else:          
        output = msg[1] + ": " + msg[2] % vars


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
