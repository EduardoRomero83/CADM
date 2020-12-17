import os
import sys

if (len(sys.argv) != 3):
    print("This command takes 2 parameters: python step2.dimlimit.py treeName unknown_limit \n")
    exit()
treeName=sys.argv[1]
unklimit=int(sys.argv[2])



def processDivision(cluster):
    lines = cluster.splitlines()
    dic = {}
    toReturn = [cluster]
    j = 0
    for line in lines:
        feats = line.split()[0].split(",")
        for f in feats:
            if f not in dic:
                dic[f] = 1
            else:
                dic[f] = dic[f] + 1
        j = j + 1
    countnew = 0
    for f in dic:
        if dic[f] < j:
            countnew = countnew + 1
    if countnew <= unklimit:
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
   


cResPath = "clusterwithDimLimit/" 
initClusters = "rootpath.clustering/tempFiles/"+treeName+ ".dimlimitClusters.txt"
unkClusters = "rootpath.clustering/tempFiles/"+treeName+ ".unklimitClusters.txt"
limited = "clusterwithFewUncommon/"

i = 0
groups = {}
unkgroups = {}
t = ""
prev_cid = -1
ic = open (initClusters,"r")
iclines = ic.readlines()
ic.close()
for icl in iclines:
    cid = icl.split(" ")[0]
    rest = icl[len(cid+" "):]

    if ((cid != prev_cid) and (int(prev_cid) > 0)):
        groups[prev_cid] = t.rstrip()
        t = ""
    prev_cid = cid
    t = t+rest

    #if (i % 10000 == 0):
    #    print i
    #i = i +1

groups[prev_cid] = t.rstrip()
#print prev_cid + "\n" + groups[prev_cid]
#exit()
#groups = os.listdir(cResPath)

for group in groups:
    cluster = groups[group];
    temp = ""
    j = 0
    featSet = {}
    for c in cluster.split("\n"):
        j = j + 1
        temp = temp + c + "\n"
        line = c.split()[0].split(",")

        for f in line:
            if f not in featSet:
                featSet[f] = 1
            else:
                featSet[f] = featSet[f] + 1
    countnew = 0
    for key in featSet:
        if featSet[key] < j:
            countnew = countnew + 1
    if countnew <= unklimit:
        if i in unkgroups:
            unkgroups[i] = unkgroups[i]+ "\n" +temp
        else:
            unkgroups[i] = temp
        #with open(unkCluster, "w") as out:
        #   out.write(temp)
        i = i + 1
    else:
        newclusters = divideCluster(temp)
        for newc in newclusters:
            if i in unkgroups:
                unkgroups[i] = unkgroups[i]+ "\n" +newx
            else:
                unkgroups[i] = newc
            #with open(limited + str(i), "w") as out:
            #    out.write(newc)
                if (i % 10000 == 0):
                    print(i)
            i = i + 1

with open(unkClusters, "w") as u:
    for i in unkgroups:
        for c in unkgroups[i].split("\n"):
            if (c not in [""," ","\n","\r\n"]):
                u.write (str(i) + " " +  c + "\n")
