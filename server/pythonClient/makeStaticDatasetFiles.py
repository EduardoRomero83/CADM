import numpy as np
import pickle
from keras.datasets import mnist
from keras.datasets import cifar100

dataset = "restaurant"

if dataset == "mnist":
    (X_train, y_train), (X_test, y_test) = mnist.load_data()
    X_test.shape = (10000,784)
elif dataset == "cifar100":
    (X_train, y_train), (X_test, y_test) = cifar100.load_data()
    X_test.shape = (10000,3072)
elif dataset == "traffic":
    with open('./trainOgForest/SplitData.pkl', 'rb') as f:
        testData = pickle.load(f)[1]
    print("loaded testData traffic")

    X_test = testData[testData.columns.difference(['Severity'])].to_numpy()
    y_test = testData['Severity'].to_numpy()
else:
    with open('./trainOgForest/SplitDataR.pkl', 'rb') as f:
        testData = pickle.load(f)[1]
    print("loaded testData restaurant")

    X_test = testData[testData.columns.difference(['stars'])].to_numpy()
    X_test = np.ascontiguousarray(X_test)
    y_test = testData['stars'].to_numpy()
    print(X_test.shape)


predicted = []
times = []


dumpfile = open (dataset + ".dump", "wb") 
for x in X_test:
    dumpfile.write(x)
dumpfile.close()

answers = open (dataset + ".answers", "w") 
for y in y_test:
    answers.write(str(y)) 
    answers.write("\n")

answers.close()


