import sys

template = """include sentinel-default.conf
port %s"""

for i in range(1, int(sys.argv[1]) + 1):
    with open('sentinel%d.conf' % i) as f:
        f.write(template % i)
