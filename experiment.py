import os
import subprocess
import time
from trainOgForest import manipData
from trainOgForest import manipDataR

"""
Hyperparameters for model. If multiple, then all combinations
of parameters are executed.
"""
numTrees = [str(x) for x in [10]]
depth = [str(x) for x in [8]]
mpc = [str(x) for x in [15]]
maxUnk = [str(x) for x in [8]]
dicSplits = "1"
tableSplits = "1"
"""
Dataset to test.
Values can be:  mnist or traffic or restaurant
"""
dataset = "restaurant"
timeout = "2400"
ERGmode = "0"
perfMetrics = "y"
clientAccTest = "n"

if dataset == "mnist":
    numSamples = "10000"
    numClasses = "10"
elif dataset == "traffic":
    numSamples = "700000"
    numClasses = "7"
    if os.path.exists('./trainOgForest/SplitData.pkl'):
        print('SplitData.pkl exists; proceeding with experiment')
    else:
        print('SplitData.pkl does not exist; creating SplitData.pkl')
        manipData.doEverything()
        print('created SplitData.pkl; proceeding with experiment')
elif dataset == "restaurant":
    numSamples = "5000"
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


def runOneExperiment(n, d, m, u):
    if int(m) < int(d):
        return
    treeName = "RF." + n + "." + d + "." + m + "." + u
    print(treeName)
    cmdCompile = ["timeout", timeout, "python3", "runCompilation.py", n, d, m, u,
                  numSamples, numClasses, ERGmode, perfMetrics, dicSplits, tableSplits, dataset]
    p1 = subprocess.Popen(cmdCompile)
    cmdClient = ["timeout", timeout, "python3", "runPythonClient.py", numSamples, clientAccTest,
                 treeName, ERGmode, perfMetrics, dicSplits, tableSplits, dataset]
    time.sleep(60)
    p2status = subprocess.call(cmdClient)
    cmd = ["python3", "./ResearchData/process.py", treeName]
    p1status = p1.wait()
    if p1status == 0 and p2status == 0:
        subprocess.call(cmd)
        print(treeName + " succeeded")
    else:
        print(treeName + " failed")

print('Running experiment')
for n in numTrees:
    for d in depth:
        for m in mpc:
            for u in maxUnk:
                runOneExperiment(n, d, m, u)


cmd = ["python3", "./ResearchData/ultimate.py"]
subprocess.Popen(cmd)
print('done')
