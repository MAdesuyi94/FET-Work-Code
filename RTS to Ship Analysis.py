# -*- coding: utf-8 -*-
"""
Created on Fri May 20 10:55:02 2022

@author: Matthew.Adesuyi
"""

import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import xlwings as xw
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score,roc_auc_score,confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

def territory_assign(terr):
    if terr == 'CT CAN':
        return('CAN')
    elif terr == 'CT USA' or terr == 'CT USA ALASKA' or terr == 'CLP USA' or terr == 'CLP US':
        return('USA')
    elif terr == 'CT EMEA':
        return('EMEA')
    elif terr == 'CT LAM' or terr == 'CLP LAM':
        return('LAM')
    elif terr == 'CT APAC':
        return('APAC')
    elif terr == 'CLP GOM':
        return('GOM')
    else:
        return np.nan

usfc = xw.Book(r"C:\Users\Matthew.Adesuyi\OneDrive - Forum Energy Technologies\Documents\Active Strings Machine Learning.xlsx")
strings = usfc.sheets["Active Strings Clean"].range("A1:T13000").options(pd.DataFrame,index=False).value.dropna(how='all',axis=0)

strings = strings.loc[(pd.isnull(strings['RTS Date'])==False)&(strings['String Status']=='Shipped')]
strings.loc[strings['Territory']=='CT CAN','Country'] = 'Canada'
strings.loc[strings['Territory']=='CT CAN','Basin'] = 'Canada'
strings['Territory'] = strings['Territory'].apply(territory_assign)
strings['Business Unit'] = strings['Pipe Grade'].apply(lambda x: 'Coiled Line Pipe' if 'X' in x else ('Other' if x == 'Other' else 'Coiled Tubing'))
strings['Country'].fillna('Other',inplace=True)
strings['Territory'].fillna('Other',inplace=True)
strings['Customer'].fillna('Other',inplace=True)
strings.loc[8127,'RTS Date'] = pd.Timestamp('2021-12-01 00:00:00')
strings.loc[8100,'RTS Date'] = pd.Timestamp('2021-10-05 00:00:00')
strings['RTS to Ship'] = (strings['Scheduled or Actual Shipping Date'] - strings['RTS Date']).dt.days
strings.loc[(strings['RTS to Ship']<=-1)&(strings['RTS to Ship']>=-30),'RTS to Ship'] = 0
strings = strings.dropna(subset=['RTS to Ship'],axis=0)
strings.drop(strings.loc[strings['RTS to Ship']<0].index,inplace=True)
strings['Year'] = strings['RTS Date'].dt.year
strings['Month'] = strings['RTS Date'].dt.strftime("%B")
strings = strings[['Year','Month','Customer','Territory','Country','Basin','Pipe Grade','Business Unit','RTS to Ship']]
strings['Log RTS to Ship'] = np.log(strings['RTS to Ship']+1)
#strings['RTS to Ship Bins'] = pd.qcut(strings['RTS to Ship'],q=4,precision=1,labels=[1,2,3])
strings['RTS to Ship Bins'] = strings['RTS to Ship'].apply(lambda x: 0 if x<30 else 1)
"""
******************************DATA EXPLORATION*******************************************************
"""
plt.ylim(0,400)
fig1 = plt.figure(figsize=(50,30))
ax1 = fig1.add_subplot()
sns.histplot(data=strings.loc[(strings['RTS to Ship']<500)],x='RTS to Ship',ax=ax1)
ax1.set_title("Histogram of RTS to Ship Time",fontsize=50)
ax1.set_xlabel("RTS to Ship",fontsize=50)
ax1.set_ylabel("Count",fontsize=50)
ax1.tick_params(labelsize=30)
fig1.savefig("Histogram of RTS to Ship Time.png",transparent=True)
plt.show()

fig2 = plt.figure()
ax2 = fig2.add_subplot()

cat_list = ['Territory','Basin','Pipe Grade','Business Unit','Year','Month']
for c in cat_list:
    fig2 = plt.figure(figsize=(50,20))
    ax2 = fig2.add_subplot()
    ax2.set_title(f"RTS to Ship vs {c}",fontsize=50)
    ax2.set(ylim=(0,400))
    ax2.set_xlabel(c,fontsize=50)
    ax2.set_ylabel('RTS to Ship',fontsize=50)
    ax2.tick_params(labelsize=30)
    sns.boxplot(x=c,y='RTS to Ship',data=strings.loc[strings[c]!='Other'],ax=ax2)
    fig2.savefig(f"Boxplot of RTS to Ship vs {c}.png",transparent=True)
    plt.show()

cat_list_2 = ['Business Unit','Territory','Basin','Pipe Grade','Year','Month']
for c in cat_list_2:
    fig3 = plt.figure()
    ax3 = fig3.add_subplot()
    ax3.set(xlim=(0,500))
    sns.displot(x='RTS to Ship',hue=c,kind='kde',data=strings.loc[(strings[c]!='Other')&(strings['RTS to Ship']<500)],fill=True,ax=ax3)

for c in cat_list_2:
    fig3 = plt.figure()
    ax3 = fig3.add_subplot()
    ax3.set(xlim=(0,500))
    sns.displot(x='Log RTS to Ship',hue=c,kind='kde',data=strings.loc[(strings[c]!='Other')],fill=True,ax=ax3)

for c in cat_list_2:
    fig4 = plt.figure()
    ax4 = fig4.add_subplot()
    sns.countplot(x='RTS to Ship Bins',hue=c,data=strings)
    plt.show()
    
df = pd.concat([pd.get_dummies(strings['Territory']),pd.get_dummies(strings['Basin']),
                pd.get_dummies(strings['Customer']),pd.get_dummies(strings['Business Unit'],drop_first=True),
                pd.get_dummies(strings['Country']),pd.get_dummies(strings['Pipe Grade']),
                pd.get_dummies(strings['Year']),pd.get_dummies(strings['Month']),
                strings['RTS to Ship Bins']],axis=1)
df.drop('Other',axis=1,inplace=True)
X = df.drop('RTS to Ship Bins',axis=1)
y = df['RTS to Ship Bins']

Xt,Xv,yt,yv = train_test_split(X,y,test_size=0.25,stratify=y)


lr = LogisticRegression(verbose=1,max_iter=10000,penalty='none',solver='lbfgs')
lr.fit(Xt,yt)
ytpred = lr.predict(Xt)
yt_acc = accuracy_score(yt,ytpred)
yvpred = lr.predict(Xv)
yv_acc = accuracy_score(yv,yvpred)
yt_f1 = f1_score(yt,ytpred,average='macro')
confusion_matrix(yt,ytpred)
confusion_matrix(yv,yvpred)
roc_auc_score(yt,ytpred)
roc_auc_score(yv,yvpred)

dtc = DecisionTreeClassifier()
dtc.fit(Xt,yt)
dtctpred = dtc.predict(Xt)
dtcvpred = dtc.predict(Xv)
ytdtc_acc = accuracy_score(yt,dtctpred)
yvdtc_acc = accuracy_score(yv,dtcvpred)
confusion_matrix(yt,dtctpred)
confusion_matrix(yv,dtcvpred)
roc_auc_score(yv,dtcvpred)
