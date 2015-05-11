import sys

template = """include redis-default.conf
latency-monitor-threshold 10
repl-backlog-size 32mb
repl-disable-tcp-nodelay yes
client-output-buffer-limit normal 0 0 0

port %s
dbfilename "%s.rdb"

dir .

slaveof 127.0.0.1 %s
"""

for i in range(1, int(sys.argv[1]) + 1):
    master = 6000 + i
    slave = master + 1000
    with open('redis%d.conf' % slave, 'wt') as f:
        f.write(template % (slave, slave, master))
