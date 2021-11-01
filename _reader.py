try: 
    f = open("env", "r")
    lines = f.read().splitlines()

    vars = []
    # for line in lines:
    # line.strip('\n')    
    vars = lines[0].split(':')
 
    environment = vars[0]
    snakename = vars[1] 
    

except: 
    environment = 'localhost'
    snakename = 'idzol dev' 

print("ENV: '%s' '%s'" % (environment, snakename))
 