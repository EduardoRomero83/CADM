import os
import subprocess
import time
from trainOgForest import manipData
from trainOgForest import manipDataR

"""
Hyperparameters for model. If multiple, then all combinations
of parameters are executed.
"""
"""
numTrees = [str(x) for x in [10]]
depth = [str(x) for x in [5]]
mpc = [str(x) for x in [15]]
maxUnk = [str(x) for x in [8]]
dicSplits = [str(x) for x in [1, 2, 4, 8, 16, 23]]
tableSplits = [str(x) for x in [1]]
replicas = [str(x) for x in [1, 2, 4, 8, 16, 23]]
"""
"""
Quick tests below
"""
#"""
numTrees = [str(x) for x in [10]]
depth = [str(x) for x in [5]]
mpc = [str(x) for x in [15]]
maxUnk = [str(x) for x in [8]]
dicSplits = [str(x) for x in [1]]
tableSplits = [str(x) for x in [1]]
replicas = [str(x) for x in [1]]
#"""
coresAvailable = "23" #subtract one from the total system cores to save it to the client
numSamples = ""
"""
Dataset to test.
Values can be:  mnist or traffic or restaurant or cifar100
"""
dataset = "cifar100"
timeout = "2400"
ERGmode = "0"
perfMetrics = "y"
clientAccTest = "n"
skipCombinationOfCores = True

if dataset == "mnist":
    if numSamples == "":
        numSamples = "10000"
    numClasses = "10"
elif dataset == "cifar100":
    if numSamples == "":
        numSamples = "10000"
    numClasses = "100"
elif dataset == "traffic":
    if numSamples == "":
        numSamples = "700000"
    numClasses = "7"
    if os.path.exists('./trainOgForest/SplitData.pkl'):
        print('SplitData.pkl exists; proceeding with experiment')
    else:
        print('SplitData.pkl does not exist; creating SplitData.pkl')
        manipData.doEverything()
        print('created SplitData.pkl; proceeding with experiment')
elif dataset == "restaurant":
    if numSamples == "":
        numSamples = "300"
    numClasses = "5"
    if os.path.exists('./trainOgForest/SplitDataR.pkl'):
        print('SplitDataR.pkl exists; proceeding with experiment')
    else:
        print('SplitDataR.pkl does not exist; creating SplitDataR.pkl')
        manipDataR.doEverything()
        print('created SplitDataR.pkl; proceeding with experiment')


def resetReadyFile():
    with open("./temps/pid0", "w") as f:
        f.write("False")
        f.close()
    with open("./temps/pid1", "w") as f:
        f.write("False")
        f.close()


def runOneExperiment(n, d, m, u, replicas, dicSplits, tableSplits):
    if int(m) < int(d):
        return
    coresUsed = int(replicas) * int(dicSplits) * int(tableSplits)
    if coresUsed > (3 * int(coresAvailable)):
        return
    if skipCombinationOfCores and int(replicas) > 1 and int(dicSplits) > 1:
        return
    treeName = "RF." + n + "." + d + "." + m + "." + u + "." + replicas + "." + dicSplits + "." + tableSplits + "." + numSamples
    print(treeName)
    cmdCompile = ["timeout", timeout, "python3", "runCompilation.py", n, d, m, u,
                  numSamples, numClasses, ERGmode, perfMetrics, dicSplits, tableSplits, replicas, dataset, coresAvailable]
    p1 = subprocess.Popen(cmdCompile)
    cmdClient = ["timeout", timeout, "taskset", "1", "python3", "runPythonClient.py", numSamples, clientAccTest,
                 treeName, ERGmode, perfMetrics, dicSplits, tableSplits, replicas, dataset]
    time.sleep(60)
    p2status = subprocess.call(cmdClient)
    cmd = ["python3", "./ResearchData/process.py", treeName, dataset]
    p1status = p1.wait()
    if p1status == 0 and p2status == 0:
        subprocess.call(cmd)
        print(treeName + " succeeded")
    else:
        print(treeName + " failed")
    cmd = ["pkill", "boltserver*"]
    subprocess.call(cmd)

print('Running experiment')
for n in numTrees:
    for d in depth:
        for m in mpc:
            for u in maxUnk:
                for r in replicas:
                    for ds in dicSplits:
                        for ts in tableSplits:
                            runOneExperiment(n, d, m, u, r, ds, ts)


cmd = ["python3", "./ResearchData/ultimate.py", dataset]
subprocess.Popen(cmd)
print('done')
