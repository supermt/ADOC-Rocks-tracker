from sklearn.cluster import DBSCAN
import numpy as np
import pandas as pd
from sklearn import preprocessing

df = pd.read_csv("one-way-anova.csv")
min_max_scaler = preprocessing.MinMaxScaler()

columns_need_normalization = ["std_of_IOPS","mean_of_IOPS"]

# for column in columns_need_normalization:
#     values = min_max_scaler.fit_transform(df[])
#     print(values)
    # df[column] = min_max_scaler.fit_transform(df[column])

X = []
for index in range(len(df)):
    x = np.array([df["std_of_IOPS"][index], df["mean_of_IOPS"][index]])
    X.append(x)

X = np.array(X)

normalized_X = min_max_scaler.fit_transform(X)

clustering = DBSCAN(eps=0.25, min_samples=2).fit(normalized_X)

print(clustering.labels_)