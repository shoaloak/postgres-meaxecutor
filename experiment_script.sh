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
	systemctl stop postgresql.service
	# clear pagecache and dentries/inodes
	echo 3 > /proc/sys/vm/drop_caches
	systemctl start postgresql.service
}

# doesnt work untill measurer server spawns new threads...
multi_query() {
	query=$1

	./measure_while_executing_sql.py -q "$query" -a "192.168.0.2" &
	sleep 0.1
	./measure_while_executing_sql.py -q "$query" -a "192.168.0.2" &
	wait
}

run_experiment() {
	query=$1

	while [ "$i" -le "$(($N - 1))" ];
	do
		if $CACHE
		then
			clear_cache_postgres
		fi
		./measure_while_executing_sql.py -q "$query" > "exp$1_cache$CACHE.result"
		i=$(($i + 1))
	done
}

#PSQ="EXPLAIN ANALYZE SELECT badges.userid FROM badges WHERE badges.userid NOT IN (SELECT users.id FROM users LIMIT 10);"
main() {
	query=$1
	run_experiment $query
}


# MAIN
if [ -z "$1" ]
then
	echo "No query supplied, quitting..."
	exit
fi

main $1
