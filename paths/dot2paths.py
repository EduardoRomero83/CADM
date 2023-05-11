import os
import re
import sys

if (len(sys.argv) != 3):
    print("This command takes 2 parameters: python test.py treeName numClasses\n")
    exit(1)
treeName=sys.argv[1]
numClasses=int(sys.argv[2])

def findPath(i, currPath, nodes, children, parents):
    if (i == 0):
        return nodes[0] + " ** " + currPath
    newPath = nodes[i] + " ** " + currPath
 #   rightChild = False
    parent = parents[i]
    if children[parent][0] == i:
        rightChild = False
    else:
        rightChild = True
    if (rightChild):
        newPath = "False ==> " + newPath
    else:
        newPath = "True ==> " + newPath
    if (parent >= 0):    
        return findPath(parent, newPath, nodes, children, parents)
    return "Error"

path = "./trainOgForest"
path2 = "./paths"
directory = os.listdir(path + "/dot/")
for tree in directory:
    if str(treeName + ".tree") in tree:
        with open(path + "/dot/" + tree, "r") as f, open(path2 + "/TFpaths/" +treeName+"." + tree + ".path", "w") as out:
            nodes = []
            edges = []
            f.readline()
            f.readline()
            line1 = f.readline().split("X")[1].split("\\")[0]
            nodes.append(line1)
            count = 0
            parents = {}
            children = {}
            pendingLeaf = -1
            for line in f:
                if (count % 2 == 0):
                    try:
                        line1 = line.split("X")[1].split("\\")[0]
                        #out.write(line1)
                        #out.write("\n")
                        nodes.append(line1)
                    except:
                        #out.write("Leaf")
                        #out.write("\n")
                        try:
                            line = line.replace("\\n", ", ")
                            response = line.split("=")[4].split("[")[1].split("]")[0]
                            array = []
                            numbers = response.split(",")
                            for i in range(numClasses):
                                array.append(int(numbers[i]))
                            nodes.append(str(array))
                            pendingLeaf = int(line.split()[0])
                        except:
                            pass
                else:
                    edge = line.split(';')[0].rstrip()
                    parent = int(edge.split()[0])
                    child = int(edge.split()[2])
                    if child not in parents:
                        parents[child] = parent
                    if parent not in children:
                        children[parent] = [child, -1]
                    else:
                        children[parent][1] = child
                    edges.append(edge)
                    if (pendingLeaf >= 0): 
                        pathToLeaf = findPath(pendingLeaf, "", nodes, children, parents)
                        out.write(pathToLeaf)
                        out.write("\n")
                        pendingLeaf = -1
                count = count + 1
    

