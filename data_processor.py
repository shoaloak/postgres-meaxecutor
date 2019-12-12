#!/usr/bin/env python3
import os
import sys

# packages
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
sns.set()

COLOR_LIST = list(mpl.colors._colors_full_map.values())
UNIQUE_COLORS = [
        '#000000', '#FF0000', '#00FF00', '#0000FF',
        '#FFFF00', '#FF00FF', '#4363d8', '#800000',
        '#808000', '#008000', '#008080', '#000080',
        '#800080', '#e6194b', '#3cb44b', '#ffe119']
FIG_DIR = 'figs'
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

        self.cpu = pd.read_csv(cpu_log_path)
        self.io = pd.read_csv(io_log_path)
        self.mem = pd.read_csv(mem_log_path)
        self.net = pd.read_csv(net_log_path)

        self.io['Time'] = pd.to_datetime(self.io['Time'])
        self.cpu['Time'] = pd.to_datetime(self.cpu['Time'])
        self.mem['Time'] = pd.to_datetime(self.mem['Time'])
        self.net['Time'] = pd.to_datetime(self.net['Time'])

    def get_io_plt(self):
        # get current axis
        ax = plt.gca()

        # features
        io_time = self.io.columns[0]
        io_read = self.io.columns[1]
        io_write = self.io.columns[2]
        io_busy_time = self.io.columns[3]

        # create lines
        self.io.plot(kind='line', x=io_time, y=io_read, ax=ax)
        self.io.plot(kind='line', x=io_time, y=io_write, ax=ax)

        # plot!
        plt.title('Input/Output')
        plt.xlabel(io_time)
        plt.ylabel('Bytes')
        plt.legend()
        plt.show()
        #plt.savefig('figs/io_' + self.ts + '.png')

    def get_cpu_plt(self):
        ax = plt.gca()
        ax.set_prop_cycle(color=UNIQUE_COLORS)

        cpu_time = self.cpu.columns[0]

        for i,cpu_no in enumerate(self.cpu.columns[1:], start=0):
            self.cpu.plot(kind='line', x=cpu_time, y=cpu_no, ax=ax)

        plt.title('CPU Utilization')
        plt.xlabel(cpu_time)
        plt.ylabel('Percentage utilized')
        plt.legend()
        plt.show()
        #plt.savefig('figs/cpu_' + self.ts + '.png')

    def get_mem_plt(self):
        ax = plt.gca()

        mem_time = self.mem.columns[0]
        mem_ram  = self.mem.columns[1]
        mem_swap = self.mem.columns[2]

        self.mem.plot(kind='line', x=mem_time, y=mem_ram, ax=ax)
        self.mem.plot(kind='line', x=mem_time, y=mem_swap, ax=ax)

        plt.title('Memory Utilization')
        plt.xlabel(mem_time)
        plt.ylabel('MB utilized')
        plt.legend()
        plt.show()
        #plt.savefig('figs/cpu_' + self.ts + '.png')

    def get_net_plt(self):
        ax = plt.gca()

        net_time    = self.net.columns[0]
        net_sent    = self.net.columns[1]
        net_recv    = self.net.columns[2]

        self.net.plot(kind='line', x=net_time, y=net_sent, ax=ax)
        self.net.plot(kind='line', x=net_time, y=net_recv, ax=ax)

        plt.title('Network Utilization')
        plt.xlabel(net_time)
        plt.ylabel('Bytes')
        plt.legend()
        plt.show()
        #plt.savefig('figs/cpu_' + self.ts + '.png')

def get_unique_timestamps():
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
    # create neccesary dirs
    if not os.path.exists(FIG_DIR):
        os.mkdir(FIG_DIR)

    metrics = create_metrics(get_unique_timestamps())

    for m in metrics:
        m.get_cpu_plt()
        #m.get_io_plt()
        #m.get_mem_plt()
        #m.get_net_plt()

if __name__ == "__main__":
    main()
