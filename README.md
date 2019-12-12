# Script to gather data of PostgreSQL queries
Multi-threaded client-server program to gather metrics
on a (sharded) PostgreSQL database.

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
meaxector:
apt install postgresql-server-dev-11

data processor:
apt install python3-tk
