import numpy as np
import sys
import pickle
from sklearn.ensemble import RandomForestClassifier

import sys

if (len(sys.argv) != 5):
    print("This command takes 4 parameters: python train.py treeName estimators(int) max_depth(int) dataset\n")
    print("Note: tree name will follow the rest of the compile process.  Choose wisely\n")
    exit()

treeName=sys.argv[1]
treeEst=int(sys.argv[2])
treeDep=int(sys.argv[3])
dataset = sys.argv[4]

if dataset == "mnist":
    from keras.datasets import mnist

if __name__ == "__main__":
    if dataset == "mnist":
        (X_train, y_train), (X_test, y_test) = mnist.load_data()
        X_train = np.reshape(X_train,(60000,784))
        forest = RandomForestClassifier(n_estimators=treeEst, max_depth=treeDep)
        forest.fit(X_train, y_train)
    elif dataset == "traffic":
        with open('./trainOgForest/SplitData.pkl', 'rb') as f:
            trainData = pickle.load(f)[0]
        X_train = trainData[trainData.columns.difference(['Severity'])].to_numpy()
        y_train = trainData['Severity'].to_numpy()
    else:
        with open('./trainOgForest/SplitDataR.pkl', 'rb') as f:
            trainData = pickle.load(f)[0]
        X_train = trainData[trainData.columns.difference(['stars'])].to_numpy()
        y_train = trainData['stars'].to_numpy()
        print(X_train.shape)
        print(X_train[0])
        print(X_train.dtype)
        print(X_train[0].dtype)


    forest = RandomForestClassifier(n_estimators=treeEst, max_depth=treeDep)
    """for i in range(len(X_train)):
        print(i)
        forest.fit([X_train[i]], [y_train[i]])"""
    forest.fit(X_train, y_train)
    print("trained")
    # dump
    with open("trainOgForest/pkl/" + treeName+".forest.pkl", "wb") as f:
        pickle.dump(forest, f, pickle.HIGHEST_PROTOCOL)
    print("Dumped")
