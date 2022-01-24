import os
import sys

if (len(sys.argv) != 2):
    print("This command takes 1 parameters: python test.py treeName\n")
    exit(1)
treeName=sys.argv[1]


path = "./paths/TFpaths/"
path2 = "./paths/"
directory = os.listdir(path)

with open(path2 + treeName + ".truePaths.txt", "w") as out:
    for tree in directory:
        if str(treeName + ".tree") in tree:
            with open(path + tree, "r") as f:
                for line in f:
                    l = line.rsplit(None, 1)[0]
                    out.write(l)
                    out.write("\n")

