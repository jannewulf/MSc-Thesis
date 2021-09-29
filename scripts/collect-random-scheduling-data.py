#! /usr/bin/python3

import glob
import os
import sys

import pandas as pd

def read_measurement_file(path):
    print(path, file=sys.stderr)
    benchmark, func_bb, seed_run = path.split(os.sep)[-3:]
    data = {
        'benchmark': benchmark,
        'function': func_bb.split('-')[0],
        'basicblock': func_bb.split('-')[1],
        'seed': seed_run.split('.')[0].split('_')[0],
        'run': seed_run.split('.')[0].split('_')[1]
    }
    with open(path, 'r') as f:
        try:
            for line in f.readlines():
                line = line.rstrip()
                if 'Count:' in line:
                    data['count'] = int(line.split(':')[1])
                elif 'Min:' in line:
                    data['min'] = float(line.split(':')[1])
                elif 'Median:' in line:
                    data['median'] = float(line.split(':')[1])
                elif 'Mean:' in line:
                    data['mean'] = float(line.split(':')[1])
                elif 'Max:' in line:
                    data['max'] = float(line.split(':')[1])
                elif 'StdDev:' in line:
                    data['stddev'] = float(line.split('±')[1])
        except UnicodeDecodeError:
            print('UnicodeDecodeError', file=sys.stderr)
            return None
    return data


results_dir = sys.argv[1]

dataset = pd.DataFrame()
for f in glob.iglob(os.path.join(results_dir, '*', '*', '*.txt')):
    bb_data = read_measurement_file(f)
    if bb_data:
        dataset = dataset.append(bb_data, ignore_index=True)

print(dataset.to_csv())
