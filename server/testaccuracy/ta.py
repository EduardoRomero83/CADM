from bitarray import bitarray
import requests
import numpy as np
import socket
import time
import sys
import pickle
#from keras.datasets import mnist


#with open("TRANSFORMEDDATA.pkl", "rb") as f:
#    X_test = pickle.load(f)
f = open("server/testaccuracy/temp", "r")
lines = f.readlines()
f.close()

a = open("server/pythonClient/traffic.answers", "r")
alines = a.readlines()
a.close()

i = 0
correct = 0
j=0
while(j < int(sys.argv[1]) ):
#    if i % 2 == 1:
 #       i = i + 1
#       continue
    line = lines[i].split(",")
    line = line[:7]
    responses = [int(x) for x in line]
    resp = responses.index(max(responses))
    #print(resp, int(alines[j].strip()))
    if int(resp) == int(alines[j].strip()):
        correct = correct + 1
    #else:
        #print(j,resp, int(alines[j].strip()), line)        
    i = i + 1
    j = j+1

print("Server Accuracy: " + str(correct/float(i)))
