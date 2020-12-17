import os
import sys
import time

if (len(sys.argv)) != 6:
    print("This command takes 5 parameters: python runServer.py NumberOfSamples Test?y/n treeName ERGMODE metrics\n")
    exit()

numSamples = sys.argv[1]
test = 'y' in sys.argv[2]
treename = sys.argv[3]
ergmode = sys.argv[4]
pidfile = "./temps/pid" + ergmode.strip()
metrics = 'y' in sys.argv[5]
pid = 0

print(pidfile)
cmd = "python3 server/pythonClient/client.py " + numSamples + ";"
print("Run Client")

ready = False
if not metrics:
    ready = True

while not ready:
    pidcond = open(pidfile,"r", os.O_NONBLOCK).readlines()[0]
    if "F" in pidcond:
        print("spinning")
        time.sleep(30)
    else:
        pid = int(pidcond)
        ready = True

print("Found PID")
#while not psutil.pid_exists(pid):
#    time.sleep(2)

os.system(cmd)
time.sleep(120)

if test:
    cmd = "python3 server/testaccuracy/ta.py " + numSamples + " >> ./ResearchData/raw/" + treename + ".acc.server.txt"
    print("Test Accuracy")
    os.system(cmd)




