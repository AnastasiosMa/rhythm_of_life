#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 15:50:30 2026

@author: anmavrol
"""

import pandas as pd
import numpy as np
import re
import os
import csv
from io import StringIO
import unicodedata


dir_files = 'data/preprocessed2/'
data_dir = 'workingFiles.xlsx'
review_dir = 'reviewedFiles.xlsx'

data = pd.read_excel(dir_files+data_dir)

#datafile with artist name and region
reg = pd.read_excel('data/Artist_Age_and_Region.xlsx')

#added tappers
tap = pd.read_excel('data/Tapping Data/WorkingFiles_Tapper_Seat_Session/WorkingFiles_With_Tapper_Seat_and_Session_Data.xlsx')

tap['trackIdx'] = tap['playlist']+tap['index'].astype(str)
data['trackIdx'] = data['playlist']+data['index'].astype(str)

data = data.merge(
    tap[['trackIdx', 'Tapper']],  # choose columns you want
    on='trackIdx',
    how='left'
)

data['artist'] = (
    data['playlist']
    .str.replace(r'_Metadata.*$', '', regex=True, flags=re.IGNORECASE)
    .str.replace(r'-\d+', '', regex=True)
    .str.replace('-', ' ')
    .str.strip())

replacements = {
    'a ha': 'a-ha',
    'Ladysmith Black Mambazo_Metad': 'Ladysmith Black Mambazo',
    'Ladysmith Black Mambazo_Metadat': 'Ladysmith Black Mambazo',
    'D.D.E': 'D.D.E.',
    'H.O.T': 'H.O.T.',
}

data['artist'] = data['artist'].replace(replacements)

#add country
data['artistCountry'] = data['artist'].map(
    reg.set_index('Artist')['Country / Region'])

#check for mismatchs
mismatch_mask = data[data['artistCountry'].isna()]
print('N mismatches:{}'.format(len(mismatch_mask)))
#%% Match spotify id with annotations
data['playlistCode'] = (
    data['playlist']
    .str.replace(r'_Metadata.*$', '', regex=True, flags=re.IGNORECASE)
    #.str.replace(r'-\d+', '', regex=True)
    .str.replace(r'[-_./,]', '')
    .str.replace(r'Metadat', '', regex=True, flags=re.IGNORECASE)
    .str.replace(r'Metad', '', regex=True, flags=re.IGNORECASE)
    .str.strip())

data['playlistCode'] = data['playlistCode'].replace(replacements)
data['playlistCode'] = data['playlistCode']+'_'+data['index'].astype(str)

spotify_dir_name = 'data/SpotifyMetadata/Spotify metadata/'
spotify_filenames = os.listdir(spotify_dir_name)
spotify_filenames = [f for f in spotify_filenames if f.endswith('.csv')]

def last_string_index(row):
    for i in range(len(row) - 1, -1, -1):  # loop backwards
        if isinstance(row[i], str) and row[i].strip() != "":
            return i
    return None

all_temp = []
for spotify_filename in spotify_filenames:
    print(spotify_filename)
        
    rows=[]
    preview_names = []
    idx = []
    with open(spotify_dir_name+spotify_filename, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            # parse the single CSV record in 'line' as fields:
            reader = csv.reader(StringIO(line), delimiter=',', quotechar='"')
            parsed = next(reader)
            rows.append(parsed)
    spotify_data = pd.DataFrame(rows)
    spotify_data.columns = spotify_data.iloc[0,:]
    spotify_data=spotify_data.drop(index=0)
    
    col_n = spotify_data.apply(last_string_index, axis=1).to_numpy()
    preview_idx = spotify_data.columns.get_loc("id")
    index_idx = spotify_data.columns.get_loc("index")        
    for i in range(len(col_n)):
        if col_n[i] == 55 or col_n[i] == 27 or col_n[i] == 28:
           preview_names.append(spotify_data.loc[i+1,'id'])
           idx.append(spotify_data.loc[i+1,'index'])
        else:
           preview_names.append(spotify_data.iloc[i,preview_idx+(col_n[i]-55)])
           idx.append(spotify_data.iloc[i,index_idx+(col_n[i]-55)])  
    temp = {
        'preview': preview_names,
        'index': idx}
    temp_df = pd.DataFrame(temp)
    #convert filename
    asd = re.sub(r'_Metadata\.csv$', '', spotify_filename)
    asd = re.sub(r'[-_./,]', '', asd)
    temp_df['playlistCode'] = asd +'_'+temp_df['index'].astype(str)
    all_temp.append(temp_df)
    

def normalize_text(x):
    if isinstance(x, str):
        return unicodedata.normalize('NFC', x)
    return x
    
combined_temp = pd.concat(all_temp, ignore_index=True)

data['playlistCode'] = data['playlistCode'].apply(normalize_text)
combined_temp['playlistCode'] = combined_temp['playlistCode'].apply(normalize_text)

data = data.merge(
    combined_temp[['playlistCode', 'preview']],  
    on='playlistCode',
    how='left')

mismatch_mask = data[data['preview'].isna()]
print('N mismatches:{}'.format(len(mismatch_mask)))
#%% Preprocess ROL dataset 
print('N: {}'.format(len(data)))
# rows where tempo is a string
data = data[~data['Tempo'].apply(lambda x: isinstance(x, str))]
print('String N: {}'.format(len(data)))
data = data.dropna(subset=['Tempo'])
print('Missing N: {}'.format(len(data)))
print('Number of Non-music tracks : {}'.format(sum(data['Skit / Non-music track']==1)))
data = data[~(data['Skit / Non-music track'] == 1)]
print('Non-music tracks N: {}'.format(len(data)))
data = data[data['Tempo']!=0]
data = data[data['Tempo']>30]
print('0-30 tempo N: {}'.format(len(data)))
Ntot = len(data)
data = data[data['Unclear tempo']==0]
print('Unclear N: {}'.format(len(data)))
Nunl = Ntot - len(data)
print('Number of Unclear tempi: {}'.format(Nunl))
print('Number of localise tempo tracks : {}'.format(sum(data['Local Tempo Change']==1)))
data = data[~data['Local Tempo Change']==1]
print('Localised tempo tracks N: {}'.format(len(data)))


review = pd.read_excel(dir_files+review_dir)
review = review[~review['Tempo'].apply(lambda x: isinstance(x, str))]
review = review[review['Tempo']!=0]
review = review[review['Tempo']>30]

data['trackCode'] = data['playlist']+data['index'].astype('Int64').astype('str')
review['trackCode'] = review['playlist']+review['index'].astype('Int64').astype('str')
data['TempoAgreement'] = None

for i,row in data.iterrows():
    matches = review.index[review['trackCode'] == row['trackCode']]
    if len(matches) == 1: 
        idx = matches[0]
        data.at[i,'TempoAgreement'] = abs(float(row['Tempo'])-float(review.loc[idx,'Tempo']))/float(row['Tempo'])
    elif len(matches)>1:
        print('More than one matches found', len(matches))

data['Acc0'] = None
data['Acc1'] = None
data['Acc2'] = None
data['Review'] = None


for i, row in data.iterrows():
    matches = review.index[review['trackCode'] == row['trackCode']]

    if len(matches) == 1:
        idx = matches[0]
        tempo_data = float(row['Tempo'])
        tempo_review = float(review.at[idx, 'Tempo'])
        # relative error
        rel_err = abs(tempo_data - tempo_review) / tempo_data

        # Acc0: ±2%
        acc0 = rel_err <= 0.02
        # Acc1: ±4%
        acc1 = rel_err <= 0.04
        # octave-aware checks (±4%)
        rel_err_half = abs(tempo_data - (tempo_review / 2)) / tempo_data
        rel_err_double = abs(tempo_data - (tempo_review * 2)) / tempo_data
        octave_ok = (rel_err_half <= 0.04) or (rel_err_double <= 0.04)
        # Acc2: same OR octave-aware agreement
        acc2 = acc1 or octave_ok
        # store results
        data.at[i, 'Acc0'] = acc0
        data.at[i, 'Acc1'] = acc1
        data.at[i, 'Acc2'] = acc2
        data.at[i, 'Review'] = tempo_review

    elif len(matches) > 1:
        print('More than one match found:', len(matches))
N_found_reviews = sum(data['TempoAgreement'].notna())
data['TempoAgreement'].hist(bins=50)
print('Acc0:{}'.format(round(data['Acc0'].sum()/N_found_reviews,3)))
print('Acc1:{}'.format(round(data['Acc1'].sum()/N_found_reviews,3)))
print('Acc2:{}'.format(round(data['Acc2'].sum()/N_found_reviews,3)))
print('Non-zero distances:{}'.format(sum(data['TempoAgreement']>0.001)))

print('Number of tracks with ACC0 disagreement : {}'.format(sum(data['Acc0']==0)))
data = data[~(data['Acc0'] == 0)]

print('Number of mising tracks:{}'.format(sum(data['preview'].isna())))
data = data[~data['preview'].isna()]
print('Final N: {}'.format(len(data)))

data.to_excel('data/preprocessed3/workingFilesAllRaters.xlsx', index=False)

data = data[~data['Tapper'].isin(['Lotta', 'Sofia'])]
print('Final N: {}'.format(len(data)))
data.to_excel('data/preprocessed3/'+data_dir, index=False)

