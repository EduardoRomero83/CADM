import math
import os
import sys
import subprocess
import time

#Check args
if (len(sys.argv)) != 11:
    print("This command takes 10 parameters: python runServer.py treeName mpc NumberOfSamples ERGMODE performanceMetrics(y/n) dicSplits tabSplits replicas dataset coresAvailable\n")
    print("Instead received " + str(len(sys.argv) - 1) + " parameters")
    exit(1)

treeName = sys.argv[1]
mpc = sys.argv[2]
numSamples = sys.argv[3]
ergmode = sys.argv[4]
metrics = 'y' in sys.argv[5]
dicSplits = sys.argv[6]
tabSplits = sys.argv[7]
replicas = sys.argv[8]
dataset = sys.argv[9]
coresAvailable = sys.argv[10]

pathSizeFile = "./metadata/" + treeName + ".numpaths.txt"
f = open(pathSizeFile)
nums = f.readlines()
f.close()

numClusterFile = "./metadata/" + treeName + ".numClustersPerFile.txt"
f = open(numClusterFile)
numClustersPerFile = int(f.readlines()[0])
f.close()

numPathFile = "./metadata/" + treeName + ".numPathsPerFile.txt"
f = open(numPathFile)
numPathsPerFile = int(f.readlines()[0])
f.close()

finalNumBits = str(int(math.floor(math.log(int(nums[0]),2)) + 3))
port = 7878

cmd = []
cmd2 = []
statements = []

if dataset == "mnist":
    nb = "784"
    numclasses = "10"
elif dataset == "traffic":
    nb = "11"
    numclasses = "7"
else: # dataset == "restaurant":
    nb = "1500"
    numclasses = "5"


cmd.append("sed -i 's/^# *define NUMCLASSES.*/\#define NUMCLASSES " + numclasses + "/' server/src/inline.cpp")
statements.append("Changing NUMCLASSES on file")

cmd.append("sed -i 's/^# *define NB.*/\#define NB " + nb + "/' server/src/inline.cpp")
statements.append("Changing NB on file")

cmd.append("sed -i 's/^# *define ERGMODE.*/\#define ERGMODE " + ergmode + "/' server/src/inline.cpp")
statements.append("Changing ERGMODE on file")

cmd.append("sed -i 's/^# *define SAMPLES.*/\#define SAMPLES " + numSamples + "/' server/src/inline.cpp")
statements.append("Changing number of Samples on file")

cmd.append("sed -i 's/^# *define NUMBITS.*/\#define NUMBITS " + finalNumBits + "/' server/src/inline.cpp")
statements.append("Changing number of bits per sample")

cmd.append("sed -i 's/^# *define MAXFEAT.*/\#define MAXFEAT " + mpc + "/' server/src/inline.cpp")
statements.append("Changing number of features per cluster")

