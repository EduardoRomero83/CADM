import sys

if (len(sys.argv) != 2):
    print("This command takes 1 parameters: python test.py treeName\n")
    exit()
treeName=sys.argv[1]


def shortenfeat(feat):
    feature = feat.split("[")[1].split("]")[0]
    value = feat.split("=")[1].split("*")[0].strip().replace(".", "")
    while(len(value) < 4):
        value = "0" + value
    while(len(feature) < 3):
        feature = "0" + feature
    decision = "T" in feat.split("**")[1]
    combined = feature + value
    return combined, decision
 

ogFile = open("paths/"+treeName + ".truePaths.txt", "r")
lines = ogFile.readlines()
ogFile.close()

outpath = []
with open("paths/numericPaths/" + treeName + ".numericPaths.txt", "w") as outFile:
    for line in lines:
        features = line.split("==>")
        resp = features[-1]
        features = features[:len(features) - 1]
        resp = resp.split("[")[1].split("]")[0]
        resp = "".join(resp.split())
        newPath = ""
        addr = ""
        for feature in features[:-1]:
            shortfeat, dec = shortenfeat(feature)
            newPath = newPath + shortfeat + ","
            if dec:
                addr = addr + "1"
            else:
                addr = addr + "0"
        shortfeat, dec = shortenfeat(features[-1])
        newPath = newPath + shortfeat + " "
        if dec:
            addr = addr + "1 "
        else:
            addr = addr + "0 "
        outFile.write( newPath + addr + resp + "\n")


