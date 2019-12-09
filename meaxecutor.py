#!/usr/bin/env python3
import datetime
import os
import sys
from threading import Event, Thread
import time

# packages
import psutil
import psycopg2

# GLOBALS
DB_CREDENTIALS  = "dbname=stackoverflow user=owa"
DELTA           = 0.1     # min: 0.1
DISK            = 'sdb1'
LOG_DIR         = 'logs/'
NIC             = 'eno4'
MB              = 1024*1024

def io_measurer(e, stop):
    log_fn = LOG_DIR + "io_stats{}.csv".format(datetime.datetime.now().strftime("%d%m-%H%M%s"))
    try:
        log_fp = open(log_fn, "a+")
    except IOError:
        print("error opening {}".format(log_fn))
        sys.exit(1)
    
    log_fp.write("Date, Time, Written(B), Read(B), Busy Time(ms)\n")

    e.wait()
    hdd_metrics = psutil.disk_io_counters(perdisk=True)[DISK]
    # TODO: change to dict or list... ugly as hell
    # metric_dict = {'readb': hdd_metrics[2],
    #                'writeb': hdd_metrics[3],
    #                'busyt': hdd_metrics[8]}
    readb = hdd_metrics.read_bytes
    writeb = hdd_metrics.write_bytes
    busyt = hdd_metrics.busy_time
    while True:
        time.sleep(DELTA)
        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%d.%m.%Y,%H:%M:%S')
        hdd_metrics = psutil.disk_io_counters(perdisk=True)[DISK]

        readb_new = hdd_metrics.read_bytes
        writeb_new = hdd_metrics.write_bytes
        busyt_new = hdd_metrics.busy_time
        writeb_diff = writeb_new - writeb
        readb_diff = readb_new - readb
        busyt_diff = busyt_new - busyt
        writeb = writeb_new
        readb = readb_new
        busyt = busyt_new

        log_fp.write(ts + "," + str(writeb_diff) + "," + str(readb_diff) + "," + str(busyt_diff) + "\n")
        if stop():
            log_fp.close()
            break

def cpu_measurer(e, stop):
    log_fn = LOG_DIR + "cpu_stats{}.csv".format(datetime.datetime.now().strftime("%d%m-%H%M%s"))
    try:
        log_fp = open(log_fn, "a+")
    except IOError:
        print("error opening {}".format(log_fn))
        sys.exit(1)
    
    csv_header = "Date, Time"
    no_cores = psutil.cpu_count()
    for core in range(no_cores):
        csv_header += ", CPU{}%".format(core)
    log_fp.write(csv_header + "\n")

    e.wait()
    while True:
        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%d.%m.%Y,%H:%M:%S')

        percents = psutil.cpu_percent(interval=DELTA, percpu=True)
        percent_str = "{}".format(str(percents[0]))
        for percent in percents[1:]:
            percent_str += ", {}".format(str(percent))

        log_fp.write(ts + "," + percent_str + "\n")
        if stop():
            log_fp.close()
            break

def net_measurer(e, stop):
    log_fn = LOG_DIR + "net_stats{}.csv".format(datetime.datetime.now().strftime("%d%m-%H%M%s"))
    try:
        log_fp = open(log_fn, "a+")
    except IOError:
        print("error opening {}".format(log_fn))
        sys.exit(1)
    
    log_fp.write("Date, Time, sent(B), received(B)\n")

    e.wait()
    net_metrics = psutil.net_io_counters(pernic=True, nowrap=True)[NIC]
    sentb = net_metrics.bytes_sent
    recvb = net_metrics.bytes_recv
    while True:
        time.sleep(DELTA)
        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%d.%m.%Y,%H:%M:%S')
        net_metrics = psutil.net_io_counters(pernic=True, nowrap=True)[NIC]

        sentb_new = net_metrics.bytes_sent
        recvb_new = net_metrics.bytes_recv
        sentb_diff = sentb_new - sentb
        recvb_diff = recvb_new - recvb
        sentb = sentb_new
        recvb = recvb_new

        log_fp.write(ts + "," + str(sentb_diff) + "," + str(recvb_diff) + "\n")
        if stop():
            log_fp.close()
            break

# TODO: create
#def mem_measurer(e, stop):

def create_threads(e, stop_mutex):
    io_thread = Thread(target=io_measurer, args=(e,stop_mutex,))
    cpu_thread = Thread(target=cpu_measurer, args=(e,stop_mutex,))
    net_thread = Thread(target=net_measurer, args=(e,stop_mutex,))
    return [io_thread, cpu_thread, net_thread]

def main(sql_query):
    # e for signalling to start measuring, vice versa ;)
    e = Event()
    stop_measuring = False

    # create threads and start them
    threads = create_threads(e, lambda : stop_measuring,)
    for t in threads:
        t.start()

    # create db connection
    conn = psycopg2.connect(DB_CREDENTIALS)
    cur = conn.cursor()

    # start measurement, execute query, stop measurement
    time.sleep(0.1)
    try:
        query_status = True
        e.set()
        cur.execute(sql_query)
    except psycopg2.errors.SyntaxError:
        query_status = False
        print("SQL Syntax error!")

    stop_measuring = True

    # results
    if query_status:
        print(cur.fetchone())

    # cleanup
    for t in threads:
        t.join()
    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: {} [SQL query]".format(sys.argv[0]))
        sys.exit(1)

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    main(sys.argv[1])