for i in range(int(dicSplits)):
  for j in range(int(tabSplits)):
    copyID = i * int(tabSplits) + j
    coreMask = 1 << (copyID % coresAvailable)
    cmd.append("cp server/src/inline.cpp server/src/inline" + str(i) + "." + str(j) + ".cpp")
    statements.append("Copy files")
    cmd.append("sed -i 's/^# *define PORT.*/\#define PORT " + str(port + copyID) + "/' server/src/inline" + str(i) + "." + str(j) + ".cpp")
    statements.append("Changing the ports")
    cmd.append("sed -i 's/^# *define DICSPLIT.*/\#define DICSPLIT " + str(i) + "/' server/src/inline" + str(i) + "." + str(j) + ".cpp")
    statements.append("Assigning dictionary partition")
    cmd.append("sed -i 's/^# *define TABLESPLIT.*/\#define TABLESPLIT " + str(j) + "/' server/src/inline" + str(i) + "." + str(j) + ".cpp")
    statements.append("Assigning table partition")
    cmd.append("sed -i 's/^# *define CLUSTEROFFSET.*/\#define CLUSTEROFFSET " + str(i * numClustersPerFile) + "/' server/src/inline" + str(i) + "." + str(j) + ".cpp")
    statements.append("Fixing dic offset")
    cmd.append("sed -i 's/^# *define TABLEOFFSET.*/\#define TABLEOFFSET " + str(j * numPathsPerFile) + "/' server/src/inline" + str(i) + "." + str(j) + ".cpp")
    statements.append("Fixing table offset")
    if j == int(tabSplits) -1:
        cmd.append("sed -i 's/^# *define TABLEUPPERLIMIT.*/\#define TABLEUPPERLIMIT " + str((j + 2) * numPathsPerFile) + "/' server/src/inline" + str(i) + "." + str(j) + ".cpp")
        statements.append("Fixing table upper bound")
    else:
        cmd.append("sed -i 's/^# *define TABLEUPPERLIMIT.*/\#define TABLEUPPERLIMIT " + str((j + 1) * numPathsPerFile) + "/' server/src/inline" + str(i) + "." + str(j) + ".cpp")
        statements.append("Fixing table upper bound")
    cmd.append("cd server/src/; g++  -o server" + str(i) + "." + str(j) + ".out -funsafe-loop-optimizations -funroll-all-loops -O3 inline" + str(i) + "." + str(j) + ".cpp; cd ../../") 
    statements.append("Compile C++ file")

    if metrics:
      if ergmode == '0':
          #c = ["./server/src/server" + i + ".out", treeName, ">>", "./ResearchData/raw/" + treeName + ".time.txt", "&", "echo"]
          cmd2.append("taskset " + str(coreMask) + " ./server/src/server" + str(i) + "." + str(j) + ".out " + treeName + " >> ./ResearchData/raw/" + treeName + ".dicSplit" + str(i) + ".tabSplit" + str(j) + ".time.txt & echo $! > ./temps/pid" + ergmode)
          cmd2.append("perf stat --field-separator=, -o ./ResearchData/raw/" + treeName + "." + ergmode + ".core" + str(copyID) + ".serverperf -e cpu-cycles,instructions,branches,branch-misses,cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses -p ")
      else:
          cmd2.append("taskset " + str(coreMask) + " ./server/src/server" + str(i) + "." + str(j) + ".out " + treeName + " > server/testaccuracy/temp" + str(i) + "." + str(j) + " & echo $! > ./temps/pid" + ergmode)
          cmd2.append("perf stat --field-separator=, -o ./ResearchData/raw/" + treeName + "." + ergmode + ".core" + str(copyID) + ".serverperf -e cpu-cycles,instructions,branches,branch-misses,cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses -p ")
      statements.append("Run server")

    else:
      cmd2.append("taskset " + str(coreMask) + " ./server/src/server" + str(i) + "." + str(j) + ".out " +  treeName + " > server/testaccuracy/temp" + str(i) + "." + str(j))
      statements.append("Run server")

i = 0
for command in cmd:
    print(statements[i])
    os.system(command) 
    i = i + 1

for j in range(int(dicSplits) * int(tabSplits)):
  if metrics:
    pidfile = "./temps/pid" + ergmode.strip()
    p1 = subprocess.Popen(cmd2[2*j], shell=True)
    print(cmd2[2*j])
    ready = False
    pid = ""
    while not ready:
         try:
             pidcond = open(pidfile,"r", os.O_NONBLOCK).readlines()[0]
         except:
             pidcond = "F"
         if "F" in pidcond:
             time.sleep(1)
         else:
             pid = pidcond
             ready = True

   #while not psutil.pid_exists(int(pid)):
       #time.sleep(1)
    cmd2[2*j + 1] = cmd2[2*j + 1] + pid
    p2 = subprocess.Popen(cmd2[2*j + 1], shell=True)
    print(cmd2[2*j + 1])
    #Disable temporarily perf until we can get all pid correctly
    #p2 = subprocess.Popen(cmd2[2*j + 1], shell=True)
  else:
    p1 = subprocess.Popen(cmd2[i], shell=True)
    print(statements[i])
    i = i + 1
print("Replicas are: " + replicas)
print("Cores are: " + coresAvailable)

