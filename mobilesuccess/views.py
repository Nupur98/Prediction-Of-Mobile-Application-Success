from django.shortcuts import render
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
# Create your views here.
def page1(request):
    return render(request,'page1.html')

def page2(request):
    return render(request,'page2.html')

def page3(request):
    df_apps = pd.read_csv("googleplaystorerecord2.csv")
    category = request.POST['category']
    size = request.POST['size']
    price = request.POST['price']
    content = request.POST['content']
    genres = request.POST['genres']
    android = request.POST['andver']
    
    dic = {"Category":category,"Size":size,"Price":price,"Content Rating":content,"Genres":genres,"Android Ver":android}
    print(category,size,price,content,genres)
    df_apps=df_apps.drop(['Rating','App','Reviews','Type','Last Updated','Current Ver','Installs'],axis=1)
    popApps = df_apps.copy()
    popApps.append(dic,ignore_index=True)
    # popApps = popApps.drop_duplicates()
    popApps["Price"] = popApps["Price"].str.replace("$","")
    popApps["Price"] = popApps["Price"].astype(float)
    popApps["Size"] = popApps["Size"].str.replace("Varies with device","0")
    popApps["Size"] = popApps["Size"].str.replace("1,000+","0")
    popApps["Size"] = (popApps["Size"].replace(r'[kM]+$', '', regex=True).astype(float) *\
    popApps["Size"].str.extract(r'[\d\.]+([kM]+)', expand=False).fillna(1).replace(['k','M'], [10**3, 10**6]).astype(int))
    countPop = popApps[popApps["Size"] == 0.0].count()
    mid=popApps.Size.median()
    popApps.loc[popApps.Size == 0.0, 'Size'] = mid
    a = popApps.loc[df_apps["Content Rating"].isnull()]
    popApps=popApps.drop( axis=0,index=a.index)
    popApps["Genres"] = popApps["Genres"].str.replace(";","&")
    countPop = popApps[popApps["Android Ver"] == "Varies with device"].count()
    popApps["Android Ver"] = popApps["Android Ver"].str.replace("Varies with device","4.0")
    popApps['Android Ver']=popApps["Android Ver"].str.replace(" and up","")
    popApps['Android Ver'] = (popApps['Android Ver'].str.slice(0,3))
    popApps=popApps.rename(columns={"Android Ver": "AndroidVer"})
    popApps.AndroidVer.fillna("4.0",inplace=True)
    label_encoder = preprocessing.LabelEncoder() 
    popApps['Category']= label_encoder.fit_transform(popApps['Category'])
    popApps['Content Rating']= label_encoder.fit_transform(popApps['Content Rating']) 
    popApps['Genres']= label_encoder.fit_transform(popApps['Genres'])
    popApps['AndroidVer'] = popApps['AndroidVer'].astype(float)
    df = pd.DataFrame(popApps,columns=['Category','Size','Price','Content Rating','Genres','AndroidVer'])[:-1]
    y = popApps.Popular[:-1]
    input = popApps.iloc[-1]
    X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.3)
    X_test.append(input,ignore_index=True)
    popularity_classifier = DecisionTreeClassifier()
    popularity_classifier.fit(X_train, y_train)
    predictions = popularity_classifier.predict(X_test)
    print(predictions[-1])
    context = {
        'output':predictions[-1]
    }
    return render(request,'page3.html',context)