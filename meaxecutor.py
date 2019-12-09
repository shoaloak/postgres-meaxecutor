#!/usr/bin/env python3
import datetime
import sys
from threading import Event, Thread
import time

# packages
import psutil
import psycopg2

# GLOBALS
DB_CREDENTIALS = "dbname=stackoverflow user=owa"
DISK = 'sdb1'
DELTA = 0.1

def io_measurer(e, stop):
    log_fn = "io_stats{}.csv".format(datetime.datetime.now().strftime("%d%m-%H%M%s"))
    try:
        log_fp = open(log_fn, "a+")
    except IOError:
        print("error opening {}".format(log_fn))
        sys.exit(1)
    
    log_fp.write("Date, Time, Written MB, Read MB, Busy Time(ms), Writen Total MB, Read Total MB, Busy Time Total (ms)\n")

    e.wait()
    hdd_dict = psutil.disk_io_counters(perdisk=True)[DISK]
    # TODO: change to dict
    # metric_dict = {'readb': hdd_dict[2],
    #                'writeb': hdd_dict[3],
    #                'busyt': hdd_dict[8]}
    readb = hdd_dict[2]
    writeb = hdd_dict[3]
    busyt = hdd_dict[8]
    while True:
        time.sleep(DELTA)
        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%d.%m.%Y,%H:%M:%S')
        hdd_dict = psutil.disk_io_counters(perdisk=True)[DISK]

        writebnew = hdd_dict[2]
        readbnew = hdd_dict[3]
        busytnew = hdd_dict[8]
        writebcy = writebnew - writeb
        readbcy = readbnew - readb
        busytcy = busytnew - busyt
        writeb = writebnew
        readb = readbnew
        busyt = busytnew

        log_fp.write(ts + "," + str(writebcy/1048576) + "," + str(readbcy/1048576) + "," + str(busytcy) + "," + str(writebnew/1048576) + "," + str(readbnew/1048576) + "," + str(busytnew) + "\n")

        if stop():
            log_fp.close()
            break

def cpu_measurer(e, stop):
    log_fn = "cpu_stats{}.csv".format(datetime.datetime.now().strftime("%d%m-%H%M%s"))
    try:
        log_fp = open(log_fn, "a+")
    except IOError:
        print("error opening {}".format(log_fn))
        sys.exit(1)
    
    e.wait()
    # get cpu stuff
    while True:

        if stop():
            log_fp.close()
            break

def net_measurer(e, stop):
    log_fn = "net_stats{}.csv".format(datetime.datetime.now().strftime("%d%m-%H%M%s"))
    try:
        log_fp = open(log_fn, "a+")
    except IOError:
        print("error opening {}".format(log_fn))
        sys.exit(1)
    
    e.wait()
    # get net stuff
    while True:

        if stop():
            log_fp.close()
            break

def create_threads(e, stop_mutex):
    io_thread = Thread(target=io_measurer, args=(e,stop_mutex,))
    #cpu_thread = Thread(target=cpu_measurer, args=(e,stop_mutex,))
    #net_thread = Thread(target=net_measurer, args=(e,stop_mutex,))

    #return [io_thread, cpu_thread, net_thread]
    return [io_thread]

def main(sql_query):
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
    print('Starting...')
    e.set()
    cur.execute(sql_query)
    stop_measuring = True
    print('End!')

    # results
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

    main(sys.argv[1])
