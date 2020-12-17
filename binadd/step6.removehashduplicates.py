import sys

if (len(sys.argv) != 2):
    print("This command takes 1 parameter: python step6.removehashduplicates.py treeName\n")
    exit()
treeName=sys.argv[1]

infile = "./binadd/tempFiles/" + treeName + ".secondhash.sorted.txt"

f = open(infile, "r")
lines = f.readlines()
f.close()

lineset = set()

for theline in lines:
    line = " ".join(theline.split()[:-1])
    if line not in lineset:
        lineset.add(line)
        print(theline.strip())

