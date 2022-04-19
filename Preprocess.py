# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 20:13:08 2021

@author: CLaug
"""

import pandas as pd
import os 
from datetime import timedelta
from datetime import datetime

path = os.path.dirname(os.path.realpath(__file__))
INPUTFILE = path + "\\times.csv"
OUTPUTFILE = path + "\\processed_times.csv"

def preprocess(INPUTFILE, OUTPUTFILE):
    
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
    # Also calculate whether swim was a final
    PBs = []
    finals = []
    PB = 100000
    prev_name = 0
    prev_event = 0
    prev_date = datetime(1900, 1, 1)
    prev_location = "x"
    
    df = df.sort_values(["Name", "Event","Date"])
    
    # Iterate through the rows
    for _, row in df.iterrows():
        name = row["Name"]
        event = row["Event"]
        time = row["Time (s)"]
        date = row["Date"]
        location = row["Location"]
        
        if name!=prev_name or event!=prev_event:
            PB=100000
        if time < PB: # if new time is lower than PB then set as PB
            PBs.append(time)
            PB = time
        else: PBs.append(PB)
        
        if event==prev_event and location == prev_location and (date-prev_date).days < 7:
            finals.append("F")
        else: finals.append("H")
        
        prev_name=name
        prev_event=event
        prev_location=location
        prev_date=date
        
    df["PB at Swim"] = PBs
    df["final_flag"] = finals
    
    # Competition flags: Swimmers focus on the Olympics and World Championships the most
    def competition(s):
        # Get date and city from corresponding columns
        date = datetime.strptime(str(s["Date"]), "%Y-%m-%d %H:%M:%S")
        city = s['Location']
        # Olympics 
        if (date > datetime(2021, 7, 23)
            and date < datetime(2021, 8, 8)
            and "Tokyo" in city) or (date > datetime(2016, 8, 5) 
            and date < datetime(2016, 8, 21) 
            and "Rio" in city) or (date > datetime(2012, 7, 27) 
            and date < datetime(2012, 8, 12) 
            and "London" in city):
            return "O"
        # Wold Championships
        elif (date > datetime(2019, 7, 21) 
            and date < datetime(2019, 7, 28) 
            and "Gwangju" in city) or (date > datetime(2017, 7, 14)  
            and date < datetime(2017, 7, 23)
            and "Budapest" in city) or (date > datetime(2015, 7, 24)
            and date < datetime(2015, 8, 9) 
            and "Kazan" in city) or (date > datetime(2013, 7, 20) 
            and date < datetime(2013, 8, 4) 
            and "Barcelona" in city):
            return "W"
        else:
            return "N"
    
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

    # Remove semi finals and heats swim at the Olympics
    df = df[~((df[["Event", "Name", "Location"]].duplicated(keep='last')) & 
            (df["Date"]>"2021-07-24 00:00:00"))]
    
    df.drop(['Time', 'DOB', 'FINA Points', 'Club', 'Location'], axis=1, inplace=True)
    
    df.to_csv(OUTPUTFILE)
    
    return df
 

df = preprocess(INPUTFILE, OUTPUTFILE)
