import math
import sys

if (len(sys.argv) != 2):
    print("This command takes 1 parameter: python step2.firsthash.py treeName\n")
    exit()
treeName=sys.argv[1]

f = open("./binadd/tempFiles/" + treeName + ".naiveoffset.txt", "r")
lines = f.readlines()
f.close()

pathSizeFile = "./metadata/" + treeName + ".numpaths.txt"
f = open(pathSizeFile)
nums = f.readlines()
f.close()

finalNumBits = int(math.floor(math.log(int(nums[0]),2)) + 3)

n1 = 2
n2 = 23

for line in lines:
    addr, result, cID = line.split()
    addr = int(addr, 2)
    adSize = 2**finalNumBits
    newaddr = ((n1 * addr) + (n2 * int(cID))) % adSize
    newstr = bin(newaddr)[2:].zfill(finalNumBits) + " " + result + " " + cID
    print(newstr)
