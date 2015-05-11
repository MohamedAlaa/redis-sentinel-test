import sys

template = """include default-sentinel.conf
port %s"""

for i in range(1, int(sys.argv[1]) + 1):
    port = 8000 + i
    with open('sentinel%d.conf' % port, 'wt') as f:
        f.write(template % port)
