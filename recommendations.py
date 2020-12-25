# -*- coding: utf-8 -*-
"""recommendations.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SmMmUNexgV6KwgFNjBGfUC9PmRjc100L
"""

import os
import pandas as pd
from sklearn import preprocessing
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

store = {}
df = pd.read_csv('./dataset/googleplaystore_user_reviews.csv')

#preprocessing dataset (removing null values)
df = df[df['Translated_Review'].notna()]
index_names = df[ df['Translated_Review'] == "nan" ].index 
df.drop(index_names, inplace = True)

for index, row in df.iterrows():
  if row['App'] in store:
    store[row['App']]+=row['Translated_Review']
  else:
    store[row['App']]=row['Translated_Review']

list_reviews = []
for key, value in store.items():
  list_reviews.append([key,value])

#creating a dataset of app reviews (concatenated)
data_reviews = pd.DataFrame(list_reviews,columns=['App','Translated_Review'])
data_reviews.set_index('App', inplace=True)

#printing list of apps which have reviews (not all apps have reviews )
# for index,rows in data_reviews.iterrows():
#   print(index)

data = pd.read_csv('/content/dataset/googleplaystore.csv',index_col = "App")
data["App Name"]=data.index

#removing duplicate entries
data.drop_duplicates(subset=['App Name'], keep='first',inplace = True)

data.Type = pd.Categorical(data.Type)
data.Type=data.Type.astype('category').cat.codes

print(data.head())
# for i in data.iloc[0]:
#   print(i)

#taking inputs
app_name = input("Write app name:\t")
num_rec = int(input("Write number of recommendations:\t"))

matching_apps_index=data["App Name"].str.contains(app_name, case= False)
matching_apps = data[matching_apps_index]

# for i in range(0,len(matching_apps.axes[0])):
#   print("Recommending for app: ",matching_apps.iloc[i][12])

if len(matching_apps)==0:
  print("NO SUCH APP")
else:
  given_app=matching_apps.iloc[0,:]
  print("Recommending for app: ",given_app[12])
  print(given_app)

data = data.loc[data['Category'] == given_app[0]]


#app name
tf = TfidfVectorizer(analyzer='word', stop_words='english')
tfidf_matrix = pd.DataFrame((tf.fit_transform(data.index)).toarray(),index=data.index)
matrix = cosine_similarity(tfidf_matrix,[tfidf_matrix.loc[given_app[12]]])


#app reviews
tf = TfidfVectorizer(analyzer='word', stop_words='english')
tfidf_matrix = pd.DataFrame((tf.fit_transform(data_reviews['Translated_Review'])).toarray(),index=data_reviews.index)

reviews_similarity = {}
for index, row in data.iterrows():
    reviews_similarity[index]=0

if given_app[12] in data_reviews.index:
  matrix_reviews = cosine_similarity(tfidf_matrix,[tfidf_matrix.loc[given_app[12]]])
  for i in range(0,len(matrix_reviews)):
    reviews_similarity[data_reviews.index[i]]=matrix_reviews[i][0]

else:
  print("No reviews found")

list_similarities = []

for i in range(0,len(matrix)):
  list_similarities.append([matrix[i][0]+reviews_similarity[data.index[i]],data.index[i],matrix[i][0],reviews_similarity[data.index[i]]])
list_similarities.sort(reverse = True)

final_simi = {}
for entry in list_similarities:
  if entry[0] !=0 and entry[1] != given_app[12]:
    final_simi[entry[1]]=entry[0]
    # print(entry[0],entry[1])

buckets = []

ranges = []
ranges.append([1.5,2.0])
ranges.append([1.0,1.5])
ranges.append([0.6,1.0])
ranges.append([0.4,0.6])
ranges.append([0.3,0.4])
ranges.append([0.25,0.3])
ranges.append([0.2,0.25])
ranges.append([0.15,0.2])
ranges.append([0.1,0.15])
ranges.append([0.075,0.1])

low = 1.5
high = 2.0
temp= []
for entry in list_similarities:
  if entry[0] <= high and entry[0] > low:
    temp.append(entry[1])
buckets.append(temp)

for ran in ranges:
  low = ran[0]
  high = ran[1]
  temp= []
  for entry in list_similarities:
    if entry[0] <= high and entry[0] > low:
      temp.append(entry[1])
  buckets.append(temp)

final_ans=[]
final_simi[given_app[12]]=2.0
for entry in buckets:
  if len(entry) > 0:
    index_names=entry
    data_temp=data.loc[index_names]
    final_data = data_temp.sort_values(by=['Rating'], ascending=False)
    for index,row in final_data.iterrows():
      if index!=given_app[12]:
        final_ans.append([index,row['Rating'],final_simi[index]])
    # print(entry)

#printing recommendations
if len(final_ans)==0:
  print("No Good recommendations")
else:
  print("App,\t Rating,\t Similarity_measure")
  for i in range(0,min(num_rec,len(final_ans))):
    print(final_ans[i][0],'\t',final_ans[i][1],'\t',round(final_ans[i][2],3))

