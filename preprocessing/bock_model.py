#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 13:11:31 2026

@author: anmavrol
"""

#install tempocnn
import os
import pandas as pd
from madmom.audio.signal import Signal
from madmom.features.beats import RNNBeatProcessor
from madmom.features.tempo import TempoEstimationProcessor

dir_name = 'data/spotify_previews'
dir_folders = os.listdir(path=dir_name)

counter = 0
pathExists = os.path.exists('data/features/bock_completed_folders.csv')
if pathExists:
   completed_folders = pd.read_csv('data/features/bock_completed_folders.csv')['folder'].tolist()
   existing_data = pd.read_csv('data/features/bock_model.csv') 
else:
    existing_data = pd.DataFrame(columns=['Track', 'tempo','clarity'])
    completed_folders = []
new_folders=list(set(dir_folders).difference(set(completed_folders)))        

for folder in new_folders:
    tempi = []
    clarity = []
    track_filenames = os.listdir(os.path.join(dir_name, folder))
    track_filenames = [f for f in track_filenames if f.endswith('.mp3')]
    print(len(track_filenames))
    for track in track_filenames:
        # load audio
        signal = Signal(track)
        # compute beat activation function (RNN)
        act = RNNBeatProcessor()(signal)
        # estimate tempo (comb filter)
        bock_tempo = TempoEstimationProcessor(fps=100)(act)
        print(f"Estimated global tempo: {bock_tempo[0][0]}")
        tempi.append(bock_tempo[0][0])
        clarity.append(bock_tempo[0][1])
    completed_folders.append(folder)
    temp = {'Track':track_filenames,'tempo':tempi,'clarity':clarity}
    temp_df = pd.DataFrame(temp)
    existing_data = pd.concat([existing_data, temp_df], ignore_index=True)
    existing_data.to_csv('data/features/bock_model.csv', index=False)
    pd.DataFrame({'folder': completed_folders}).to_csv(
    'data/features/bock_completed_folders.csv',
    index=False)