#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 11:02:06 2024

@author: anmavrol
"""

#install tempocnn
import os
import pandas as pd
from tempocnn.classifier import TempoClassifier
from tempocnn.feature import read_features

model_name = 'cnn'
dir_name = 'spotify_previews'
classifier = TempoClassifier(model_name)
dir_folders = os.listdir(path=dir_name)

counter = 0
pathExists = os.path.exists('features/schr_completed_folders.csv')
if pathExists:
   completed_folders = pd.read_csv('features/schr_completed_folders.csv')['folder'].tolist()
   existing_data = pd.read_csv('features/schr_model.csv') 
else:
    existing_data = pd.DataFrame(columns=['Track', 'tempo'])
    completed_folders = []
new_folders=list(set(dir_folders).difference(set(completed_folders)))        

for folder in new_folders:
    tempi = []
    track_filenames = os.listdir(os.path.join(dir_name, folder))
    track_filenames = [f for f in track_filenames if f.endswith('.mp3')]
    print(len(track_filenames))
    for k in track_filenames:
        features = read_features(os.path.join(dir_name, folder, k))
        tempo = classifier.estimate_tempo(features, interpolate=False)
        print(f"Estimated global tempo: {tempo}")
        tempi.append(tempo)
    completed_folders.append(folder)
    temp = {'Track':track_filenames,'tempo':tempi}
    temp_df = pd.DataFrame(temp)
    existing_data = pd.concat([existing_data, temp_df], ignore_index=True)
    existing_data.to_csv('features/schr_model.csv', index=False)
    pd.DataFrame({'folder': completed_folders}).to_csv(
    'features/schr_completed_folders.csv',
    index=False)

    
