from datetime import datetime
from pytz import timezone
import sklearn.model_selection as skms
from sklearn.preprocessing import LabelEncoder
from collections import defaultdict
from multiprocessing import Pool
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split


#For reference below is code for traffic:
i = 0
# Gets the time length of the event in seconds between [0, 255]
# makes time of day between [0, 255]
# gets the month
# gets the year - 2016 (earliest year)
def getTime(row):

    format = '%Y-%m-%d %H:%M:%S'
    str_start = row['StartTime(UTC)'][:19]
    datetime_start = datetime.strptime(str_start, format)
    str_end = row['EndTime(UTC)'][:19]
    datetime_end = datetime.strptime(str_end, format)
    seconds = (datetime_end - datetime_start).total_seconds()
    seconds = seconds*255/84201515.0
    seconds = int(round(seconds))
    timeOfDay = datetime_start.hour*60*60 + datetime_start.minute*60 + datetime_start.second
    timeOfDay = timeOfDay*255/86400
    timeOfDay = int(round(timeOfDay))
    month = int(datetime_start.month)
    year = int(datetime_start.year - 2016)
    return pd.Series((seconds, timeOfDay, month, year))

# makes latitude a non-negative integer
def normalizeLat(x):
    return int(round(x+90))

# makes longitude a non-negative integer between [0, 255]
def normalizeLng(x):
    return int(round((x+180)*255/360))

# makes distance in miles an integer between [0, 255]
def normalizeDistance(x):
    return int(round(x*10*255/10578))

# makes zipcode an integer between [0, 255]
def normalizeZipCode(x):
    return int(round(int(x)*255/99950))

def preprocessText(x):
    global i
    if i > 1000:
        return ""
    try:    
        text = re.sub('[^a-zA-Z]', ' ', x)
    except:
        print(x)
        return ""
    text = text.lower()
    text = text.split()
    ps = PorterStemmer()
    text = [ps.stem(word) for word in text if not word in set(stopwords.words("english"))]
    text = ' '.join(text)
    i += 1
    return text

    

# thanks nathaniel!
def parallelize_dataframe(df, func, n_cores=4):
    df_split = np.array_split(df, n_cores)
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df

def makeDataSubset(df):
    d = defaultdict(LabelEncoder)
    
    #df[["stars","text"]] = df[["stars","text"]].apply(lambda col: d[col.name].fit_transform(col))

    nan = float("NaN")
    df.replace("", nan, inplace=True)
    df.dropna(inplace=True)
    print("dropped na")
    
    nltk.download('stopwords')
    print("Start preprocess")    
    df['text'] = df['text'].map(lambda x: preprocessText(x))
    print("preprocessed text")

    cv = CountVectorizer(max_features = 1500)

    x = pd.DataFrame(cv.fit_transform(df["text"]).toarray())
    print(x.shape)
    x[1500] = df["stars"].astype(int)
    """
    df['Distance(mi)'] = df['Distance(mi)'].map(lambda x: normalizeDistance(x))
    print("normalized distance")

    df['LocationLat'] = df['LocationLat'].map(lambda x: normalizeLat(x))
    print("normalized lat")

    df['LocationLng'] = df['LocationLng'].map(lambda x: normalizeLng(x))
    print("normalized lng")

    df['ZipCode'] = df['ZipCode'].map(lambda x: normalizeZipCode(x))
    print("normalized zipcode")

    df[['EventLength', 'TimeOfDay', 'Month', 'Year']] = df[['StartTime(UTC)', 'EndTime(UTC)']].apply(lambda row: getTime(row), axis=1)
    print("got time cols")

    df.drop(['StartTime(UTC)', 'EndTime(UTC)'], axis=1, inplace=True)
    print("dropped datetime objects")

    df = df.astype('uint8')
    print("converted type to unsigned 8 bit int") # [0,256]
    """
    return x

# Splits the data into train / test (70/30) batches
def splitData():
    filepath = './trainOgForest/RestaurantsData.csv'
    raw_data = open(filepath, 'rt')
    data = pd.read_csv(raw_data, sep=",", header=0, keep_default_na=False)

    splitData = skms.train_test_split(data, test_size=0.3, shuffle=True)
    with open('./trainOgForest/SplitDataR.pkl', 'wb') as f:
        pickle.dump(splitData, f, pickle.HIGHEST_PROTOCOL)
    print("split and dumped")

# does everything :)
def doEverything():
    # Get restaurant dataset
    rest_path = './trainOgForest/RestaurantReviews.csv'
    rest_raw = open(rest_path, 'rt')
    rest_df = pd.read_csv(rest_raw, sep=",", header=0, keep_default_na=False)
    # Must downsample to about 10000
    rest_df.drop(rest_df.tail(17745000).index, inplace = True)
    # makes a subset of the dataset
    #"review_id","user_id","business_id","stars","date","text","useful","funny","cool"

    rest_df2 = rest_df[["stars","text"]]
    #rest_df2 = makeDataSubset(rest_df2)
    rest_df2 = parallelize_dataframe(rest_df2, makeDataSubset, 24)
    rest_df2.to_csv('./trainOgForest/RestaurantsData.csv', index=False)
    splitData()


if __name__ == "__main__":
    doEverything()
