import os
import sys

if (len(sys.argv) != 2):
    print("This command takes 2 parameters: python step1.dimlimit.py treeName \n")
    exit()
treeName=sys.argv[1]



groups = {}
unkgroups = {}
ic = open ("rootpath.clustering/tempFiles/"+treeName+".unklimitClusters.txt","r")
oc = open ("rootpath.clustering/tempFiles/"+treeName+".clusterfeatures.txt","w")
iclines = ic.readlines()
ic.close()
for icl in iclines:
    cid = icl.split(" ")[0]
    rest = icl.split(" ")[1]
    if cid in groups:
        groups[cid] = groups[cid] +"\n" + rest.strip()
    else:
        groups[cid] = rest.strip()

#folder = "clusterwithFewUncommon/"
#clusters = os.listdir(folder)

for cluster in groups:
    features = {} 
    common = set()
    i = 0        
    for line in groups[cluster].split("\n"):
        temp = {}
        lineFeats = line.split()[0].split(",")
        for word in lineFeats:
            if word not in features:
                features[word] = 1
                temp[word] = True
            else:
                if word not in temp:
                    features[word] = features[word] + 1
                    temp[word] = True
        i = i + 1
    for word in features:
        if features[word] == i:
            common.add(word)

    clist = sorted(common)
    flist = sorted(features.keys())
    finalList = ""
    if len(common) < len(features):
        for c in clist:
            finalList = finalList + c + ","
        for f in flist[:-1]:
            if f not in common:
                finalList = finalList + f + ","
        if flist[-1] not in common:
            finalList = finalList +  flist[-1]
        else:
            finalList = finalList[:-1]
    else:
        for f in flist[:-1]:
            finalList = finalList + f + ","
        finalList = finalList + flist[-1]
    answer = cluster + " " + finalList + " " + str(len(common))
    oc.write(answer + "\n")
oc.close()
