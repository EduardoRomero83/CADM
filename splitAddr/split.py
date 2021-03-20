from bitarray import bitarray
import sys

if (len(sys.argv) != 4):
    print("This command takes 2 parameters: python split.py treeName mpc numCores \n")
    exit()
treeName=sys.argv[1]
mpc = int(sys.argv[2])
nCores = int(sys.argv[3])

def getCurrentFile(currCore):
  s = "./metadata/" + treeName + ".addresses" + str(currCore) + ".bin"
  return s


"""
OLD: Copy of server structure + reasoning why divide clusters the following way:
struct cluster
{
  //char ftcount;
  unsigned int signature;
  feature ft[MAXFEAT];
  unsigned int important;
  unsigned int common;
};
"""

bytesPerCluster = 4 * mpc + 12
ogfile = open("./metadata/" + treeName + ".features.bin", "rb")
clusters = ogfile.read()
ogfile.close()

numClusters = len(clusters) // bytesPerCluster
clustersPerCore = numClusters // nCores

currentCore = 0

ogfile = open("./metadata/" + treeName + ".features.bin", "rb")
for i in range(nCores-1):
    piece = ogfile.read(clustersPerCore * bytesPerCluster)  
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

outfile = open("./metadata/" + treeName + ".numClustersPerFile.txt", "w")
outfile.write(str(numClusters))
outfile.close()

