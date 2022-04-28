# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 22:00:51 2022

@author: CLaug
"""

import pandas as pd
import numpy as np
import scipy.stats
from sklearn.preprocessing import LabelEncoder
from statsmodels.api import OLS
from statsmodels.tools.tools import add_constant
from statsmodels.stats.outliers_influence import variance_inflation_factor

#%% Encode data to either onehot ecnoding (for linear regression) or label encoding otherwise
    
def encode_data(df, onehot, categorical_cols):
    if onehot:
        df = add_constant(df, prepend=False)
        return pd.get_dummies(df, columns=categorical_cols)
    else: 
        enc = LabelEncoder()
        for col in categorical_cols:
            df[col]= enc.fit_transform(df[col])
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


def regression_output(m):
    
    # R^2: coefficient of determination that tells us that how much percentage variation independent variable can be explained by independent variable
    print("R-squared: ", m.rsquared)
    print('F-statistic:', m.fvalue) 
    print('Probability of observing value at least as high as F-statistic:', m.f_pvalue)
    
    return None

def regression_output_comparison(m1,m2):
    # Is model2 significantly better than model1?
    # Likelihood Ratio test
    # Null Hypothesis: Models fit equally well
    # 2*(Loglik model 1 - loglik model 2)
    print("Likelihood ratio: ", 2*(m1.llf-m2.llf)) # 0.3862

    # LR test critical value with 2 d.f (109-107)
    print("Chi-sq critical value: ", scipy.stats.chi2.ppf(0.95, df=m1.df_model - m2.df_model))

    return None


#%% Mulitcollinearity Investigation

def mc_investigation(df):
    X = df.select_dtypes(include='number').iloc[:,1:] 
    
    # Calculate the varaince inflation factors
    vif = pd.Series([variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
                    index=X.columns)
    
    return vif