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
import scipy.stats
from datetime import timedelta
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from statsmodels.api import OLS
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

path = os.path.dirname(os.path.realpath(__file__))
INPUTFILE = path + "\\processed_times.csv"

## Read file to df
df = pd.read_csv(INPUTFILE, index_col="Unnamed: 0")

#%% Missing values imputation
#model_df.isnull().sum().sort_values(axis=0) # 318 in time since COVID column

imp = SimpleImputer(missing_values=np.nan, strategy='mean')
df["Time (s) change since COVID"] = imp.fit_transform(df[["Time (s) change since COVID"]]).ravel()


#%% Encode 
onehot=True
    
def encode_data(df, onehot, categorical_cols):
    if onehot:
        df = add_constant(df, prepend=False)
        return pd.get_dummies(df, columns=categorical_cols)
    else: 
        enc = LabelEncoder()
        
        df['Location']= enc.fit_transform(df['Location'])
        df['Name']= enc.fit_transform(df['Name'])
        df['Nation']= enc.fit_transform(df['Nation'])
        df['Event']= enc.fit_transform(df['Event'])
        df['Competition_flag']= enc.fit_transform(df['Competition_flag'])
        
        return df


# %% Function for rmspe
def rmspe(y_true, y_pred):
    '''
    Compute Root Mean Square Percentage Error between two arrays.
    '''
    loss = np.sqrt(np.mean(np.square(((y_true - y_pred) / y_true)), axis=0))

    return loss

#%% Linear Regression
# Make sure assumptions are met e.g. shapiro-wilk test, heteroskedasticity
# Normality of response variable, i.e. times
# from scipy.stats import shapiro

#perform Shapiro-Wilk test
# Require a p value>0.05 so we can conclude that there is not sufficient evidence to reject the null hypothesis of normality 
#print(shapiro(model_df["Time (s)"])) # p=0

#model_df["Time (s)"].hist(bins=100)



def perform_regression(df, cols_to_drop):
    
    # Drop the unwanted columns
    df = df.drop(cols_to_drop, axis=1)
    categorical_cols = df.select_dtypes(include='object').columns.values.tolist()
    
    # Perform encoding with the decided predictors, excluding the date in the first column
    model_df = encode_data(df, True, categorical_cols[1:])
    
    
    # Train test split
    train_df = model_df[model_df["Date"]<"2021-07-25 00:00:00"]
    test_df = model_df[model_df["Date"]>"2021-07-24 00:00:00"]
    
    
    X_train = train_df.iloc[:,2:]
    y_train = train_df.iloc[:,1]
    X_test = test_df.iloc[:,2:]
    y_test = test_df.iloc[:,1]
    
    # Transform times with a log transform, to achieve linearity
    y_test = np.log(y_test)
    y_train = np.log(y_train)
    
    # Fit the linear model
    model = OLS(y_train, X_train).fit()
    
    # Get predicted values
    y_pred = model.predict(X_test)
    
    y_test = np.exp(y_test)
    y_pred = np.exp(y_pred)
    
    test_error = rmspe(y_test, y_pred)
                             
    return y_pred, test_error, model

# Review - How well does the model fit?
# Obtain coefficient of determination, r^2

# Durbin-Watson test statistic is close to 2, so no autocorrelation
# Jarque-Bera statistic is far from zero so samples do not have a normal distrubtion

# Produce residual plot - if the plot pattern is random, transform the data
#plt.scatter(residuals,y_pred)
#plt.show()


#%% Call the linear regression model

def output(m):
    
    # R^2: coefficient of determination that tells us that how much percentage variation independent variable can be explained by independent variable
    print("R-squared: ", m.rsquared)
    print('F-statistic:', m.fvalue) 
    print('Probability of observing value at least as high as F-statistic:', m.f_pvalue)
    
    return None

def output_comparison(m1,m2):
    # Is model2 significantly better than model1?
    # Likelihood Ratio test
    # Null Hypothesis: Models fit equally well
    # 2*(Loglik model 1 - loglik model 2)
    print("Likelihood ratio: ", 2*(m1.llf-m2.llf)) # 0.3862

    # LR test critical value with 2 d.f (109-107)
    print("Chi-sq critical value: ", scipy.stats.chi2.ppf(0.95, df=m1.df_model - m2.df_model))

    return None

# First with all predictors
cols_to_drop = []
ols_pred1, ols_error1, model1 = perform_regression(df, cols_to_drop)
print("\nModel1")
output(model1)
# p<0.05 so we can conclude that our model performs better than other simpler model
# t-values show that coefficients for month and time change since covid are not significantly different from 0

# With significant predictors
cols_to_drop = ["Month", "Time (s) change since COVID"]
ols_pred2, ols_error2, model2 = perform_regression(df, cols_to_drop)
print("\nModel2")
output(model2)


# Is model2 significantly better than model1?
output_comparison(model1, model2)
# 0.382 < 5.991 so cannot reject the null hypothesis. 
# This means the full model and the nested model fit the data equally well. 


# Remove multicollinear predictors
cols_to_drop = ["Month", "Time (s) change since COVID", "Year"]
ols_pred3, ols_error3, model3 = perform_regression(df, cols_to_drop)
print("\nModel3")
output(model3)
# All coefficients are signifcant

# Is model3 significantly better than model1?
output_comparison(model1, model3)
# 55.78>7.815 so can reject the null hypothesis. 
# Since model 1 has greater r squared, can conclude that model 1 is significantly better than model 3 at 95% confidence level. 

# Remove non-significant coefficients, as a result of removing year
cols_to_drop = ["Month", "Time (s) change since COVID", "Year", "Nation", "Name"]
ols_pred4, ols_error4, model4 = perform_regression(df, cols_to_drop)
print("\nModel4")
output(model4)

# Is model4 significantly better than model3?
output_comparison(model3, model4)
# 1759.26>110.89 so can reject the null hypothesis. 
# Since model 3 has greater r squared, can conclude that model 3 is significantly better than model 4 at 95% confidence level.

# Choose model3


#%% Mulitcollinearity Investigation
X = df.select_dtypes(include='number').iloc[:,1:] # !!! Select numerical columns instead

# Calculate the varaince inflation factors
vif = pd.Series([variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
                index=X.columns)



