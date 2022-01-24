import os
import sys

if (len(sys.argv) != 3):
    print("This command takes 2 parameters: python step1.dimlimit.py treeName max_dims_limit \n")
    exit(1)
treeName=sys.argv[1]
MAX_FSET = int(sys.argv[2])

def processDivision(cluster):
    lines = cluster.splitlines()
    set1 = set()
    toReturn = [cluster]
    for line in lines:
        feats = line.split(",")
        set1.update(feats)
    if len(set1) <= MAX_FSET:
        return toReturn
    else:
        return divideCluster(cluster)
     

def divideCluster(cluster):
    lines = cluster.splitlines()
    newClusters = []
    half = len(lines)//2
    h1 = "\n".join(lines[half:])
    h2 = "\n".join(lines[:half])
    newClusters.extend(processDivision(h1))
    newClusters.extend(processDivision(h2))
    return newClusters
   


f = open("paths/numericPaths/"+treeName+".numericPaths.txt", "r")
lines = f.readlines()
f.close()
lines.sort();

realindex = -1
readindex = -1
featSet = set()
with open("rootpath.clustering/tempFiles/"+treeName+".dimlimitClusters.txt", "w") as out:
    for line in lines:
        line = str(0) + " " + line;
        index, rest = line.split(None, 1)
        index = int(index)
        features = rest.split()[0].split(",")
        if index > readindex:
            readindex = readindex + 1
            realindex = realindex + 1
            featSet = set(features)
            newstr = str(realindex) + " " + rest
            out.write(newstr)
            continue
        featSet.update(features)
        if len(featSet) <= MAX_FSET:
            newstr = str(realindex) + " " + rest
            out.write(newstr)
        else:
            realindex = realindex + 1
            featSet = set(features)
            newstr = str(realindex) + " " + rest
            out.write(newstr)
