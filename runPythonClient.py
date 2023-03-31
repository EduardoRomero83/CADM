import os
import sys
import time

if (len(sys.argv)) != 10:
    print("This command takes 9 parameters: python runPythonClient.py" +
          " NumberOfSamples TestAcc?y/n treeName ERGMODE metrics dicSplits tableSplits replicas dataset\n")
    print("Instead received " + str(len(sys.argv) - 1) + " parameters")
    exit(1)

numSamples = sys.argv[1]
test = 'y' in sys.argv[2]
treename = sys.argv[3]
ergmode = sys.argv[4]
pidfile = "./temps/pid" + ergmode.strip()
metrics = 'y' in sys.argv[5]
dicSplits = sys.argv[6]
tableSplits = sys.argv[7]
replicas = sys.argv[8]
dataset = sys.argv[9]
pid = 0
numCores = int(dicSplits) * int(tableSplits) * int(replicas)

print(pidfile)
cmd = "python3 server/pythonClient/client.py " + numSamples + " " + str(numCores) + " " + replicas + " " + dicSplits + " " + tableSplits + " " + ergmode + " " + dataset + " " + treename + ";"
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
time.sleep(30)

if test:
    cmd = "python3 server/testaccuracy/ta.py " + numSamples + " >> ./ResearchData/raw/" + treename + ".acc.server.txt"
    print("Test Accuracy")
    os.system(cmd)




