# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 12:11:59 2021

@author: CLaug
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import os 
import time
import statsmodels.api as sm
from datetime import timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from statsmodels.api import OLS


path = os.path.dirname(os.path.realpath(__file__))
INPUTFILE = path + "\\processed_times.csv"

## Read file to df
model_df = pd.read_csv(INPUTFILE, index_col="Unnamed: 0")

#%% Train test split
onehot=True

train_df = model_df[model_df["Date"]<"2021-07-25 00:00:00"]
test_df = model_df[model_df["Date"]>"2021-07-24 00:00:00"]

# Remove heats and semi final swims at the olympics
if onehot:
    test_df.drop_duplicates(subset = test_df.columns.difference(["Date", "Time (s)", "Month", "Age at Swim", "PB at Swim"]),
                            keep = 'first', inplace = True)
else:
    test_df.drop_duplicates(subset =["Event", "Name", "Location"],
                            keep = 'first', inplace = True)


X_train = train_df.iloc[:,2:]
y_train = train_df.iloc[:,1]
X_test = test_df.iloc[:,2:]
y_test = test_df.iloc[:,1]

#%% Missing valyes imputation
model_df.isnull().sum().sort_values(axis=0) # 318 in time since COVID column

imp = SimpleImputer(missing_values=np.nan, strategy='mean')
model_df["Time (s) change since COVID"] = imp.fit_transform(model_df[["Time (s) change since COVID"]]).ravel()


#%% Linear Regression
# Make sure assumptions are met e.g. shapiro-wilk test, heteroskedasticity

# Fit the linear model
model = LinearRegression()
model.fit(X_train,y_train)

y_pred = model.predict(X_test)
residuals = y_pred - y_test

print(mean_squared_error(y_test, y_pred))

#print(OLS(y_train, X_train).fit().summary())

#produce residual plot
plt.scatter(residuals,y_pred)
plt.show()

#%% Fit the random forest
classifier = RandomForestRegressor(n_estimators=100, criterion='mse', random_state=1)
classifier.fit(X_train,y_train)

y_pred = classifier.predict(X_test)

print(mean_squared_error(y_test, y_pred))

# Variables to investigate: End of year meet flag, world record at time of swim, improvment over pandemic