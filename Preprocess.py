# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 20:13:08 2021

@author: CLaug
"""

import pandas as pd
import numpy as np
import re
import os 
import time
from datetime import timedelta
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
from datetime import datetime

path = os.path.dirname(os.path.realpath(__file__))
INPUTFILE = path + "\\times.csv"
OUTPUTFILE = path + "\\processed_times.csv"

def preprocess(INPUTFILE):
    
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
    
    # Convert time to seconds 
    def to_seconds(s):
        if ":" in s:
            mins, secs = map(float, s.split(":"))
            td = timedelta(minutes=mins, seconds=secs)
            return td.total_seconds()
        else: return s
    
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
    
    # Competition flags
    def competition(s):
        date = datetime.strptime(str(s["Date"]), "%Y-%m-%d %H:%M:%S")
        # Olympics 
        if (date > datetime(2021, 7, 23)
            and date < datetime(2021, 8, 8)
            and s['Location'] == "Tokyo (JPN)") or (date > datetime(2016, 8, 5) 
            and date < datetime(2016, 8, 21) 
            and s['Location'] == "Rio (BRA)") or (date > datetime(2012, 7, 27) 
            and date < datetime(2012, 8, 12) 
            and s['Location'] == "London (GBR)"):
            return "O"
        # Wold Championships
        elif (date > datetime(2019, 7, 21) 
            and date < datetime(2019, 7, 28) 
            and s['Location'] == "Gwangju (KOR)") or (date > datetime(2017, 7, 14)  
            and date < datetime(2017, 7, 23)
            and s['Location'] == "Budapest (HUN)") or (date > datetime(2015, 7, 24)
            and date < datetime(2015, 8, 9) 
            and s['Location'] == "Kazan (RUS)") or (date > datetime(2013, 7, 20) 
            and date < datetime(2013, 8, 4) 
            and s['Location'] == "Barcelona (ESP)"):
            return "W"
        else:
            return "N"
    
    df["Competition_flag"] = df.apply(competition, axis=1)
    
    # Calculate improvement after pandemic
    reduced_df = df[df["Date"]>"2019-01-01 00:00:00"]
    reduced_df = reduced_df[reduced_df["Date"]<"2021-07-20 00:00:00"]
    
    # Find difference between average time before pandemic and after
    postCOVID = reduced_df[reduced_df["Date"]>"2021-01-01 00:00:00"].groupby(["Name", "Event"]).agg({"Time (s)":"mean"})
    preCOVID = reduced_df[reduced_df["Date"]<"2020-03-01 00:00:00"].groupby(["Name", "Event"]).agg({"Time (s)":"mean"})
    changeCOVID = postCOVID - preCOVID
    
    df = df.join(changeCOVID, how = 'left', on=["Name", "Event"], rsuffix=" change since COVID")
    
    # return df[["Date", "Time (s)", "Location", "Name", "Nation", "Event", "Month", "Year", "Age at Swim", "PB at Swim", "Time (s) change since COVID"]]
    return df

#%% Encoding categorical variables
onehot=True

def encode_data(model_df, onehot, OUTPUTFILE):
    categorical_cols = ['Location', 'Name', 'Nation', 'Event']
    
    if onehot:
        encoded_data = pd.get_dummies(model_df, columns=categorical_cols)
        encoded_data.to_csv(OUTPUTFILE)
    else: 
        enc = LabelEncoder()
        
        model_df['Location']= enc.fit_transform(df['Location'])
        model_df['Name']= enc.fit_transform(df['Name'])
        model_df['Nation']= enc.fit_transform(df['Nation'])
        model_df['Event']= enc.fit_transform(df['Event'])
        
        model_df.to_csv(OUTPUTFILE)

temp = preprocess(INPUTFILE)
encode_data(preprocess(INPUTFILE), onehot, OUTPUTFILE)