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
df = df.dropna()
df = df.reset_index(drop=True)
X = []
for index in range(len(df)):
    x = np.array([df["std_of_IOPS"][index], df["mean_of_IOPS"][index]])
    X.append(x)

X = np.array(X)

normalized_X = min_max_scaler.fit_transform(X)

clustering = DBSCAN(eps=0.012, min_samples=2).fit(normalized_X)

result_map = {}

for index, label in zip(range(len(clustering.labels_)),clustering.labels_):
    temp_list = result_map.get(label,[])
    temp_list.append((df["media"][index],df["io_option"][index]))
    result_map[label] = temp_list
print(result_map)
