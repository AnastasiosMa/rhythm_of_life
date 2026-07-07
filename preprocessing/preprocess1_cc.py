#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 11:02:06 2024

@author: anmavrol
"""

import os
import sys
import pandas as pd


def main(dir_name, save_dir):
    dir_files = os.listdir(path=dir_name)

    # Get columns from first file
    cols = pd.read_excel(os.path.join(dir_name, dir_files[0])).columns.values.tolist()
    cols.insert(0, 'annotator')
    cols.insert(0, 'playlist')
    cols.insert(0, 'file')

    data = pd.DataFrame(columns=cols)

    for folder in dir_files:

        # Skip non-Excel files
        if not folder.endswith('.xlsx'):
            continue

        # Extract annotator name
        # Example:
        # tempo_ratings_round1_John.xlsx -> John
        annotator = os.path.splitext(folder)[0].rsplit('_', 1)[-1]

        file_path = os.path.join(dir_name, folder)

        xls = pd.ExcelFile(file_path)

        for sheet in xls.sheet_names:
            temp = pd.read_excel(xls, sheet_name=sheet)

            # Remove empty tracks
            temp = temp[temp["name"].notna()]
            temp = temp[temp["name"].astype(str).str.strip() != ""]

            temp['file'] = folder
            temp['playlist'] = sheet
            temp['annotator'] = annotator

            print(
                f"File: {folder} | Annotator: {annotator} | Sheet: {sheet}"
            )

            data = pd.concat([data, temp], ignore_index=True)

    # Remove unnamed columns from Excel
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]

    # Save merged file
    data.to_excel(save_dir, index=False)

    print(f"Saved {len(data)} rows to {save_dir}")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

    
