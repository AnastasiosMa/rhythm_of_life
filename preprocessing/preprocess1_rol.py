#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 11:02:06 2024

@author: anmavrol
"""

#install tempocnn
import os
import pandas as pd
import sys

def main(dir_name,save_dir):
    dir_files = os.listdir(path=dir_name)       
    
    cols = pd.read_excel(dir_name+dir_files[0]).columns.values.tolist()
    cols.insert(0,'playlist')
    cols.insert(0,'file')
    data = pd.DataFrame(columns = cols)
    for folder in dir_files:
        xls = pd.ExcelFile(dir_name+folder)
        for sheet in xls.sheet_names:
            temp = pd.read_excel(xls, sheet_name=sheet)
            temp = temp[temp["name"].notna()]                 # remove NaN
            temp = temp[temp["name"].astype(str).str.strip() != ""]  # remove empty strings
            temp['file'] = folder
            temp['playlist'] = sheet
            print("Sheet:", sheet)
            data = pd.concat([data, temp], ignore_index=True)
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    data.to_excel(save_dir, index=False)

if __name__== '__main__':
    main(sys.argv[1], sys.argv[2])

    
