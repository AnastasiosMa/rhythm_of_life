#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 22:57:13 2026

@author: anmavrol
"""

import pandas as pd
import re
import numpy as np

data_dir = 'ccsWorkingFiles.xlsx'
features_dir = 'data/ccsFeatures/'
    
data = pd.read_excel('data/preprocessed3/'+data_dir)

data = data.dropna(subset=['trackID'])
print('Missing N: {}'.format(len(data)))

mirtoolbox = pd.read_csv(features_dir+'mirtempo.csv').drop_duplicates(subset='Track')
tempocnn = pd.read_csv(features_dir+'schr_model.csv').drop_duplicates(subset='name')
librosa = pd.read_csv(features_dir+'librosa_model.csv').drop_duplicates(subset='Track')

#remove .mp3
mirtoolbox['Track'] = (mirtoolbox['Track']
    .str.replace(r'.mp3', '', regex=True, flags=re.IGNORECASE))
tempocnn['name'] = (tempocnn['name']
    .str.replace(r'.mp4', '', regex=True, flags=re.IGNORECASE))
librosa['Track'] = (librosa['Track']
    .str.replace(r'.mp3', '', regex=True, flags=re.IGNORECASE))

data = data.rename(columns={'tempo': 'Spotify'})

data['MIRToolbox'] = data['trackID'].map(
    mirtoolbox.set_index('Track')['mirtempo'])
print('MIRToolbox missing:{}'.format(sum(data['MIRToolbox'].isna())))
data['Librosa'] = data['trackID'].map(
    librosa.set_index('Track')['tempo'])
print('Librosa missing:{}'.format(sum(data['Librosa'].isna())))
data['TempoCNN'] = data['playlistCode'].map(
    tempocnn.set_index('name')['tempo'])
print('TempoCNN missing:{}'.format(sum(data['TempoCNN'].isna())))

def compute_tempo_accuracy(gt, pred):
    gt = pd.to_numeric(gt, errors='coerce')
    pred = pd.to_numeric(pred, errors='coerce')

    # avoid division issues
    mask = gt > 0
    rel_err = np.abs(gt - pred) / gt
    acc0 = (gt.round() == pred.round()) & mask
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

tempo_cols = ['Spotify','MIRToolbox','Librosa', 'TempoCNN']

gt_col = 'Tempo'

summary = []

for col in tempo_cols:
    valid = data[[gt_col, col]].dropna()
    metrics = compute_tempo_accuracy(
        valid[gt_col],
        valid[col])

    summary.append({
        'Algorithm': col,
        'Acc0': metrics['Acc0'].mean()*100,
        'Acc1': metrics['Acc1'].mean()*100,
        'Acc2': metrics['Acc2'].mean()*100,
        'N': metrics['Acc0'].notna().sum()})

summary = pd.DataFrame(summary)

summary = summary.sort_values(
    by=['Acc2', 'Acc1'],
    ascending=False)

summary = summary.round(2)
print(summary)

summary.to_excel('paper2/ccs_res.xlsx',index=False)
data.to_excel('paper2/ccs_preprocessed_data.xlsx',index=False)