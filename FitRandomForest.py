# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 20:19:24 2022

@author: CLaug
"""
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import os 
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.ensemble import GradientBoostingClassifier

path = os.path.dirname(os.path.realpath(__file__))
INPUTFILE = path + "\\processed_times.csv"
OUTPUTFILE = path + "\\predicted_times.csv"

## Read file to df
df = pd.read_csv(INPUTFILE, index_col="Unnamed: 0")

#%% Missing values imputation
#model_df.isnull().sum().sort_values(axis=0) # 318 in time since COVID column

imp = SimpleImputer(missing_values=np.nan, strategy='mean')
df["Time (s) change since COVID"] = imp.fit_transform(df[["Time (s) change since COVID"]]).ravel()

#%% Prep
# Drop the unwanted columns
categorical_cols = df.select_dtypes(include='object').columns.values.tolist()

# Perform encoding with the decided predictors, excluding the date in the first column
model_df = encode_data(df, False, categorical_cols[1:])


# Train test split
train_df = model_df[model_df["Date"]<"2021-07-25 00:00:00"]
test_df = model_df[model_df["Date"]>"2021-07-24 00:00:00"]


X_train = train_df.drop(["Time (s)", "Date"], axis=1)
y_train = train_df.iloc[:,4]
X_test = test_df.drop(["Time (s)", "Date"], axis=1)
y_test = test_df.iloc[:,4]

#%% Fit random forest 

classifier = RandomForestRegressor(n_estimators=500, criterion='mse', random_state=1)
classifier.fit(X_train,y_train)

RF_pred = classifier.predict(X_test)

print(rmspe(y_test, RF_pred))


#%% Fit XGBoost

xgb_model = xgb.XGBRegressor(objective="reg:squarederror", random_state=42)

xgb_model.fit(X_train, y_train)

XGB_pred = xgb_model.predict(X_test)

print(rmspe(y_test, XGB_pred))

#%% Pull predicted values together
output_df = df[df["Date"]>"2021-07-24 00:00:00"]
output_df = output_df[["Name", "Event", "Time (s)"]]

# Add results from models
output_df["Linear Regression"] = ols_pred3
output_df["Random Forest"] = RF_pred
output_df["XGBoost"] = XGB_pred

# Get errors in seconds
output_df = output_df.melt(id_vars = ["Name", "Event", "Time (s)"], var_name = ["Model"])
output_df["error"] = output_df["Time (s)"] - output_df["value"]

output_df.to_csv(OUTPUTFILE)
