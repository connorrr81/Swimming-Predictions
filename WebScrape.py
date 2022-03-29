# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 21:10:34 2021

@author: CLaug
"""


from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import numpy as np
import re
import os
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
path = os.path.dirname(os.path.realpath(__file__))
OUTPUTPATH = path + "\\times.csv"

#%% Initialise BeautifulSoup on Olympic Events Page

url = "https://www.swimrankings.net/index.php?page=athleteSelect&nationId=0&selectPage=TOP100_MEN"
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")


#%% Define the event df
event_df = pd.DataFrame(columns=["ID"],
                        index=["50m Freestyle", "100m Freestyle", "200m Freestyle", "400m Freestyle", "800m Freestyle", "1500m Freestyle",
                               "100m Backstroke", "200m Backstroke",
                               "100m Breaststroke", "200m Breaststroke",
                               "100m Butterfly", "200m Butterfly",
                               "200m Medley", "400m Medley"],
                        data = {"ID": [1,2,3,5,6,8,10,11,13,14,16,17,18,19]})
                       #data = {"ID": [1,2,3,5,6,8,10,11,13,14,16,17,18,19]})

#%% Get the links of the Top 100 page
links = soup.find_all('a')

baseurl = "https://www.swimrankings.net/index.php"

for link in links[-1:]:
    address = baseurl + link.get('href')
    
    # Swimmers best times
    tables = pd.read_html(address)
    df = tables[3]
    
    # Obtain the swimmers best events
    # Consider long course only for olynpic prediction
    df = df[df["Course"]=="50m"]
    df = df[df["Pts."]!="-"]
    df["Pts."] = df["Pts."].apply(pd.to_numeric)
    # Define elite performance of more than 900 FINA points, this 
    best_performances = df[df["Pts."]>900]
    best_events = best_performances["Event"].values
    
    for events in best_events:
        if events in ["50m Backstroke", "50m Breaststroke", "50m Butterfly"]:
            continue
        event_ID = event_df['ID'][events]
        event_history_page = address + "&styleId=" + str(event_ID)
        print(event_history_page)
        
        historic_tables = pd.read_html(event_history_page)
        historic_df = historic_tables[3]
        print(historic_df.head())
        
#%% Get links to athlete profile for all olympic finals

# for all athletes...
baseurl = "https://www.swimrankings.net/index.php"

# For olympic finalists...
baseurl_men = "https://www.swimrankings.net/index.php?page=meetDetail&meetId=626385&gender=1&styleId="
baseurl_women = "https://www.swimrankings.net/index.php?page=meetDetail&meetId=626385&gender=2&styleId="

# Define an empty df to store the athletes top times
times_df = pd.DataFrame(columns=["Long Course (50m)", "Long Course (50m).1",
                                 "Long Course (50m).2",  "Long Course (50m).3",
                                 "Name", "DOB", "Nation", "Club"])

for event in event_df["ID"]:
    address = baseurl_men + str(event)
    
    # Set up BeautifulSoup to find the links
    page = urlopen(address)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    # Get all links from page
    links = soup.find_all('a')
    
    # Obtain the links for the athletes within the page, for some events (the straight to final) there is an extra hyperlink t0 avoid
    if event in [1,2,3,10,11,13,14,16,17,18]:
        links = links[35:57:3]
    else: links = links[34:57:3]
    
    for link in links:
        # Build the url to the athletes profile
        athlete_page = baseurl + link.get('href')
        
        # Select the page containing the event they finaled in
        event_history_page = athlete_page + "&styleId=" + str(event) 
        
        # Get the table with information of their historical swims in that event
        historic_tables = pd.read_html(event_history_page)
        historic_df = historic_tables[3]
        
        name, DOB, nation, club = get_swimmer_info(athlete_page)
        
        # Insert their details
        historic_df["Name"] = name
        historic_df["DOB"] = DOB
        historic_df["Nation"] = nation
        historic_df["Club"] = club
        historic_df["Event"] = event_df[event_df["ID"]==event].index.values[0]
        
        times_df = times_df.append(historic_df)
        
        print(name)
        
        time.sleep(5)

#times_df.to_csv(OUTPUTPATH) 
    
#%%
def get_swimmer_info(url):
    
    # Initiate web scraper
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    name_and_DOB = soup.find(id='name').get_text()
    nation_and_club = soup.find(id='nationclub').get_text()
    
    athlete_name, DOB = name_and_DOB.split("(")
    DOB = DOB[:4]
    
    try:
        string_pos = re.search('[a-z][A-Z]', nation_and_club).start()
        nation, club = nation_and_club[:string_pos+1], nation_and_club[string_pos+1:]
    except AttributeError:
        nation = nation_and_club
        club = np.nan
    
    return athlete_name, DOB, nation, club        
        