#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 22:57:13 2026

@author: anmavrol
"""

import pandas as pd
import re

data_dir = 'workingFiles.xlsx'

data = pd.read_excel('data/preprocessed3/'+data_dir)
spotify = pd.read_csv('data/features/spotify_model.csv').drop_duplicates(subset='Track')
bock = pd.read_csv('data/features/bock_model.csv').drop_duplicates(subset='Track')
mirtoolbox = pd.read_csv('data/features/mirtempo.csv').drop_duplicates(subset='Track')
tempocnn = pd.read_csv('data/features/schr_model.csv').drop_duplicates(subset='Track')
librossa = pd.read_csv('data/features/librosa_model.csv').drop_duplicates(subset='Track')

#remove .mp3
mirtoolbox['Track'] = (mirtoolbox['Track']
    .str.replace(r'.mp3', '', regex=True, flags=re.IGNORECASE))
bock['Track'] = (bock['Track']
    .str.replace(r'.mp3', '', regex=True, flags=re.IGNORECASE))
tempocnn['Track'] = (tempocnn['Track']
    .str.replace(r'.mp3', '', regex=True, flags=re.IGNORECASE))
librossa['Track'] = (librossa['Track']
    .str.replace(r'.mp3', '', regex=True, flags=re.IGNORECASE))

data['Spotify'] = data['preview'].map(
    spotify.set_index('Track')['tempo'])
print('Spotify missing:{}'.format(sum(data['Spotify'].isna())))
data['MIRToolbox'] = data['preview'].map(
    mirtoolbox.set_index('Track')['mirtempo'])
print('MIRToolbox missing:{}'.format(sum(data['MIRToolbox'].isna())))
data['Librossa'] = data['preview'].map(
    librossa.set_index('Track')['tempo'])
print('Librossa missing:{}'.format(sum(data['Librossa'].isna())))
data['Bock'] = data['preview'].map(
    bock.set_index('Track')['tempo'])
print('Bock missing:{}'.format(sum(data['Bock'].isna())))
data['TempoCNN'] = data['preview'].map(
    tempocnn.set_index('Track')['tempo'])
print('TempoCNN missing:{}'.format(sum(data['TempoCNN'].isna())))
