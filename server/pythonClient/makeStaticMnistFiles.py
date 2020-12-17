from bitarray import bitarray
import requests
import numpy as np
import socket
import time
import sys
import pickle
#from keras.datasets import mnist

#(X_train, y_train), (X_test, y_test) = mnist.load_data()
#X_test = X_test[:, np.newaxis, :, :]
#X_test = X_test.reshape(10000,784)

with open('./trainOgForest/SplitData.pkl', 'rb') as f:
    testData = pickle.load(f)[1]
print "loaded testData"
X_test = testData[testData.columns.difference(['Severity'])].to_numpy()
y_test = testData['Severity'].to_numpy()
X_test = X_test.astype('uint8', order='C', copy=False)
y_test = y_test.astype('uint8', copy=False)
print X_test.dtype
print y_test.dtype
#exit()

predicted = []
times = []

#with open("TRANSFORMEDDATA.pkl", "rb") as f:
#    X_test = pickle.load(f)


count = 1
HOST="127.0.0.1"
PORT=7878
#s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((HOST, PORT))
i = 0
trafficdump = open ("traffic.dump", "wb") 
for x in X_test:
    #if i < 1:
	#i = i + 1
	#continue
    #newX = x.tolist()
    #a = bitarray()
    #for n in newX:	
    #	print n
    #	a.append(bin(int(n))[2:].zfill(16))
    #print a.length()
    #print len(bytearray(x.tolist()))
    #for r in range (0, 400):
    #    print sys.getsizeof(x[r]);
    #print y_test[1]

#    for x1 in x:
#	for x2 in x1:
#	    for x3 in x2:
#	        print x3
#    print x
#    exit()
    trafficdump.write(x)
    #s.send(x)
trafficdump.close()

trafficanswers = open ("traffic.answers", "w") 
for y in y_test:
    trafficanswers.write(str(y)) 
    trafficanswers.write("\n")

trafficanswers.close()

    #exit()
    #time.sleep(20000)
    #r = requests.post("http://127.0.0.1:7878", data={'number':x.tolist()})
    #array = r.json()['respArray']
    #predicted.append(array.index(max(array)))
    #times.append(r.elapsed.microseconds)
    #print "%d: response time: %d" %(count,r.elapsed.microseconds)
    #if array.index(max(array)) == y_test[count]:
    #    print "%d: correct" %(count)
    #count=count+1

#print "Average response time: %d" %((sum(times)/len(times)))
#print "Longest response time: %d" %(max(times))

#correct = 0
#for i in range(len(predicted)):
#    if predicted[i] == y_test[i]:
#	correct = correct + 1

#print "Accuracy was: %f" %((correct / len(predicted)* 100))

