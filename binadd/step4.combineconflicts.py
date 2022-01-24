import sys

if (len(sys.argv) != 2):
    print("This command takes 1 parameter: python step4.combineconflicts.py treeName\n")
    exit(1)
treeName=sys.argv[1]


infile = "./binadd/tempFiles/" + treeName + ".firsthash.conflicts.txt"

f = open(infile, "r")
lines = f.readlines()
f.close()

currAddr = ""
currString = ""
prevString = ""
for line in lines:
    conf, addr, res, cID = line.strip().split()
    if addr != currAddr:
        if currString != "":
            print(currString)
            currString = ""
        elif prevString != "":
            print(prevString)
        currAddr = addr
        prevString = line.strip()
    else:
        if currString == "":
            currString = prevString + " $ " + line.strip()
        else:
            currString = currString + " $ " + line.strip()
if currString == "":
    print(prevString)
else:
    print(currString)
