import numpy as np
import sys
from keras.datasets import mnist
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn import tree
import time
import os
import sys

if (len(sys.argv) != 3):
    print "This command takes 2 parameters: python test.py treeName dumpTree?(1/0)\n"
    print "1 means dump trees to ./dot/ directory as dot files"
    exit()
treeName=sys.argv[1]
treeDump=int(sys.argv[2])
curpath = os.path.abspath(os.curdir)


if __name__ == "__main__":
    (X_train, y_train), (X_test, y_test) = mnist.load_data()
    with open(curpath + "/trainOgForest/pkl/" + treeName+".forest.pkl", "rb") as f:
        forest = pickle.load(f)
    print("Loaded")
    i = 0
    #X_test.shape = (10000,784)
    correct = 0
    predictions = []
    misses = []
    start = time.time()
    while (i < 10000):
        #prediction = forest.predict(X_test[i:i+1,:])
        #if ( int(prediction[0]) == int(y_test[i])):
        #     correct = correct + 1
	#else:
	#    misses.append(i)
        i = i + 1
    score = correct / float(i) #accuracy_score(answers, predictions)
    end = time.time()
    with open (curpath + "/temps/"+treeName+".acc.python.txt", "w") as out:
        out.write("Accuracy: "+ str(score)+"\n")
        out.write(str(end - start)+"\n")
    #with open (curpath + "/temps/"+treeName+"acc.txt", "w") as out:
    #   out.write(str(misses))


    if (treeDump == 1):
        i = 0
        for estimator in forest.estimators_:
            #print(curpath)
            name = curpath + "/temps/"+treeName+".tree" + str(i) + ".dot"
            #print(name)
            #print(type(estimator))
            with open(name, "w") as f:
                f = tree.export_graphviz(estimator, out_file=f)
                i = i + 1
