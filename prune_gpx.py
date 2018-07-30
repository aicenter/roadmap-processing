from roadmaptools.inout import load_gpx, save_gpx
from tqdm import tqdm
import os


# data = load_gpx('/home/martin/Stažené/traces-raw-old.gpx')
# save_gpx(data,'neexistujici slozka')

def file_len(fname):
    letters = 0
    with open(fname, 'r') as f:
        for line in f.readlines():
            letters += len(line)
    return letters


def cut_gpx(in_file, out_file):
    number_of_chars = file_len(in_file)
    print(number_of_chars)
    number_of_chars /= 2
    number_of_chars = int(number_of_chars)
    # number_of_lines = 300000000
    print(number_of_chars)
    result = ''
    with open(in_file, 'r') as fh:
        for line in fh.readlines():
            if len(result) < number_of_chars:
                result += line
            elif not line.startswith('      <trkpt'):
                # print(line.startswith('      <trkpt'))
                result += line
            else:
                break
            print(len(result))
    result += '\n</trkseg>\n</trk>\n</gpx>'

    with open(out_file, 'w') as ofh:
        ofh.write(result)


# data = load_gpx('/home/martin/Stažené/traces-raw.gpx')



# cut_gpx('/home/martin/Stažené/traces-raw.gpx','/home/martin/Stažené/traces-raw-mensi.gpx')

# def _read_all_csv_from_dir(directory: str):
#     traces_all = []
#
#     for filename in tqdm(os.listdir(directory), desc="Loading and parsing traces"):
#         if os.path.splitext(filename)[-1] == '.csv':
#             abs_filename = os.path.join(directory, filename)
#             traces_all.append(_load_traces_from_csv(abs_filename))
#     return traces_all

import pandas as pd
import numpy as np
import roadmaptools

ls = []
len_ids = set()
pd.set_option('display.max_columns', None)
column_names = ['id_record', 'id_car', 'status', 'lat', 'lon', 'time']
# data_types = [str,int,str,float,float,str]
arr = np.empty(shape=(len(os.listdir('/home/martin/MOBILITY/data/traces')),),dtype=object)
for idx,filename in tqdm(enumerate(os.listdir('/home/martin/MOBILITY/data/traces'))):
    abs_filename = os.path.join('/home/martin/MOBILITY/data/traces', filename)
    filename_parts = abs_filename.split(sep='.')
    file_extension = filename_parts[-2]
    df = pd.read_csv(abs_filename, header=None, names=column_names)
    df['id_car'] = pd.to_numeric(file_extension + df['id_car'].astype(str))
    # print(df.head())
    # print(df.dtypes)
    filtered = df[(df.iloc[:, 2] != "STREETPICKUP")].loc[:, ['id_car','lat', 'lon', 'time']].sort_values(by=['id_car','time'],ascending=True)
    # print(filtered)
    # ls.append(filtered)
    arr[idx] = filtered

df = pd.concat(arr,ignore_index=True)
# print(df)
sorted_df = df.sort_values(by=['id_car','time'],ascending=True)
# print(sorted_df)
# for idx, row in df.iterrows():
#     print(idx)

# iter_csv = pd.read_csv(abs_filename,iterator=True,chunksize=1000)
# df = pd.concat([chunk[chunk['field'] > constant] for chunk in iter_csv])
#     for row in df:
#         len_id = len(row[1])
#         if len_id not in len_ids:
#             len_ids.add(len_id)
#
# print(len_ids)

from numpy import genfromtxt
# my_data = genfromtxt('my_file.csv', delimiter=',')
for filename in tqdm((os.listdir('/home/martin/MOBILITY/data/traces'))):
    abs_filename = os.path.join('/home/martin/MOBILITY/data/traces', filename)
    filename_parts = abs_filename.split(sep='.')
    file_extension = filename_parts[-2]
    arr = genfromtxt(abs_filename,dtype=None)
    print(arr)
