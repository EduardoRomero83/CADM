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
elif dataset == "traffic":
    readSize = 11 #11 features, 1 byte each
else:  #dataset == "traffic":
    readSize = 1500

splits = cores // replicas

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

print("Finding processes")
processName = "boltserver"
pids = []
for proc in psutil.process_iter(['pid', 'name']):
    if processName in proc.info['name']:
        pids.append(proc.info['pid'])
print("The pids are: " + str(pids))

if dataset == "mnist":
    infile = open("server/pythonClient/mnist.dump","rb")
else:
    infile = open("server/pythonClient/traffic.dump","rb")
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

for pid in pids:
    try:
        os.waitpid(pid, 0)
    except:
        continue
    
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
              print(sample)
              values = sample.strip().split(',')
              print(values)
              intValues = list(filter(lambda x: x != '', map(int, values)))
              print(intValues)
              samples.append(intValues)
          print("samples have elements: " + str(len(samples)))
          print("each with elements: " + str(len(samples[0])))
          if replicaCompilation == []:
              replicaCompilation.append(samples)
              print("Replicacomp was empty")
              continue
          for l in range(len(samples)):
              for m in range(len(samples[l])):
                  print("Replicacomp was full")
                  replicaCompilation[l][m] =  replicaCompilation[l][m] + samples[l][m]
    allReplicas.append(replicaCompilation)

finalAnswers = []  
print(len(allReplicas[0]))  
for i in range(numSamples):
    replicaIndex = i % replicas
    sampleIndex = i // replicas
    finalAnswers.append(allReplicas[replicaIndex][sampleIndex])
    
endTime = time.monotonic()

with open(outputFile, 'wb+') as f:
    for answer in finalAnswers:
        f.write(str(answer))

sendTime = endSendTime - startTime
serverTotalTime = pidsDoneTime - startTime
totalTime = endTime - startTime

print("Send time was: " + str(sendTime))
print("Server time was: " + str(serverTotalTime))
print("Total time was: " + str(totalTime))

print("Client done")




