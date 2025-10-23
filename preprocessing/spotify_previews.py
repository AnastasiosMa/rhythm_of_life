#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 23 22:45:16 2025

@author: anmavrol
"""

import requests
import base64
import os
import pandas as pd
import numpy as np
from IPython.core.debugger import Pdb
ipdb = Pdb()
import time
import csv
from io import StringIO

#%% Spotify authentication
with open('spotify_user_authentication.txt') as f:
    credentials = f.readlines()
_id = credentials[0][0:-1]
_secret = credentials[1][0:-1]
#artists = pd.read_excel('data/top_artists/Top_artists.xlsx').values.tolist()
#artists = list(itertools.chain.from_iterable(artists))
#%%
class Connection:
    """
    Class' object instantiates a connection with spotify. When the connection is alive, queries are made with the query_get
    method.
    """
    def __init__(self, client_id, secret):
        # First header and parameters needed to require an access token.
        param = {"grant_type": "client_credentials"}
        header = {"Authorization": "Basic {}".format(
            base64.b64encode("{}:{}".format(client_id, secret).encode("ascii")).decode("ascii")),
                  'Content-Type': 'application/x-www-form-urlencoded'}
        self.token = requests.post("https://accounts.spotify.com/api/token", param, headers=header).json()["access_token"]
        self.header = {"Authorization": "Bearer {}".format(self.token)}
        self.base_url = "https://api.spotify.com"

    def query_get(self, query, params=None):
        """
        
        :param query: (str) URL coming after example.com
        :param params: (dict)
        :return: (json) 
        """
        return requests.get(self.base_url + query, params, headers=self.header).json()
    
def find_spotify_id(track_name, artist_name):
    """
    If id is missing try to find through search
    """
    track_id=[]
    if isinstance(artist_name, (str)):
       query_track = dict(q = track_name + ' ' + artist_name, type = "track", limit = 50) 
    else:
       query_track = dict(q = track_name, type = "track", limit = 50)       
    search = conn.query_get('/v1/search/',query_track)
    for i in range(len(search['tracks']['items'])):
        artist = search['tracks']['items'][i]['artists'][0]['name']
        name = search['tracks']['items'][i]['name']
        if artist_name.lower()==artist.lower() and track_name.lower()==name.lower():
           track_id = search['tracks']['items'][i]['id'] 
           break
    return(track_id)

def download_track(track_id,save_loc,url):
    os.makedirs(save_loc, exist_ok=True)
    f = os.path.join(save_loc, "{}.mp3".format(track_id))
    if not os.path.isfile(f):
           r = requests.get(url)
           print("Saving {}.mp3".format(track_id))
           #print("ID: " + track_id)
           with open(f, "wb") as f:
                        f.write(r.content)
    else:
           print("file already exists:{}".format(track_id))
path = 'data/SpotifyMetadata/Spotify metadata/'
csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
if os.path.exists('data/completed_csvs.txt'):
   completed_csvs = pd.read_csv('data/completed_csvs.txt', header=None)[0].tolist()
   csv_files = [f for f in csv_files if f not in completed_csvs]
else:
   completed_csvs = [] 
#%%get preview
for csv_file in csv_files:
    rows = []
    with open(path+csv_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            # parse the single CSV record in 'line' as fields:
            reader = csv.reader(StringIO(line), delimiter=',', quotechar='"')
            parsed = next(reader)
            rows.append(parsed)
    data = pd.DataFrame(rows)
    data.columns = data.iloc[0,:]
    data=data.drop(index=0)
    conn = Connection(_id, _secret) 
    print(csv_file)
    save_loc = 'data/spotify_previews/'+csv_file[:-4]
    for i in data.index:
        if isinstance(data.loc[i,'Preview Url'], str):
           time.sleep(0.75) 
           try:
               download_track(data.loc[i,'id'],save_loc,data.loc[i,'Preview Url'])        
           except:
               print('Error in retrieving excerpts')
    completed_csvs.append(csv_file)
    with open('data/completed_csvs.txt','w') as f:
        for item in completed_csvs:
            f.write(item + "\n")

