# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 12:11:59 2021

@author: CLaug
"""
import pandas as pd
import os 
import pickle

# Import helper functions
from model_helpers import perform_regression, regression_output, regression_output_comparison

path = os.path.abspath(os.path.join(__file__ ,"../../.."))

INPUTFILE = path + "\\data\\processed\\processed_times.csv"
OUTPUTFILE = path + "\\models"

## Read file to df
df = pd.read_csv(INPUTFILE, index_col="Unnamed: 0")

#%% Call the linear regression model

# First with all predictors
cols_to_drop = []
ols_pred1, ols_error1, model1 = perform_regression(df, cols_to_drop)
regression_output(model1)
# p<0.05 so we can conclude that our model performs better than other simpler model
# t-values show that coefficients for month and time change since covid are not significantly different from 0

# With significant predictors
cols_to_drop = ["Month", "Time (s) change since COVID"]
ols_pred2, ols_error2, model2 = perform_regression(df, cols_to_drop)
regression_output(model2)


# Is model2 significantly better than model1?
regression_output_comparison(model1, model2)
# 0.382 < 5.991 so cannot reject the null hypothesis. 
# This means the full model and the nested model fit the data equally well. 


# Remove multicollinear predictors
cols_to_drop = ["Month", "Time (s) change since COVID", "Year"]
ols_pred3, ols_error3, model3 = perform_regression(df, cols_to_drop)
regression_output(model3)
# All coefficients are signifcant

# Is model3 significantly better than model1?
regression_output_comparison(model1, model3)
# 55.78>7.815 so can reject the null hypothesis. 
# Since model 1 has greater r squared, can conclude that model 1 is significantly better than model 3 at 95% confidence level. 

# Remove non-significant coefficients, as a result of removing year
cols_to_drop = ["Month", "Time (s) change since COVID", "Year", "Nation", "Name"]
ols_pred4, ols_error4, model4 = perform_regression(df, cols_to_drop)
regression_output(model4)

# Is model4 significantly better than model3?
regression_output_comparison(model3, model4)
# 1759.26>110.89 so can reject the null hypothesis. 
# Since model 3 has greater r squared, can conclude that model 3 is significantly better than model 4 at 95% confidence level.

# Choose model3
pickle.dump(model3, open(OUTPUTFILE + "//linear_model.sav", 'wb'))





