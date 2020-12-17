import numpy as np
import sys
#from keras.datasets import mnist
import pickle
from sklearn.ensemble import RandomForestClassifier

import sys

if (len(sys.argv) != 4):
    print("This command takes 3 parameters: python train.py treeName estimators(int) max_depth(int)\n")
    print("Note: tree name will follow the rest of the compile process.  Choose wisely\n")
    exit()

treeName=sys.argv[1]
treeEst=int(sys.argv[2])
treeDep=int(sys.argv[3])

if __name__ == "__main__":

#    (X_train, y_train), (X_test, y_test) = mnist.load_data()
#    X_train = np.reshape(X_train,(60000,784))
#    forest = RandomForestClassifier(n_estimators=treeEst, max_depth=treeDep)
#    forest.fit(X_train, y_train)
    with open('./trainOgForest/SplitData.pkl', 'rb') as f:
        trainData = pickle.load(f)[0]
    
    X_train = trainData[trainData.columns.difference(['Severity'])].to_numpy()
    y_train = trainData['Severity'].to_numpy()

#    print(y_train)
#    print(y_train.shape)
#    print(X_train)
#    print(X_train.shape)
#    print(X_train[0])
#    exit()
    forest = RandomForestClassifier(n_estimators=treeEst, max_depth=treeDep)
    forest.fit(X_train, y_train)
    print("trained")
    # dump
    with open("trainOgForest/pkl/" + treeName+".forest.pkl", "wb") as f:
        pickle.dump(forest, f, pickle.HIGHEST_PROTOCOL)
    print("Dumped")
