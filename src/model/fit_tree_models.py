# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 20:19:24 2022

@author: CLaug
"""
from sklearn.ensemble import RandomForestRegressor
import os 
import pandas as pd
import pickle
import xgboost as xgb
from sklearn.ensemble import GradientBoostingClassifier

# Import helper functions
from model_helpers import encode_data, rmspe

path = os.path.abspath(os.path.join(__file__ ,"../../.."))

INPUTFILE = path + "\\data\\processed\\processed_times.csv"
OUTPUTFILE = path + "\\models"

## Read file to df
df = pd.read_csv(INPUTFILE, index_col="Unnamed: 0")

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

rf = RandomForestRegressor(n_estimators=500, criterion='mse', random_state=1)
rf.fit(X_train,y_train)

rf_pred = rf.predict(X_test)

print(rmspe(y_test, rf_pred))

pickle.dump(rf, open(OUTPUTFILE + "//random_forest.sav", 'wb'))

#%% Fit XGBoost

xgb_model = xgb.XGBRegressor(objective="reg:squarederror", random_state=42)

xgb_model.fit(X_train, y_train)

XGB_pred = xgb_model.predict(X_test)

print(rmspe(y_test, XGB_pred))

pickle.dump(xgb_model, open(OUTPUTFILE + "//xgboost.sav", 'wb'))

#%% Pull predicted values together
output_df = df[df["Date"]>"2021-07-24 00:00:00"]
output_df = output_df[["Name", "Event", "Time (s)"]]

# Add results from models
output_df["Linear Regression"] = ols_pred3
output_df["Random Forest"] = rf_pred
output_df["XGBoost"] = XGB_pred

# Get errors in seconds
output_df = output_df.melt(id_vars = ["Name", "Event", "Time (s)"], var_name = ["Model"])
output_df["error"] = output_df["Time (s)"] - output_df["value"]

output_df.to_csv(path + "\\data\\output\\processed_times.csv")
