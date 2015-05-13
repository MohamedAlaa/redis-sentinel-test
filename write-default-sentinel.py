#!/usr/bin/env python

import sys

count = int(sys.argv[1])
quorum = int(sys.argv[2])

template = """sentinel monitor %(name)s 127.0.0.1 %(port)s %(quorum)s
sentinel down-after-milliseconds %(name)s 3000
sentinel parallel-syncs %(name)s 1
sentinel failover-timeout %(name)s 60000
sentinel client-reconfig-script %(name)s client-reconfigure.sh
"""

with open('default-sentinel.conf', 'wt') as f:
    for i in range(1, count + 1):
        port = 6000 + i
        f.write(template % {
                'port':port,
                'quorum':quorum,
                'name':'master%s' % port
            })
