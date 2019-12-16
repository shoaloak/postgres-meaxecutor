#!/bin/bash

# ensure you have the following in .ssh/config...
# uncommented ofcourse ;)

#Host ceph1
#	AddressFamily inet
#	HostName exp12.studexp.os3.nl
#	Port 22
#	User owa
#	IdentityFile ~/.ssh/ceph1
#
#Host ceph2
#	AddressFamily inet
#	ProxyJump ceph1
#	HostName 192.168.0.2
#	User owa
#	IdentityFile ~/.ssh/ceph1
#
#Host ceph4
#	AddressFamily inet
#	ProxyJump ceph1
#	HostName 192.168.0.4
#	User owa
#	IdentityFile ~/.ssh/ceph1

# this scripts assumes that the meaxecutor is in $HOME on the cephs

DST="./"
#mkdir -p "$DST"{1,2,4}

scp -r ceph1:~/postgres-meaxecutor/logs "$DST"
scp -r ceph2:~/postgres-meaxecutor/logs "$DST"
scp -r ceph4:~/postgres-meaxecutor/logs "$DST"
