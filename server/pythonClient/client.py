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
dataset = sys.argv[4]
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

sendTime = endSendTime - startTime
serverTotalTime = pidsDoneTime - startTime

print("Send time was: " + str(sendTime))
print("Server time was: " + str(serverTotalTime))

print("Client done")




