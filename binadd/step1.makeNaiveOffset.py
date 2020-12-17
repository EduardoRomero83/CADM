import sys
import random
#  Accepts a file organized as ClusterId Path Directions Output ClusterDimensions. er.numericPaths.clusterid.featurelist.txt
#  Accepts command line of #maxdimensionspercluster (mpc) # 20 
#  This script does the following: 
#      1. For each line
#             Check if ClusterDimensions != PrevDimensions // Or just check if clusterID is the same, right? That's faster and why would it hurt?
#                   if so, create a hashmap HM mapping dimension -> position
#             Create integer array IA of size mpc (init to -1) // Should be len(ClusterDimensions) or next steps don't make sense
#             For each Path element E (corresponding to number i) lookup  HM(E) and store Directions[i] in IA[HM(E)] 

#             Check if ClusterDimensions is < mpc
#                  if so, create a binary number (B) clusterID*BIGPRIME / 2^(mpc - clusterdimensions) // Should be mod
#                  append IA + B (starting at index ClusterDimensions)
#
#             expansions = Size(ClusterDimensions) - Size(Path)
#             For each j = 0 to 2^(expansions)
#                 replacementBit = 0
#                 For k = 0 to mpc
#                   if IA[k] = -1; set IA[k] to j<replacementBit> 
#                   replacementBit++
#                  Print IA[K] output


#$BIGPRIME = 373

#Very Naive right now. TO-DO use better hash function
def hashmap(dimensions):
    dic = {}
    i = 0
    for feature in dimensions:
        dic[feature] = i
        i = i + 1
    return dic

def removeDuplicates(path, directions):
    newPath = []
    newDir = ""
    count = 0
    setF = set()
    for feat in path:
        if feat not in setF:
            setF.add(feat)
            newPath.append(feat)
            newDir = newDir + directions[count]
        count = count + 1
    return newPath, newDir

if (len(sys.argv) != 3):
    print("This command takes 2 parameters: python step1.makeNaiveOffset.py treeName mpc\n")
    exit()
treeName=sys.argv[1]
mpc = int(sys.argv[2])


BIGPRIME = 373
ogfile = open("./rootpath.clustering/clusteredOutputs/" + treeName + ".txt", "r")
currID = "-1"
currDic = {}
for line in ogfile:
    cID, path, directions, output, cDim = line.split()
    cDim = cDim.split(",")
    path = path.split(",")
    if len(path) != len(set(path)):
        path, directions = removeDuplicates(path, directions)
    dims = len(cDim)
    if cID != currID:
        currID = cID
        currDic = hashmap(cDim) 
    IA = ["-1"] * dims
    dirArr = [x for x in list(directions)]
    i = 0
    for E in path:
        IA[currDic[E]] = dirArr[i]
        i = i + 1
    if dims < mpc:
        b = ((int(cID) + 1) * BIGPRIME) % 2 ** (mpc - dims)
        B = bin(b)[2:].zfill(mpc - dims)
        for c in list(B):
            IA.append(c)
    if len(IA) < mpc:
        print("ERROR")
        exit()

    expansions = dims - len(path)
    for j in range(2**expansions):
        jb = list(bin(j)[2:].zfill(expansions))
        replacementBit = 0
        ia = IA[:]
        for k in range(mpc):
            if ia[k] == "-1":
        # I added this because of repeated features on the same path. Not neccessary now.
        # If anything prints from except below, then something went unexpectedly wrong, but they are not printed for now
                try:
                    ia[k] = jb[replacementBit]
                except:
                    print(line)
                    exit()
                replacementBit = replacementBit + 1
        out = "".join(ia) + " " + output + " " + cID
        print(out)
ogfile.close()
