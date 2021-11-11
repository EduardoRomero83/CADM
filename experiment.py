import os
import subprocess
import time
from trainOgForest import manipData

numTrees = ["10"]
depth = ["4"]
#mpc = ["17", "18", "19", "20"]
#maxUnk = ["8"]
#maxUnk = ["2", "3", "4", "5", "6", "7", "8", "9", "10"]
#numTrees = ["100"]
#depth = ["14", "16"]
mpc = ["15"]
maxUnk = ["8"]
dicSplits = "1"
tableSplits = "1"
dataset = "mnist" # mnist or traffic

if dataset == "mnist":
    numSamples = "10000"
else:
    numSamples = "700000"
    if os.path.exists('./trainOgForest/SplitData.pkl'):
        print('SplitData.pkl exists; proceeding with experiment')
    else:
        print('SplitData.pkl does not exist; creating SplitData.pkl')
        manipData.doEverything()
        print('created SplitData.pkl; proceeding with experiment')

print('Running experiment')
cmd = []
for n in numTrees:
    for d in depth:
        for m in mpc:
            for u in maxUnk:
                if int(m) < int(d):
                    continue
                with open("./temps/pid0", "w") as f:
                    f.write("False")
                    f.close()
                with open("./temps/pid1", "w") as f:
                    f.write("False")
                    f.close()
                #time.sleep(10)
                treeName = "RF." + n + "." + d + "." + m + "." + u
                print(treeName)
                cmd = ["timeout", "1200", "python3", "runCompilation.py", n, d, m, u, numSamples, "7", "0", "y", dicSplits, tableSplits, dataset]
                p1 = subprocess.Popen(cmd)
                time.sleep(10)
                cmd = ["timeout", "1200", "python3", "runPythonClient.py", numSamples, "n", treeName, "0", "y", dicSplits, tableSplits, dataset]
                time.sleep(60)
                p2 = subprocess.call(cmd)
                #cmd = ["timeout", "7200", "python3", "runPythonClient.py", "700", "y", treeName, "1", "y", nCores]
                #p3 = subprocess.call(cmd)
                cmd = ["python3", "./ResearchData/process.py", treeName]
                p1.wait()
                p4 = subprocess.call(cmd)


cmd = ["python3", "./ResearchData/ultimate.py"]
subprocess.call(cmd)
print('done')

