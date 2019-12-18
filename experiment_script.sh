#!/bin/bash

# set to false if you dont want cached experiments
CACHE=true
N=3

check_if_su() {
	if [ "$EUID" -ne 0 ]
	then echo "Please run as root"
		exit
	fi
}

clear_cache_postgres() {
	check_if_su
	echo stopping DB
	systemctl stop postgresql.service
	echo clear pagecache and dentries/inodes
	echo 3 > /proc/sys/vm/drop_caches
	echo starting DB
	systemctl start postgresql.service
}

# doesnt work untill measurer server spawns new threads...
multi_query() {
	query=$*

	./measure_while_executing_sql.py -q "$query" -a "192.168.0.2" &
	sleep 0.1
	./measure_while_executing_sql.py -q "$query" -a "192.168.0.2" &
	wait
}

run_experiment() {
	query=$*

	d=`date +%j%H%M%S%N`
	echo "$query\n" >> "exp$d-cache$CACHE.result.txt"

	i=1
	while [ "$i" -le "$(($N))" ]; do
		if ! $CACHE
		then
			clear_cache_postgres
		fi
		echo "Running $i iteration..."
		echo "$i iteration..." >> "exp$d-cache$CACHE.result.txt"
		./measure_while_executing_sql.py -q "$query" >> "exp$d-cache$CACHE.result.txt"
		i=$(($i+1))
	done
}

#PSQ="EXPLAIN ANALYZE SELECT badges.userid FROM badges WHERE badges.userid NOT IN (SELECT users.id FROM users LIMIT 10);"
main() {
	query=$*
	run_experiment $query
}


# MAIN
if [ -z "$1" ]
then
	echo "No query supplied, quitting..."
	exit
fi

main "$*"
