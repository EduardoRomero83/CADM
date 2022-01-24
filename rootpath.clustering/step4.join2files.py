import sys
if (len(sys.argv) != 2):
    print("This command takes 2 parameters: python step1.dimlimit.py treeName \n")
    exit(1)
treeName=sys.argv[1]



features = open("rootpath.clustering/tempFiles/"+treeName+".clusterfeatures.sorted.txt", "r")
paths = open("rootpath.clustering/tempFiles/"+treeName+".unklimitClusters.txt", "r")
output = open("rootpath.clustering/clusteredOutputs/"+treeName+".txt", "w")

feats = features.readlines()
ps = paths.readlines()
paths.close()
features.close()

i = 0
for line in ps:
    cid, path = line.split(None, 1)
    cid = int(cid)
    fs = feats[cid].split()[1]
    newstr = str(cid) + " " + path.strip() + " " + fs.strip()
    output.write( newstr + "\n")
output.close()
