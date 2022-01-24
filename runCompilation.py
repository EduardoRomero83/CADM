import os
import subprocess
import sys


if (len(sys.argv)) != 12:
    print("This command takes 11 parameters: python runCompilation.py " +
          "numberOfTrees maxDepth" +
          "mpc maxUnknown numberofTestingSamples numClasses " +
          "ERGMODE performanceMetrics?(y/n) dicSplits tableSplits dataset\n")
    exit(1)

numTrees = sys.argv[1]
maxDepth = sys.argv[2]
mpc = sys.argv[3]
maxUnk = sys.argv[4]
numSamples = sys.argv[5]
numClasses = sys.argv[6]
ergmode = sys.argv[7]
metrics = 'y' in sys.argv[8]
dicSplits = sys.argv[9]
tableSplits = sys.argv[10]
dataset = sys.argv[11]

treeName = "RF." + numTrees + "." + maxDepth + "." + mpc + "." + maxUnk
cmd = []
statements = []

cmd.append(["python3", "trainOgForest/train.py", treeName, numTrees, maxDepth, dataset])
statements.append("Train model")
if metrics:
    cmd.append(["perf", "stat", "--field-separator=,", "-o", 
                "./ResearchData/raw/" + treeName + ".pythonperf", "-e", "cpu-cycles,instructions,branches," +
                "branch-misses,cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses," +
                "LLC-loads,LLC-load-misses", "python3", "trainOgForest/test.py", treeName, "1", dataset])
    statements.append("DOT files extraction")
else:
    cmd.append(["python3", "trainOgForest/test.py", treeName, "1", dataset])
    statements.append("DOT files extraction")
cmd.append(["python3", "paths/dot2paths.py", treeName, numClasses])
statements.append("DOT to directories")

cmd.append(["python3", "paths/pathdir2txt.py", treeName])
statements.append("Path directory to text file")

cmd.append(["python3", "paths/pathtxt2format.py", treeName])
statements.append("Get numeric paths")

cmd.append(["python3", "rootpath.clustering/step1.dimlimit.py", treeName, mpc])
statements.append("Separate clusters by dim limit")

cmd.append(["python3", "rootpath.clustering/step2.unklimit.py", treeName, maxUnk])
statements.append("Clusters unkown limit")

cmd.append(["python3", "rootpath.clustering/step3.clusterfeatures.py", treeName])
statements.append("Get cluster features file")

cmd.append(["sort -n -k 1 rootpath.clustering/tempFiles/" + treeName +
            ".clusterfeatures.txt > rootpath.clustering/tempFiles/" + treeName +
            "clusterfeatures.sorted.txt"])
statements.append("Sort")

cmd.append(["python3", "rootpath.clustering/step4.join2files.py", treeName])
statements.append("Join cluster features and numeric paths")

cmd.append(["python3", "binfeats/step1.createCommonList.py" , treeName, ">",
            "binfeats/commonandimp/" + treeName + ".commonandimp.txt"])
statements.append("Common features")

cmd.append(["python3", "binfeats/step2.featToBin.py", treeName, mpc])
statements.append("Binary features")

cmd.append(["python3", "splitFeatures/split.py", treeName, mpc, dicSplits])
statements.append("Parallelize features")

cmd.append(["python3", "binadd/step1.makeNaiveOffset.py", treeName, mpc, ">",
            "binadd/tempFiles/" + treeName + ".naiveoffset.txt"])
statements.append("Naive offset")

cmd.append(["cat binadd/tempFiles/" + treeName + ".naiveoffset.txt | wc -l > " +
            "metadata/" + treeName + ".numpaths.txt"])
statements.append("Count paths")

cmd.append(["python3", "binadd/step2.firsthash.py", treeName, ">",
            "binadd/tempFiles/" + treeName + ".firsthash.txt"])
statements.append("First hash")

cmd.append(["sort -k 1 binadd/tempFiles/" + treeName + ".firsthash.txt > " +
            "binadd/tempFiles/" + treeName + ".firsthash.sorted.txt"])
statements.append("Sort")

cmd.append(["python3", "binadd/step3.markconflicts.py", treeName, ">", 
            "binadd/tempFiles/" + treeName + ".firsthash.conflicts.txt"])
statements.append("Mark Conflicts")

cmd.append(["python3", "binadd/step4.combineconflicts.py", treeName, ">",
            "./binadd/tempFiles/" + treeName + ".firsthash.combinedconflicts.txt"])
statements.append("Combine conflicts")

cmd.append(["python3", "binadd/step5.secondhash.py", treeName, numClasses, ">",
            "binadd/tempFiles/" + treeName + ".secondhash.txt"])
statements.append("Second hash")

cmd.append(["sort -k 2 binadd/tempFiles/" + treeName + ".secondhash.txt > " +
            "binadd/tempFiles/" + treeName + ".secondhash.sorted.txt"])
statements.append("Sort")

cmd.append(["python3", "binadd/step6.removehashduplicates.py", treeName, ">", 
            "binadd/tempFiles/" + treeName + ".secondhash.nodup.txt"])
statements.append("Remove duplicate conflicts")

cmd.append(["python3", "binadd/step7.neededbits.py", treeName, ">",
            "metadata/" + treeName + ".bitsperaddline.txt"])
statements.append("Count bits")

cmd.append(["python3", "binadd/step8.tobinary.py", treeName])
statements.append("Binary addresses")

cmd.append(["python3", "splitAddr/split.py", treeName, mpc, tableSplits])
statements.append("Parallelize addresses")
if metrics:
    cmd.append(["python3", "runServer.py", treeName, mpc, numSamples, ergmode,
                "y", dicSplits, tableSplits, dataset])
    statements.append("Compile and run the server with metrics")
    
else:
   cmd.append(["python3", "runServer.py", treeName, mpc, numSamples, ergmode, 
               "n", dicSplits, tableSplits, dataset])
   statements.append("Compile and run the server")
    
i = 0
for command in cmd:
    print(statements[i])
    if len(command) > 1:
        if ">" in command:
            redirectIndex = command.index(">")
            outfile = command[redirectIndex:]
            command = command[:redirectIndex]
            with open(outfile[0], "w+") as f:
                print(command)
                print(outfile)
                p = subprocess.Popen(command, stdout=f)
                status = p.wait()
                if status == 0:
                    print("Succeeded")
                else:
                    print("Failed")
                    exit(1)
        else:
            p = subprocess.Popen(command)
            status = p.wait()
            if status == 0:
                print("Succeeded")
            else:
                print("Failed")
                exit(1)
    else:
        os.system(command[0])
    i = i + 1
    #if i > 2:
        #exit()


