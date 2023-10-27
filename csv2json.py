# -*- coding: utf-8 -*-

import csv
import json
import os

os.chdir('/떠나볼까/redSys/DATA_Files')

csv_files = ['clean_exhibit_df.csv', 'clean_festival_df.csv', 'clean_musical_df.csv']

json_files = ['exhibit.json', 'festival.json', 'musical.json']

for i in range(len(csv_files)):
    data = []

    with open(csv_files[i], 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            data.append(row)

    with open(json_files[i], 'w') as jsonfile:
        jsonfile.write(json.dumps(data, indent=4))
