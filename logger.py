import time as time 
from time import gmtime, strftime

import constants as CONST 

# import logging 
# TODO: Replace with logger -- https://docs.python.org/3/howto/logging.html


global messages
messages = {
    'def':[1, "ERROR", "Test. %d %d %s"],

    'time':[2, "TIME"],

    # Server 
    'healthcheck':[5,"INFO", "Healthcheck - OK"],
    'interrupt':[3,"INTERRUPT"," %s"],
    'start':[3,"START", " %s"],
    'end':[3,"END", " %s"],
    'move':[3,"MOVE", " %s"],
    'shout':[3,"SHOUT", " %s"],
    
    # Board 
    'updateboardsnakes-warn':[3, "WARN", "Enemy snake head not defined. %s"],

    # Routing 
    'route-fromto':[6,"FROM TO", " %s %s"],
    'route-return':[6,"ROUTE", " %s"],
    'paths':[6,"PATH", " %s"],
    'path-target':[6,"TARGET", " %s"],
    
    # 'findbestpath-debug':[3,"PATH", " %s:%s:%s"],
    'route-gradient':[3,"PATH", " Gradient %s"],
    
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
 
    #  try:
    if(src == 'time'):
        time.time()
        diff = 1000 * (time.time() - vars[1]) 
        output = msg[1] + ": {:.2f} ms | ".format(diff) + vars[0]

    else:            
        output = msg[1] + ": " + msg[2] % vars

    # TODO:  if key does not exist 
      # 'default', "%s"


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
