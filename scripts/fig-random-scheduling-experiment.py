import os
import sys

import click
import matplotlib.pyplot as plt
import numpy as np
import plot_utils as pu


@click.command()
@click.argument('benchmarks', default='data/random-scheduling-experiment', type=click.Path(exists=True))
@click.option('-v', '--value', default='min')
@click.option('-s', '--save', default=None, type=click.Path())
def main(benchmarks, value, save):
    benchmarks_dirs = os.listdir(benchmarks)
    for b in benchmarks_dirs:
        plot_benchmark(os.path.join(benchmarks, b), value, save)


def plot_benchmark(benchmark, value_name, save):
    function = None
    basic_block = None
    count = None
    seed_to_values = {}

    files = os.listdir(benchmark)
    for f in files:
        seed = int(f.split('.')[0].split('_')[1])
        run = int(f.split('.')[0].split('_')[2])
        if not seed in seed_to_values.keys():
            seed_to_values[seed] = {}
        with open(os.path.join(benchmark, f), 'r') as stats_file:
            function, basic_block = stats_file.readline().strip().split('-')
            for line in stats_file.readlines():
                line = line.strip().lower()
                if line.startswith('count:'):
                    count = int(line.split(':')[-1].strip())
                if line.startswith(value_name.lower()):
                    seed_to_values[seed][run] = float(line.split(':')[-1].strip())
                    break

    x = np.array(sorted(seed_to_values.keys()))
    try:
        times_run1 = np.array([seed_to_values[k][1] for k in x])
        times_run2 = np.array([seed_to_values[k][2] for k in x])
    except KeyError:
        return
    #normalize_by = times_run1[0]
    #times_run1 /= normalize_by
    #times_run2 /= normalize_by

    pu.figure_setup()

    fig_size = pu.get_fig_size(15)
    fig = plt.figure(figsize=fig_size)
    ax = fig.add_subplot(111)

    bar_width = 0.35
    ax.bar(x - bar_width / 2, times_run1, bar_width, color=pu.primary_color(), label='Run 1')
    ax.bar(x + bar_width / 2, times_run2, bar_width, color=pu.secondary_color(), label='Run 2')

    benchmark_name = os.path.basename(benchmark)
    title = f'{benchmark_name}\nFunction: {function} - Basic Block: {basic_block}\n{value_name} of {count} Excutions'
    title = title.replace('_', '\_')
    ax.set_title(title)
    ax.set_xlabel('Seed')
    ax.set_xticks(x)
    ax.set_ylabel('Runtime [CPU Ticks]')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.legend(loc='lower right')

    plt.tight_layout()

    if save:
        pu.save_fig(fig, os.path.join(save, benchmark_name), 'eps')
    else:
        plt.show()


if __name__ == '__main__':
    main()