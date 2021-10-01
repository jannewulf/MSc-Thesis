#! /usr/bin/python3

import sys

import numpy as np
import pandas as pd

input_file = sys.argv[1]

coefficients_of_variation = [] 
df = pd.read_csv(input_file, index_col=0)
for benchmark, bench_df in df.groupby('benchmark'):
    coeff_var = bench_df['min'].std() / bench_df['min'].mean()
    if coeff_var == coeff_var:
        coefficients_of_variation.append(coeff_var)
    print(benchmark, coeff_var)

print('MEAN: ', np.array(coefficients_of_variation).mean())
