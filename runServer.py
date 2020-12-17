import math
import os
import sys

#Check args
if (len(sys.argv)) != 6:
    print("This command takes 5 parameters: python runServer.py treeName mpc NumberOfSamples ERGMODE performanceMetrics(y/n)\n")
    exit()

treeName = sys.argv[1]
mpc = sys.argv[2]
numSamples = sys.argv[3]
ergmode = sys.argv[4]
metrics = 'y' in sys.argv[5]

pathSizeFile = "./metadata/" + treeName + ".numpaths.txt"
f = open(pathSizeFile)
nums = f.readlines()
f.close()

finalNumBits = str(int(math.floor(math.log(int(nums[0]),2)) + 3))

cmd = []
cmd2 = []
statements = []

cmd.append("sed -i 's/^# *define ERGMODE.*/\#define ERGMODE " + ergmode + "/' server/src/inline.cpp")
statements.append("Changing ERGMODE on file")

cmd.append("sed -i 's/^# *define SAMPLES.*/\#define SAMPLES " + numSamples + "/' server/src/inline.cpp")
statements.append("Changing number of Samples on file")

cmd.append("sed -i 's/^# *define NUMBITS.*/\#define NUMBITS " + finalNumBits + "/' server/src/inline.cpp")
statements.append("Changing number of bits per sample")

cmd.append("sed -i 's/^# *define MAXFEAT.*/\#define MAXFEAT " + mpc + "/' server/src/inline.cpp")
statements.append("Changing number of features per cluster")

cmd.append("cd server/src/; g++  -funsafe-loop-optimizations -funroll-all-loops -O3 inline.cpp; cd ../../") 
statements.append("Compile C++ file")

if metrics:
    if ergmode == '0':
        cmd2.append("./server/src/a.out " + treeName + " >> ./ResearchData/raw/" + treeName + ".time.txt & echo $! > ./temps/pid" + ergmode)
    else:
        cmd2.append("./server/src/a.out " + treeName + " > server/testaccuracy/temp & echo $! > ./temps/pid" + ergmode)
    cmd2.append("perf stat --field-separator=, -o ./ResearchData/raw/" + treeName + "." + ergmode + ".serverperf -e cpu-cycles,instructions,branches,branch-misses,cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses -p ")
    statements.append("Run server")

else:
    cmd.append("./server/src/a.out " + treeName + " > server/testaccuracy/temp")
    statements.append("Run server")

i = 0
for command in cmd:
    print(statements[i])
    os.system(command) 
    i = i + 1

if metrics:
   pidfile = "./temps/pid" + ergmode.strip()
   os.system(cmd2[0])
   print(cmd2[0])
   ready = False
   pid = ""
   while not ready:
       pidcond = open(pidfile,"r", os.O_NONBLOCK).readlines()[0]
       if "F" in pidcond:
           time.sleep(1)
       else:
           pid = pidcond
           ready = True

   #while not psutil.pid_exists(int(pid)):
       #time.sleep(1)
   cmd2[1] = cmd2[1] + pid
   os.system(cmd2[1])
 
