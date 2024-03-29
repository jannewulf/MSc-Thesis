#! /usr/bin/python3

import os
import sys
import matplotlib
from matplotlib import patches

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from numpy.core.records import array
import pandas as pd

OUTLIER_THRESHOLD = 0.05
OUT_DIR = sys.argv[2]
input_file = sys.argv[1]
GREEN = '#00715E'
BLUE = '#005AA9'
COLOR = BLUE if 'aurora' in input_file else GREEN

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

def draw_variance_measure(axis, x, y):
    ymin = min(y)
    ymax = max(y)
    has_variation = ymax > ymin and ymin > 0
    arrow = patches.FancyArrowPatch(
            (x, ymin), 
            (x, ymax), 
            arrowstyle=patches.ArrowStyle.BarAB(widthA=4, angleA=None, widthB=4, angleB=None),
            shrinkA=0,
            shrinkB=0
        )
    axis.add_patch(arrow)
    percentage = (ymax / ymin - 1) * 100 if has_variation else 0
    axis.annotate(f'+{percentage:.1f}%', (x + .2, (ymin + (ymax - ymin) / 2)), verticalalignment='center')

def generate_barplot(df, width=0.35):
    benchmark = df[['benchmark', 'function', 'basicblock']].iloc[0]
    if benchmark.isnull().values.any():
        return
    print(benchmark)
        
    outlier = find_outliers_between_runs(df)
    df_valid, df_outlier = df[~df['seed'].isin(outlier)], df[df['seed'].isin(outlier)]
    
    x = np.arange(len(df) / 2)
    x_valid = x[:len(df_valid)//2]
    x_outlier = x[-len(df_outlier)//2:] + 1.7 if len(df_outlier) > 0 else []
    
    fig, ax = plt.subplots()
    if len(df_outlier) == 0:
        ax.bar([x_valid[-1] + 1.3], [0])

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
        ax.bar(x_valid - width/2 - 0.01, run1[:len(x_valid)], width, label='Run 1', color=COLOR)
        ax.bar(x_valid + width/2 + 0.01, run2[:len(x_valid)], width, label='Run 2', color=COLOR)
        draw_variance_measure(ax, x_valid[-1] + .65, run1[:len(x_valid)] + run2[:len(x_valid)])
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
