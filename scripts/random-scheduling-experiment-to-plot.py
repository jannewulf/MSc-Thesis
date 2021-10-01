#! /usr/bin/python3

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUTLIER_THRESHOLD = 0.05
OUT_DIR = sys.argv[2]
input_file = sys.argv[1]

def find_outliers_between_runs(bench_df):
    outlier = []
    # for benchmark, bench_df in df.groupby('benchmark'):
    for seed, seed_df in bench_df.groupby('seed'):
        max_runtime = seed_df['min'].max()
        min_runtime = seed_df['min'].min()
        mean_runtime = seed_df['min'].mean()
        difference_between_runs = (max_runtime - min_runtime) / mean_runtime

        if difference_between_runs > OUTLIER_THRESHOLD:
            outlier.append(seed)
    return outlier

def generate_barplot(df, width=0.35):
    benchmark = df[['benchmark', 'function', 'basicblock']].iloc[0]
    if benchmark.isnull().values.any():
        return
    print(benchmark)
        
    outlier = find_outliers_between_runs(df)
    df_valid, df_outlier = df[~df['seed'].isin(outlier)], df[df['seed'].isin(outlier)]
    
    x = np.arange(len(df) / 2)
    x_valid = x[:len(df_valid)//2]
    x_outlier = x[-len(df_outlier)//2:] + 0.5 if len(df_outlier) > 0 else []
    fig, ax = plt.subplots()

    run1, run2, seed_labels = [], [], []
    for seed, seed_df in sorted(df_valid.groupby('seed'), key=lambda x: x[1]['min'].mean()):
        runtime1 = float(seed_df[seed_df['run'] == 1]['min'])
        runtime2 = float(seed_df[seed_df['run'] == 2]['min'])
        run1.append(runtime1)
        run2.append(runtime2)
        seed_labels.append(seed)
    for seed, seed_df in sorted(df_outlier.groupby('seed'), key=lambda x: x[1]['min'].mean()):
        runtime1 = float(seed_df[seed_df['run'] == 1]['min'])
        runtime2 = float(seed_df[seed_df['run'] == 2]['min'])
        run1.append(runtime1)
        run2.append(runtime2)
        seed_labels.append(seed)
    
    if (len(df_valid) > 0):
        ax.bar(x_valid - width/2 - 0.01, run1[:len(x_valid)], width, label='Run 1', color='#00715E')
        ax.bar(x_valid + width/2 + 0.01, run2[:len(x_valid)], width, label='Run 2', color='#00715E')
    if (len(df_outlier) > 0):
        ax.bar(x_outlier - width/2 - 0.01, run1[-len(x_outlier):], width, label='Run 1', color='gray')
        ax.bar(x_outlier + width/2 + 0.01, run2[-len(x_outlier):], width, label='Run 2', color='gray')

    ax.set_ylabel('Runtime [Cycles]')
    ax.set_xlabel('Seed')
    ax.set_title('Random Scheduling Experiment\n' + ' '.join(benchmark))
    ax.set_xticks(np.concatenate([x_valid, x_outlier]))
    ax.set_xticklabels(seed_labels)

    fig.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, df['benchmark'].iloc[0]) + '.pdf')
    plt.close(fig)

df = pd.read_csv(input_file, index_col=0)
for benchmark, bench_df in df.groupby('benchmark'):
    generate_barplot(bench_df)
