from bitarray import bitarray
import requests
import numpy as np
import socket
import time
import sys
import pickle

predicted = []
times = []


dicSplits = int(sys.argv[2])
count = 1
HOST="127.0.0.1"
PORT=7878
sArr = []
for i in range(dicSplits):
  s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  PORT = PORT + 1
  sArr.append(s)

i = 0
infile = open("server/pythonClient/traffic.dump","rb")
print("Sending from client")
while (i < int(sys.argv[1]) ):
    img = infile.read(11) #11 features, 1 byte each
    for j in range(dicSplits): 
        sArr[j].send(img)
    print(i)
    i=i+1
infile.close()
for j in range(dicSplits):
    sArr[j].close()
print("Client done")


