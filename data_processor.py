#!/usr/bin/env python3
import os
import sys

# packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

LOG_DIR = 'logs'

class Metric:
    def __init__(self, ts):
        self.ts = ts
        self.cpu = None
        self.io = None
        self.mem = None
        self.net = None

    def create_dfs(self):
        cpu_log_path    = LOG_DIR + '/cpu_stats' + self.ts + '.csv'
        io_log_path     = LOG_DIR + '/io_stats' + self.ts + '.csv'
        mem_log_path    = LOG_DIR + '/mem_stats' + self.ts + '.csv'
        net_log_path    = LOG_DIR + '/net_stats' + self.ts + '.csv'
        self.io = pd.read_csv(cpu_log_path)
        self.cpu = pd.read_csv(io_log_path)
        self.mem = pd.read_csv(mem_log_path)
        self.net = pd.read_csv(net_log_path)

    def get_io_plt(self):
        #plt.title('Input/Output')
        #plt.xlabel('Time')
        #plt.ylabel('Bytes')

        # gca = get current axis
        ax=plt.gca()

        self.io.plot(kind='line', x='Time', y='Written(B)', ax=ax)
        self.io.plot(kind='line', x='Time', y='Read(B)', ax=ax)

        plt.legend()
        plt.show()

def get_unique_tss():
    metric_ident = ['mem', 'cpu', 'io', 'net']
    metric_ident += ['_stats', '.csv']

    logs = os.listdir('logs')
    for ident in metric_ident:
        logs = [x.replace(ident, '') for x in logs]

    return set(logs)

def create_metrics(tss):
    metrics = []
    for ts in tss:
        m = Metric(ts)
        m.create_dfs()
        metrics.append(m)
    return metrics

def main():
    metrics = create_metrics(get_unique_tss())
    for m in metrics:
        m.get_io_plt()

if __name__ == "__main__":
    main()
