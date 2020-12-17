import sys

if (len(sys.argv) != 2):
    print("This command takes 1 parameter: python step3.markconflicts.py treeName\n")
    exit()
treeName=sys.argv[1]


infile = "./binadd/tempFiles/" + treeName + ".firsthash.sorted.txt"
f = open(infile , "r")
lines = f.readlines()
f.close()

addresses = {}
for line in lines:
    addr, rest =  line.split(" ", 1)
    if addr not in addresses:
        addresses[addr] = 1
    else:
        addresses[addr] = addresses[addr] + 1

for line in lines: 
    addr, rest =  line.split(" ", 1)
    if addresses[addr] > 1:
        print("1 " + line.strip())
    else:
        print("0 " + line.strip())

