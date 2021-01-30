import os
import subprocess
import time
from trainOgForest import manipData

numTrees = ["10"]
depth = ["8"]
mpc = ["18"]
maxUnk = ["6"]
#numTrees = ["100"]
#depth = ["14", "16"]
#mpc = ["20"]
#maxUnk = ["4"]
nCores = "1"

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
                cmd = ["timeout", "7200", "python3", "runCompilation.py", n, d, m, u, "700000", "7", "0", "y", nCores]
                p1 = subprocess.Popen(cmd)
                time.sleep(10)
                cmd = ["timeout", "7200", "python3", "runPythonClient.py", "700000", "n", treeName, "0", "y", nCores]
                time.sleep(60)
                p2 = subprocess.call(cmd)
                cmd = ["timeout", "7200", "python3", "runPythonClient.py", "700000", "y", treeName, "1", "y", nCores]
                p3 = subprocess.call(cmd)
                cmd = ["python3", "./ResearchData/process.py", treeName]
                p1.wait()
                p4 = subprocess.call(cmd)


cmd = ["python3", "./ResearchData/ultimate.py"]
subprocess.call(cmd)
print('done')
