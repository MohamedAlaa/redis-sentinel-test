template = """include redis-default.conf
daemonize yes
latency-monitor-threshold 10
repl-backlog-size 32mb
repl-disable-tcp-nodelay yes
client-output-buffer-limit slave 2gb 2gb 60
save ""
dir .
port %(port)s
dbfilename %(port)s.rdb
pidfile %(port)s.pid
logfile %(port)s.log"""

start = 6001
count = 48

for port in range(start, start + count + 1):
    filename = 'redis%s.conf' % port
    with open(filename, 'wt') as f:
        f.write(template % {'port':port})
