from bitarray import bitarray
import requests
import numpy as np
import socket
import time
import sys
import pickle

predicted = []
times = []

dataset = sys.argv[3]
if dataset == "mnist":
    readSize = 28*28
else:
    readSize = 11 #11 features, 1 byte each

cores = int(sys.argv[2])
count = 1
HOST="127.0.0.1"
PORT=7878
sArr = []
for i in range(cores):
  s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  PORT = PORT + 1
  sArr.append(s)

i = 0
if dataset == "mnist":
    infile = open("server/pythonClient/mnist.dump","rb")
else:
    infile = open("server/pythonClient/traffic.dump","rb")
print("Sending from client")
while (i < int(sys.argv[1]) ):
    img = infile.read(readSize)
    for j in range(cores): 
        sArr[j].send(img)
    if i % 500 == 0:
      print(i)
    i=i+1
infile.close()
for j in range(cores):
    sArr[j].close()
print("Client done")


