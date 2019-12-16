# Script to gather data of PostgreSQL queries
Multi-threaded client-server program to gather metrics
on a (sharded) PostgreSQL database.

## Install
Make sure you've installed dependencies listed below.

  - clone repo (experiment script assumes you do this in home folder)
```
git clone https://github.com/shoaloak/postgres-meaxecutor
cd postgres-meacexutor
```
  - Create and activate python virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```
  - install python deps
```
pip install -r requirements.txt
```

## Example

### single database
```
./meaxecutor.py -q "SELECT * FROM posts LIMIT 1"
```

### sharded database main node
```
./meaxecutor.py -q "SELECT * FROM posts LIMIT 1" -a "192.168.0.2"

```

#### on sharded nodes
```
./meaxecutor.py -s
```

## deps
all:
apt install python3 python3-venv

meaxector:
apt install postgresql-server-dev-11

data processor:
apt install python3-tk
