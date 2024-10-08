# -*- coding: utf-8 -*-
"""projectcode.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1pigOSvp3JUHUaaMhoJuJvLGfOkDX_THd
"""

#importing all important libraries

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import time
import datetime as dt
# data preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

data=pd.read_csv('data.csv',encoding="ISO-8859-1")

data.head()

data.shape

data.describe()

data.shape

# removing null values
data.dropna(axis = 0, inplace = True)
print(data.shape)

sns.heatmap(data.isnull())

data=data[data['Quantity']>=0]
data=data[data['UnitPrice']>=0]
print(data.shape)

#add a new col total quantity
data['TotalQuantity']=data['Quantity']*data['UnitPrice']
data.head()

print(data[['InvoiceNo','Country']].groupby('Country').count().sort_values("InvoiceNo",ascending=False))

#top 5 countries sales count wise in cleaned up data
data['Country'].value_counts().head(10).plot(kind='bar')

data[data['TotalQuantity']==data['TotalQuantity'].max()]

items=data['Description'].value_counts().head()
print(items)

print(data[['InvoiceNo','Country','CustomerID','TotalQuantity']].sort_values('TotalQuantity',ascending = False).head(15))

print(data[['InvoiceNo','Country','CustomerID','TotalQuantity']].sort_values('TotalQuantity',ascending = False).head(15))

#rfm analysis
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
data['Date'] = data['InvoiceDate'].apply(lambda x: x.date())
data.head()

data['Month']=data['InvoiceDate'].apply(lambda x:x.month)
data['Year']=data['InvoiceDate'].apply(lambda x:x.year)
data=data.sort_values(by=['Year','Month'])

mmap={1:'Jan11',2:'Feb11',3:'Mar11',4:'Apr11', 5:'May11', 6:'Jun11', 7:'Jul11',8:'Aug11',9:'Sep11',10:'Oct11',11:'Nov11',12:'Dec11'}
data['Month_name']=data['Month'].map(mmap)

def my(x):
    Month=x[0]
    Year=x[1]

    if Year==2010:
        Month='Dec10'
        return Month
    else:
        return Month

data['Month_name']=data[['Month_name','Year']].apply(my, axis=1)

data.head()

#total transactions monthly
monthly=data.groupby(['Year','Month','Month_name']).sum()
monthly.head()

#recency dataframe
recency_df = data.groupby(by='CustomerID', as_index=False)['Date'].max()
recency_df.columns = ['CustomerID','LastPurchaseDate']
recency_df.head(5)

current=dt.date(2021,12,1)
print(current)

recency_df['Recency'] = recency_df['LastPurchaseDate'].apply(lambda x: (current - x).days)
recency_df.drop('LastPurchaseDate',axis = 1,inplace=True)
recency_df.head(5)

#frequency
temp = data.copy()
temp.drop_duplicates(['InvoiceNo','CustomerID'],keep='first',inplace=True)
frequency_df = temp.groupby(by=['CustomerID'], as_index=False)['InvoiceNo'].count()
frequency_df.columns = ['CustomerID','Frequency']
frequency_df.head()

#monetary
monetary_df = data.groupby(by = 'CustomerID',as_index=False).agg({'TotalQuantity':'sum'})
monetary_df.columns = ['CustomerID','TotalQuanity']
monetary_df.head(5)

#create rfm table
rfm_df = recency_df.merge(frequency_df,on='CustomerID').merge(monetary_df,on='CustomerID')
rfm_df.set_index('CustomerID',inplace=True)
rfm_df.head(5)

features=rfm_df.columns
rfm_df.shape

#rfm table visualization
print(rfm_df.corr())
sns.heatmap(rfm_df.corr(),annot=True)

#pca
sc = StandardScaler()
rfm_scaled = sc.fit_transform(rfm_df)
rfm_scaled

from sklearn.decomposition import PCA
pca=PCA()
pca_transformed_data=pca.fit_transform(rfm_scaled)

pca.components_

pca.explained_variance_

var_exp=pca.explained_variance_ratio_
var_exp

#model training
X = rfm_df.copy()
pca = PCA(n_components = 2)
df_pca = pca.fit_transform(X)

df_pca = pd.DataFrame(df_pca)
df_pca.head(5)

#  K-MEANS CLUSTERING
X=df_pca.copy()
cluster_range = range(1, 15)
cluster_errors = []
cluster_sil_scores = []

for num in cluster_range:
    clusters = KMeans(num, n_init = 100,init='k-means++',random_state=0)
    clusters.fit(X)
    # capture the cluster lables
    labels = clusters.labels_
    # capture the centroids
    centroids = clusters.cluster_centers_
    # capture the intertia
    cluster_errors.append( clusters.inertia_ )
clusters_df = pd.DataFrame({ "num_clusters":cluster_range, "cluster_errors": cluster_errors} )
clusters_df[0:10]

X=df_pca.copy()

plt.figure(figsize=(15,6))
plt.plot(clusters_df["num_clusters"],clusters_df["cluster_errors"],marker = 'o')
plt.xlabel('count of clusters')
plt.ylabel('error')

from sklearn.metrics import silhouette_samples, silhouette_score
for num in range(2,10):
    clusters = KMeans(n_clusters=num,random_state=0)
    labels = clusters.fit_predict(df_pca)

    sil_avg = silhouette_score(df_pca, labels)
    print('For',num,'The Silhouette Score is =',sil_avg)

kmeans = KMeans(n_clusters = 6)
kmeans = kmeans.fit(df_pca)
labels = kmeans.predict(df_pca)
centroids = kmeans.cluster_centers_

print(labels)
print()
print('Cluster Centers')
print(centroids)

df_pca['Clusters'] = labels
df_pca.head()

df_pca.head(5)

df_pca['Clusters'].value_counts()

df_pca.head(5)

df_pca.head()

df_pca['Clusters'].value_counts()

df_pca.head()

import plotly.express as px
figure = px.scatter_3d(data,
                    x="UnitPrice",
                    y="Country",
                    z="Quantity",
                    category_orders = {"clusters": ["0", "1", "2", "3", "4"]}
                    )
figure.update_layout()
figure.show()

