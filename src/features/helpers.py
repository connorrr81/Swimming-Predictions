# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 22:27:40 2022

@author: CLaug
"""
# Import packages
from datetime import timedelta
from datetime import datetime

# Convert time to seconds 
def to_seconds(s):
    if ":" in s:
        mins, secs = map(float, s.split(":"))
        td = timedelta(minutes=mins, seconds=secs)
        return td.total_seconds()
    else: return s
    
    
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