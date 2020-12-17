from subprocess import call
import os

pathPartitionSizes = 120 #800 Was the original experiment
clustersPerPartition = [10]

partFolder = "./clusterwithDimLimit/"
partList = []
currPart = 0
f = open("manualclusters.withDimLimit.txt", "r")
lines = f.readlines()
j = 0
print("Starting to break file into partitions")    
print(len(lines))
while j < (len(lines)):
    index, rest = lines[j].split(None, 1)
    with open(partFolder + index + ".txt", "a") as out:
	out.write(rest)
	j = j + 1
	continue
	for i in range(pathPartitionSizes):
	    try:
		out.write(lines[j])
                j = j + 1
	    except:
		break
print("Partitions done")
exit()

clusterResultFolder = "./clusterRes" + str(pathPartitionSizes) + "/"
for size in clustersPerPartition:
    print("Running k means with %d clusters per partition" % (size))
    cResPath = clusterResultFolder + str(size) + "clustersperpart/"
    for partition in os.listdir("./partitions" + str(pathPartitionSizes) + "/"):
	print(str(size) + partition)
        cmd = "cat " + partFolder + partition + "| python er.copy.kmeans.py " + str(size)
        cmd = cmd + " > " + cResPath + partition
	os.system(cmd)
