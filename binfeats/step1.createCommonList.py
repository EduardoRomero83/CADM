import os
import sys

if (len(sys.argv) != 2):
    print("This command takes 1 parameter: python step1.createCommonList.py treeName \n")
    exit(1)
treeName=sys.argv[1]


def printCommon(dic, cID, cDim):
    cDimlist = cDim.split(",")
    answer = cID + " " + cDim + " "
    importantFeatures = ""
    commonFeatures = ""
    for feat in cDimlist:
        if feat not in dic or dic[feat] == -1:
            commonFeatures = commonFeatures + "0"
            importantFeatures = importantFeatures + "0"
        else:
            commonFeatures = commonFeatures + str(dic[feat])
            importantFeatures = importantFeatures + "1"
    answer = answer + importantFeatures + " " + commonFeatures
    print(answer)


def verifyCommon(dimensions, directions, commonDic):
    for key in commonDic:
        ind = dimensions.index(key)
        dec = directions[ind]
        if not dec == commonDic[key]:
            commonDic[key] = -1

def dicCommon(dimensions, directions, commonLines, cID):
    theLine = commonLines[cID]
    cID, commonfeatures, commonSize = theLine.split()
    commonSize = int(commonSize)
    dic = {}
    i = 0
    for feature in commonfeatures.split(","):
        if i >= commonSize:
            break
        i = i + 1
        try:
            ind = dimensions.index(feature)
            dic[feature] = directions[ind]
        except Exception as e:
            print("ERROR -------------------------------------")
            print(e)
            print(dic)
            print(cID)
            print(theLine)
            print(dimensions)
            exit()
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


BIGPRIME = 373
ogfile = open("./rootpath.clustering/clusteredOutputs/" + treeName + ".txt", "r")
commonLinesFile = open("./rootpath.clustering/tempFiles/" + treeName + ".clusterfeatures.sorted.txt", "r")
commonLines = commonLinesFile.readlines()
commonLinesFile.close()
currID = "-1"
currDic = {}
prevDims = ""
for line in ogfile:
    cID, path, directions, output, cDim = line.split()
    path = path.split(",")
    if len(path) != len(set(path)):
        print("PROBLEM")
        exit()
        path, directions = removeDuplicates(path, directions)
    decs = list(directions)
    dims = len(cDim)
    if cID != currID:
        if not currID == "-1":
            printCommon(currDic, currID, prevDims) 
        currID = cID
        prevDims = cDim
        currDic = dicCommon(path, decs, commonLines, int(cID))
    else:
        verifyCommon(path, decs, currDic)
ogfile.close()
