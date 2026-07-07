#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 22:57:13 2026

@author: anmavrol
"""

import pandas as pd
import re
import numpy as np

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

def compute_tempo_accuracy(gt, pred):
    gt = pd.to_numeric(gt, errors='coerce')
    pred = pd.to_numeric(pred, errors='coerce')

    # avoid division issues
    mask = gt > 0
    rel_err = np.abs(gt - pred) / gt
    acc0 = (rel_err <= 0.02) & mask
    acc1 = (rel_err <= 0.04) & mask

    # octave-aware errors
    rel_err_half = np.abs(gt - pred / 2) / gt
    rel_err_double = np.abs(gt - pred * 2) / gt

    acc2 = (
        (rel_err <= 0.04) |
        (rel_err_half <= 0.04) |
        (rel_err_double <= 0.04)
    ) & mask

    return pd.DataFrame({
        'Acc0': acc0.astype(int),
        'Acc1': acc1.astype(int),
        'Acc2': acc2.astype(int)
    })

result = compute_tempo_accuracy(
    data['Tempo'],
    data['TempoCNN'])

data = pd.concat([data, result], axis=1)

