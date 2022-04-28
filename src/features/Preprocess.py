# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 20:13:08 2021

@author: CLaug
"""

# Import packages
import pandas as pd
import numpy as np
import os 
from datetime import datetime
from sklearn.impute import SimpleImputer


path = os.path.abspath(os.path.join(__file__ ,"../../.."))
INPUTFILE = path + "\\data\\raw\\times.csv"
OUTPUTFILE = path + "\\data\\processed\\processed_times.csv"

# Import helper functions
from helpers import to_seconds, competition

#%% Preprocess

## Read file to df
df = pd.read_csv(INPUTFILE, index_col="Unnamed: 0")

# Rename, clean, change data types
df = df.rename({"Long Course (50m)": "Time",
                "Long Course (50m).1": "FINA Points",
                "Long Course (50m).2": "Date",
                "Long Course (50m).3": "Location"},
               axis="columns")

df["Date"] = pd.to_datetime(df["Date"])
df["DOB"] = pd.to_datetime(df["DOB"], format='%Y')


# Change times to seconds
df["Time"] = df["Time"].replace({'M':''}, regex=True)
df['Time (s)'] = df['Time'].apply(to_seconds).astype(float)

# Extract the motnh, year from the datetime variable
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year

# Calculate the age at the date of swim
df['Age at Swim'] = (df['Date']-df['DOB'])
df['Age at Swim'] = df['Age at Swim'].dt.total_seconds() / (24 * 60 * 60)

# Calculate the pb on the date of the swim
PBs = []
PB = 100000
prev_name = 0
prev_event = 0

df = df.sort_values(["Name", "Event","Date"])

# Iterate through the rows
for _, row in df.iterrows():
    name = row["Name"]
    event = row["Event"]
    time = row["Time (s)"]
    
    if name!=prev_name or event!=prev_event:
        PB=100000
    if time < PB: # if new time is lower than PB then set as PB
        PBs.append(time)
        PB = time
    else: PBs.append(PB)
    
    prev_name=name
    prev_event=event
    
df["PB at Swim"] = PBs

# Also calculate whether swim was a final, using similar logic but dates need to be ascending
finals = []
prev_event = 0
prev_date = datetime(1900, 1, 1)
prev_location = "x"


df = df.sort_values(["Name", "Event","Date"], ascending=False)
# Iterate through the rows
for _, row in df.iterrows():
    event = row["Event"]
    date = row["Date"]
    location = row["Location"]
    
    if event==prev_event and location == prev_location and (date-prev_date).days < 7:
        finals.append("H")
    else: finals.append("F")
    
    prev_event=event
    prev_location=location
    prev_date=date
       
df["final_flag"] = finals
# Remove the heat swims as they don't represent the swimmers best performance at the time
df = df[df["final_flag"] == "F"]


df["Competition_flag"] = df.apply(competition, axis=1)



# Calculate improvement after pandemic
# Filter by dates befroe and after pandemic
reduced_df = df[df["Date"]>"2019-01-01 00:00:00"]
reduced_df = reduced_df[reduced_df["Date"]<"2021-07-20 00:00:00"]

# Find difference between average time before pandemic and after
postCOVID = reduced_df[reduced_df["Date"]>"2021-01-01 00:00:00"].groupby(["Name", "Event"]).agg({"Time (s)":"mean"})
preCOVID = reduced_df[reduced_df["Date"]<"2020-03-01 00:00:00"].groupby(["Name", "Event"]).agg({"Time (s)":"mean"})
changeCOVID = postCOVID - preCOVID

df = df.join(changeCOVID, how = 'left', on=["Name", "Event"], rsuffix=" change since COVID")


# Missing values imputation
#model_df.isnull().sum().sort_values(axis=0) # 318 in time since COVID column
imp = SimpleImputer(missing_values=np.nan, strategy='mean')
df["Time (s) change since COVID"] = imp.fit_transform(df[["Time (s) change since COVID"]]).ravel()


# Remove irrelevant columns for regression
df.drop(['Time', 'DOB', 'FINA Points', 'Club', 'Location', 'final_flag'], axis=1, inplace=True)

df.to_csv(OUTPUTFILE)
    

