# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 21:13:28 2022

@author: CLaug
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os 
import pandas as pd

path = os.path.dirname(os.path.realpath(__file__))
INPUTFILE = path + "\\processed_times.csv"

## Read file to df
df = pd.read_csv(INPUTFILE, index_col="Unnamed: 0")

#%% Plot pair plot on numerical columns
X = df.select_dtypes(include='number').iloc[:,1:]
sns.pairplot(X)

#%% Plot subplots
def plot_scatter(df):
    # Create figure
    fig = plt.figure(figsize=(10,14))
    
    # Define Data Coordinates
    y = df["Time (s)"]
    
    # Counter for for loop
    i=1
    
    # Create each subplot individually
    for name, values in df.drop(["Time (s)", "Name", "Nation", "Date"], axis=1).iteritems():
      plt.subplot(4, 3, i)
      plt.xlabel(name)
      if name == "Event":
          plt.xticks(fontsize=1)
           
      plt.scatter(values, y, s=0.3)
      
      i += 1 
      
    #plt.tight_layout()
    plt.show()
    
    return None

#%% Call plots

# Select one event
df_100brs = df[df["Event"] == "100m Breaststroke"]
df_100brs["age_at_swim_tr"] = np.power(df_100brs["Age at Swim"], 0.5)
plot_scatter(df_100brs)

