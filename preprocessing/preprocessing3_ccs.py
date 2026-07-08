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
import html
from ftfy import fix_text


dir_files = 'data/preprocessed2/'
data_dir = 'ccsWorkingFilesNames.xlsx'

data = pd.read_excel(dir_files+data_dir)

MOJIBAKE_MARKERS = [
    "Ã", "Å", "Ð", "Ñ", "Â", "â",
    "æ", "ç", "è", "ê", "ï",
    "¤", "€", "™"]

def mojibake_score(text):
    return sum(text.count(ch) for ch in MOJIBAKE_MARKERS)

def try_redecode(text, encoding):
    try:
        return text.encode(encoding).decode("utf-8")
    except Exception:
        return text


def fix_mojibake(text):
    if pd.isna(text):
        return text

    text = str(text)

    # HTML entities
    text = html.unescape(text)

    # First let ftfy do its magic
    text = fix_text(text)

    candidates = {text}

    current = text

    # Try several rounds of recovery
    for _ in range(3):

        latin1 = try_redecode(current, "latin1")
        cp1252 = try_redecode(current, "cp1252")

        candidates.add(latin1)
        candidates.add(cp1252)

        current = min(
            [current, latin1, cp1252],
            key=mojibake_score
        )

    best = min(candidates, key=mojibake_score)

    return best


def fix_column(df, column_name):
    df[column_name] = df[column_name].apply(fix_mojibake)
    return df

# Fix one column
data = fix_column(data, "name")
data = fix_column(data, "artist-1")

data['playlistCode'] = data['name']+'-'+data['artist-1']

#%% Preprocess CCS dataset 
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
data = data[~(data['Local Tempo Change']==1)]
print('Localised tempo tracks N: {}'.format(len(data)))
#data = data[~data['annotator'].isin(['Lotta', 'Sofia'])]
print('Final N: {}'.format(len(data)))
#%% match with spotify data
spotify_dir_name = 'data/ccsSpotifyData/Spotify_features.xlsx'
spotify_data = pd.read_excel('data/ccsSpotifyData/Spotify_features.xlsx')
spotify_data['playlistCode'] = spotify_data['trackName']+'-'+spotify_data['artistName']

data = data.merge(
    spotify_data[['playlistCode', 'trackID','tempo']],  
    on='playlistCode',
    how='left')

mismatch_mask = data[data['trackID'].isna()]
print('N mismatches:{}'.format(len(mismatch_mask)))
#%% tempo agreement
def compute_agreements(group):
    tempos = group['Tempo'].values
    n = len(tempos)
    acc0_counts = []
    acc1_counts = []
    acc2_counts = []

    for i in range(n):
        t = tempos[i]

        rel_err = np.abs(tempos - t) / t
        rel_err_half = np.abs(tempos - t/2) / t
        rel_err_double = np.abs(tempos - t*2) / t

        acc0_counts.append(np.sum(rel_err <= 0.02))
        acc1_counts.append(np.sum(rel_err <= 0.04))
        acc2_counts.append(
            np.sum(
                (rel_err <= 0.04) |
                (rel_err_half <= 0.04) |
                (rel_err_double <= 0.04)))

    # Aggregate = maximum agreement cluster size
    acc0_agg = max(acc0_counts)
    acc1_agg = max(acc1_counts)
    acc2_agg = max(acc2_counts)
    #number of ratings
    n_ratings = n
    #majority flags
    acc0 = acc0_agg > 0.5 * n_ratings
    acc1 = acc1_agg > 0.5 * n_ratings
    acc2 = acc2_agg > 0.5 * n_ratings
    #Tempo aggregation (only if Acc0 true)
    tempo_agg = np.nan
    if acc0:
        # most frequent value
        values, counts = np.unique(tempos, return_counts=True)
        max_count = counts.max()
        top_vals = values[counts == max_count]
        if len(top_vals) == 1:
            tempo_agg = top_vals[0]
        else:
            tempo_agg = round(tempos.mean())

    return pd.Series({
        'N_raters': n_ratings,
        'Acc0_agg': acc0_agg,
        'Acc1_agg': acc1_agg,
        'Acc2_agg': acc2_agg,
        'Acc0': acc0,
        'Acc1': acc1,
        'Acc2': acc2,
        'Tempo': tempo_agg})  

result = data.groupby('playlistCode').apply(compute_agreements).reset_index()

print('Acc0:{}'.format(round(result['Acc0'].sum()/len(result),3)))
print('Acc1:{}'.format(round(result['Acc1'].sum()/len(result),3)))
print('Acc2:{}'.format(round(result['Acc2'].sum()/len(result),3)))
print('Mean agreement Acc0:{}'.format(round((result['Acc0_agg']/result['N_raters']).mean(),3)))
print('Mean agreement Acc1:{}'.format(round((result['Acc1_agg']/result['N_raters']).mean(),3)))
print('Mean agreement Acc2:{}'.format(round((result['Acc2_agg']/result['N_raters']).mean(),3)))

result = result.merge(
    data[['playlistCode', 'trackID','tempo']],  
    on='playlistCode',
    how='left')

result.to_excel('data/preprocessed3/'+'ccsWorkingFiles.xlsx', index=False)
