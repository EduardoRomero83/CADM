from bitarray import bitarray
import math
import sys

if (len(sys.argv) != 4):
    print("This command takes 2 parameters: python split.py treeName mpc numCores \n")
    exit(1)
treeName=sys.argv[1]
mpc = int(sys.argv[2])
nCores = int(sys.argv[3])

def getCurrentFile(currCore):
  s = "./metadata/" + treeName + ".addresses" + str(currCore) + ".bin"
  return s


"""
Num paths will give us number of total addresses in binary file. 
+ 3 because it avoids hash conflicts (and it is done like this elsewhere)
"""
pathSizeFile = "./metadata/" + treeName + ".numpaths.txt"
f = open(pathSizeFile)
nums = f.readlines()
f.close()

finalNumBits = int(math.floor(math.log(int(nums[0]),2)) + 3)

ogfile = open("./metadata/" + treeName + ".addresses.bin", "rb")
paths = ogfile.read()
ogfile.close()

numPaths = len(paths) // finalNumBits
pathsPerCore = numPaths // nCores

currentCore = 0

ogfile = open("./metadata/" + treeName + ".addresses.bin", "rb")
for i in range(nCores-1):
    piece = ogfile.read(pathsPerCore * finalNumBits)  
    if not piece:
        break
    newFile = open(getCurrentFile(i), "wb")
    newFile.write(piece)
    newFile.close()
piece = ogfile.read()
newFile = open(getCurrentFile(nCores - 1), "wb")
newFile.write(piece)
newFile.close()
ogfile.close()

outfile = open("./metadata/" + treeName + ".numPathsPerFile.txt", "w")
outfile.write(str(numPaths))
outfile.close()

