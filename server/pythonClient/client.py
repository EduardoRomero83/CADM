import os
import psutil
import socket
import sys
import time

predicted = []
times = []

numSamples = int(sys.argv[1])
cores = int(sys.argv[2])
replicas = int(sys.argv[3])
dicSplits = int(sys.argv[4])
tableSplits = int(sys.argv[5])
ergmode = int(sys.argv[6])
dataset = sys.argv[7]
treename = sys.argv[8]
if dataset == "mnist":
    readSize = 28*28
elif dataset == "cifar100":
    readSize = 32*32*3
elif dataset == "traffic":
    readSize = 11 #11 features, 1 byte each
else:  #dataset == "traffic":
    readSize = 1500

splits = cores // replicas


print("Finding processes")
processName = "boltserver"
pids = []
foundProcess = False
while not foundProcess:
    for proc in psutil.process_iter(['pid', 'name']):
        if processName in proc.info['name']:
            pids.append(proc.info['pid'])
            foundProcess = True
print("The pids are: " + str(pids))

time.sleep(1)

count = 1
HOST="127.0.0.1"
PORT=7878
sArr = []
for j in range(replicas):
    replicaSockets = []
    for i in range(splits):
      s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((HOST, PORT))
      PORT = PORT + 1
      replicaSockets.append(s)
    sArr.append(replicaSockets)

infile = open("server/pythonClient/" + dataset + ".dump","rb")
print("Sending from client")

serverOutputFileBase = "server/testaccuracy/temp"
outputFile = "server/testaccuracy/" + treename + ".compiled.txt"

startTime = time.monotonic()

i = 0
while (i < numSamples):
    img = infile.read(readSize)
    offset = i % replicas
    for j in range(splits): 
        sArr[offset][j].send(img)
    if i % 500 == 0:
      print(i)
    i=i+1
infile.close()
for i in range(replicas):
    for j in range(splits):
        sArr[i][j].close()
        
endSendTime = time.monotonic()

if ergmode == 1:
    for pid in pids:
        try:
            os.waitpid(pid, 0)
        except:
            continue
    
    time.sleep(0.1)    
    pidsDoneTime = time.monotonic()
    
    allReplicas = []
    for i in range(replicas):
        replicaCompilation = []
        for j in range(dicSplits):
          for k in range(tableSplits):
              serverOutputFile = serverOutputFileBase + str(i) + "." + str(j) + "." + str(k) + ".txt" 
              with open(serverOutputFile, 'r') as f:
                  predictions = f.readlines()
              samples = []
              for sample in predictions:
                  values = sample.strip().split(',')[:-1]
                  intValues = list(filter(lambda x: x != '', map(int, values)))
                  samples.append(intValues)
              if replicaCompilation == []:
                  replicaCompilation = list(samples)
                  continue
              for l in range(len(samples)):
                  for m in range(len(samples[l])):
                      replicaCompilation[l][m] =  replicaCompilation[l][m] + samples[l][m]
        allReplicas.append(replicaCompilation)
    
    finalAnswers = []  
    for i in range(numSamples):
        replicaIndex = i % replicas
        sampleIndex = i // replicas
        finalAnswers.append(allReplicas[replicaIndex][sampleIndex])
        
    endTime = time.monotonic()
    
    with open(outputFile, 'w+') as f:
        for answer in finalAnswers:
            f.write(str(answer) + "\n")
    
    serverTotalTime = pidsDoneTime - startTime
    totalTime = endTime - startTime
    
    print("Server time was: " + str(serverTotalTime))
    print("Total time was: " + str(totalTime))
    
sendTime = endSendTime - startTime
print("Send time was: " + str(sendTime))
print("Client done")




