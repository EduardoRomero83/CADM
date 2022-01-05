import numpy as np
import sys
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn import tree
import pandas as pd
import time
import os
import sys

if (len(sys.argv) != 4):
    print("This command takes 3 parameters: python test.py treeName dumpTree?(1/0) dataset\n")
    print("1 means dump trees to ./dot/ directory as dot files")
    exit()
treeName=sys.argv[1]
treeDump=int(sys.argv[2])
dataset = sys.argv[3]
curpath = os.path.abspath(os.curdir)

if dataset == "mnist":
    from keras.datasets import mnist

if __name__ == "__main__":
    if dataset == "mnist":
        (X_train, y_train), (X_test, y_test) = mnist.load_data()
        X_test.shape = (10000,784)
    elif dataset == "traffic":
        with open('./trainOgForest/SplitData.pkl', 'rb') as f:
            testData = pickle.load(f)[1]
        print("loaded testData")

        X_test = testData[testData.columns.difference(['Severity'])].to_numpy()
        y_test = testData['Severity'].to_numpy()
    else:
        with open('./trainOgForest/SplitDataR.pkl', 'rb') as f:
            testData = pickle.load(f)[1]
        print("loaded testData")

        X_test = testData[testData.columns.difference(['stars'])].to_numpy()
        y_test = testData['stars'].to_numpy()
        print(X_test.shape)


    with open(curpath + "/trainOgForest/pkl/" + treeName+".forest.pkl", "rb") as f:
        forest = pickle.load(f)
    print("Loaded tree")

    i = 0
    correct = 0
    predictions = forest.predict(X_test)
    print("Made predictions")
    misses = []
    start = time.time()
    while (i < X_test.shape[0]):
        prediction = forest.predict(X_test[i:i+1,:])
        if (predictions[i] == y_test[i]):
            correct = correct + 1
        else:
            misses.append(i)
        i = i + 1
    score = correct / float(i) #accuracy_score(answers, predictions)
    end = time.time()
    print(str(end - start))
    with open (curpath + "/ResearchData/raw/"+treeName+".acc.python.txt", "w") as out:
        out.write("Accuracy: "+ str(score)+"\n")
        out.write(str(end - start)+"\n")
    #with open (curpath + "/temps/"+treeName+"acc.txt", "w") as out:
    #   out.write(str(misses))
    print("tested")

    if (treeDump == 1):
        i = 0
        for estimator in forest.estimators_:
            #print(curpath)
            name = curpath + "/trainOgForest/dot/"+treeName+".tree" + str(i) + ".dot"
            #print(name)
            #print(type(estimator))
            with open(name, "w") as f:
                f = tree.export_graphviz(estimator, out_file=f)
                i = i + 1
