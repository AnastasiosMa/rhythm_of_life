#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 17:28:06 2024

@author: anmavrol
"""

import os
from pydub import AudioSegment
#AudioSegment.converter = "Users/anmavrol/Documents/projects/github/tempo_estimation/ffmpeg"
#AudioSegment.ffmpeg = "Users/anmavrol/Documents/projects/github/tempo_estimation/ffmpeg"
#AudioSegment.ffprobe ="Users/anmavrol/Documents/projects/github/tempo_estimation/ffmpeg"

dir_input = 'mp3_tracks'
dir_output = 'wav_tracks'

track_names = os.listdir(dir_input)

# convert mp3 to wav
for name in track_names:
    try:
        sound = AudioSegment.from_file(dir_input + '/' + name,format="mp3")
        sound.export(dir_output + '/' + name, format="wav")
    except:
        print(name)
