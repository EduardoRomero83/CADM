import os
import sys


if (len(sys.argv)) != 8:
    print("This command takes 7 parameters: python runCompilation.py numberOfTrees maxDepth mpc maxUnknown numberofTestingSamples ERGMODE performanceMetrics?(y/n) \n")
    exit()

numTrees = sys.argv[1]
maxDepth = sys.argv[2]
mpc = sys.argv[3]
maxUnk = sys.argv[4]
numSamples = sys.argv[5]
ergmode = sys.argv[6]
metrics = 'y' in sys.argv[7]

treeName = "RF." + numTrees + "." + maxDepth + "." + mpc + "." + maxUnk
cmd = []
statements = []

# No need to retrain
cmd.append("python3 trainOgForest/train.py " + treeName + " " +  numTrees + " " + " " + maxDepth)
statements.append("Train model")
if metrics:
    cmd.append("perf stat --field-separator=, -o ./ResearchData/raw/" + treeName + ".pythonperf -e cpu-cycles,instructions,branches,branch-misses,cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses python3 trainOgForest/test.py " + treeName + " 1")
    statements.append("DOT files extraction")
else:
    cmd.append("python3 trainOgForest/test.py " + treeName + " 1")
    statements.append("DOT files extraction")
cmd.append("python3 paths/dot2paths.py " + treeName)
statements.append("DOT to directories")
cmd.append("python3 paths/pathdir2txt.py " + treeName)
statements.append("Path directory to text file")
cmd.append("python3 paths/pathtxt2format.py " + treeName)
statements.append("Get numeric paths")
cmd.append("python3 rootpath.clustering/step1.dimlimit.py " + treeName + " " + mpc)
statements.append("Separate clusters by dim limit")
cmd.append("python3 rootpath.clustering/step2.unklimit.py " + treeName + " " + maxUnk)
statements.append("Clusters unkown limit")
cmd.append("python3 rootpath.clustering/step3.clusterfeatures.py " + treeName)
statements.append("Get cluster features file")
cmd.append("sort -n -k 1 rootpath.clustering/tempFiles/" + treeName + ".clusterfeatures.txt > rootpath.clustering/tempFiles/" + treeName + ".clusterfeatures.sorted.txt")
statements.append("Sort")
cmd.append("python3 rootpath.clustering/step4.join2files.py " + treeName)
statements.append("Join cluster features and numeric paths")
cmd.append("python3 binfeats/step1.createCommonList.py " + treeName + " > binfeats/commonandimp/" + treeName + ".commonandimp.txt")
statements.append("Common features")
cmd.append("python3 binfeats/step2.featToBin.py " + treeName + " " + mpc)
statements.append("Binary features")
cmd.append("python3 binadd/step1.makeNaiveOffset.py " + treeName + " " + mpc + " > binadd/tempFiles/" + treeName + ".naiveoffset.txt")
statements.append("Naive offset")
cmd.append("cat binadd/tempFiles/" + treeName + ".naiveoffset.txt | wc -l > metadata/" + treeName + ".numpaths.txt")
statements.append("Count paths")
cmd.append("python3 binadd/step2.firsthash.py " + treeName + " > binadd/tempFiles/" + treeName + ".firsthash.txt")
statements.append("First hash")
cmd.append("sort -k 1 binadd/tempFiles/" + treeName + ".firsthash.txt > binadd/tempFiles/" + treeName + ".firsthash.sorted.txt")
statements.append("Sort")
cmd.append("python3 binadd/step3.markconflicts.py " + treeName + " > binadd/tempFiles/" + treeName + ".firsthash.conflicts.txt")
statements.append("Mark Conflicts")
cmd.append("python3 binadd/step4.combineconflicts.py " + treeName + " > ./binadd/tempFiles/" + treeName + ".firsthash.combinedconflicts.txt")
statements.append("Combine conflicts")
cmd.append("python3 binadd/step5.secondhash.py " + treeName + " > binadd/tempFiles/" + treeName + ".secondhash.txt")
statements.append("Second hash")
cmd.append("sort -k 2 binadd/tempFiles/" + treeName + ".secondhash.txt > binadd/tempFiles/" + treeName + ".secondhash.sorted.txt")
statements.append("Sort")
cmd.append("python3 binadd/step6.removehashduplicates.py " + treeName + " > binadd/tempFiles/" + treeName + ".secondhash.nodup.txt")
statements.append("Remove duplicate conflicts")
cmd.append("python3 binadd/step7.neededbits.py " + treeName + " > metadata/" + treeName + ".bitsperaddline.txt")
statements.append("Count bits")
cmd.append("python3 binadd/step8.tobinary.py " + treeName)
statements.append("Binary addresses")
if metrics:
    cmd.append("python3 runServer.py " + treeName + " " + mpc + " " + numSamples + " 0 y;")
    statements.append("Compile and run the server")
    cmd.append("sleep 80")
    statements.append("Sleeping between runs")
    cmd.append("python3 runServer.py " + treeName + " " + mpc + " " + numSamples + " 1 y;")
    statements.append("Compile and run the server")
else:
    cmd.append("python3 runServer.py " + treeName + " " + mpc + " " + numSamples + " " + ergmode + " n")
    statements.append("Compile and run the server")
#
i = 0
for command in cmd:
    print(statements[i])
    os.system(command) 
    i = i + 1
    #if i > 2:
	#exit()

