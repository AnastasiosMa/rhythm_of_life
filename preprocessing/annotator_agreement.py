#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 00:28:47 2026

@author: anmavrol
"""

import pandas as pd
import numpy as np

#%% CCdata
dir_files = 'data/preprocessed2/'
data_dir = 'ccsWorkingFiles.xlsx'
review_dir = 'ccsReviewedFiles.xlsx'

cc_data = pd.read_excel(dir_files + data_dir)
print('N: {}'.format(len(cc_data)))
cc_data = cc_data.dropna(subset=['Tempo'])
cc_data = cc_data[cc_data['Unclear tempo']==0]
print('Unclear N: {}'.format(len(cc_data)))
# rows where tempo is a string
cc_data = cc_data[~cc_data['Tempo'].apply(lambda x: isinstance(x, str))]
cc_data = cc_data[cc_data['Tempo']!=0]
cc_data = cc_data[cc_data['Tempo']>30]
data = cc_data[~cc_data['Local Tempo Change']==1]
print('Localised tempo tracks N: {}'.format(len(cc_data)))

cc_data['trackCode'] = cc_data['name'].astype(str) + cc_data['artist-1'].astype(str)

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
        'Tempo_agg': tempo_agg})  

result = cc_data.groupby('trackCode').apply(compute_agreements).reset_index()

print('Acc0:{}'.format(round(result['Acc0'].sum()/len(result),3)))
print('Acc1:{}'.format(round(result['Acc1'].sum()/len(result),3)))
print('Acc2:{}'.format(round(result['Acc2'].sum()/len(result),3)))
print('Mean agreement Acc0:{}'.format(round((result['Acc0_agg']/result['N_raters']).mean(),3)))
print('Mean agreement Acc1:{}'.format(round((result['Acc1_agg']/result['N_raters']).mean(),3)))
print('Mean agreement Acc2:{}'.format(round((result['Acc2_agg']/result['N_raters']).mean(),3)))
