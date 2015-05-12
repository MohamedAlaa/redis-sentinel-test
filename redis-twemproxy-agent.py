import os
import time
import sys
import redis
import yaml
import logging
import logging.handlers
import argparse
import re
import subprocess

re_server_info = re.compile('([^:]+):(\d+):(\d+) (.*)')

parser = argparse.ArgumentParser(description='Detect sentinel failover, rewrite \
    twemproxy config, restart twemproxy')
parser.add_argument('host', help='sentinel host')
parser.add_argument('port', help='sentinel port')
parser.add_argument('config', help='twemproxy config')
parser.add_argument('command', help='command to execute')
parser.add_argument('--log', help='log filename')
args = parser.parse_args()

# Setup logging
if args.log:
    handler = logging.handlers.WatchedFileHandler(filename=args.log)
else:
    handler = logging.StreamHandler(sys.stdout)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Does config exists?
if not os.path.exists(args.config):
    logging.error('Twemproxy config not found: %s', args.config)
    sys.exit(1)
# Is config valid?
try:
    with open(args.config) as f:
        config = yaml.safe_load(f)
except yaml.YAMLError as e:
    logging.error('Twemproxy yaml error: %s', e)
    sys.exit(1)

# Subscribe to sentinel
logging.info('Subscribing to sentinel host: %s, port: %s', args.host, args.port)
try:
    redis_sentinel = redis.StrictRedis(host=args.host, port=args.port)
    pubsub = redis_sentinel.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe('+switch-master')
except redis.exceptions.RedisError as e:
    logging.error('Redis setup error: %s', e)
    sys.exit(1)

# Process sentinel messages
while True:
    try:
        message = pubsub.get_message()
    except redis.exceptions.RedisError as e:
        logging.error('Redis subscribe error: %s', e)
        sys.exit(1)

    if not message:
        time.sleep(0.001)
        continue

    logging.info('Received message %s', message)

    data = message['data'].split(' ')
    if len(data) != 5:
        logger.error('Unrecognized message data, expecting 5 pieces of info, \
            got %d instead', len(data))
        sys.exit(1)

    name = data[0]
    old_ip = data[1]
    old_port = data[2]
    new_ip = data[3]
    new_port = data[4]

    # Get twemproxy config
    try:
        with open(args.config) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logging.error('Error loading twemproxy config. Unable to handle \
            switch-master event: %s', e)
        sys.exit(1)

    # Find all instances of old address and replace with new address
    changed = False
    for pool, data in config.iteritems():
        for i, server in enumerate(data['servers']):
            match = re_server_info.match(server)
            if match:
                ip, port, weight, name = match.groups()
                if old_ip == ip and old_port == port:
                    entry = '%s:%s:%s %s' % (new_ip, new_port, weight, name)
                    logging.info('Replacing %s with %s in pool %s', server, entry, pool)
                    config[pool]['servers'][i] = entry
                    changed = True

    if changed:
        try:
            # Write config
            logging.info('Rewriting config: %s', args.config)
            with open(args.config, 'wt') as f:
                f.write(yaml.dump(config, default_flow_style=False))
        except Exception as e:
            logging.error('Error writing twemproxy config: %s', e)
            sys.exit(1)

        # Execute specified command
        logging.info('Executing command: %s', args.command)
        try:
            status = subprocess.call(args.command, shell=True)
            logging.info('Command return code: %s', status)
        except Exception as e:
            logging.error('Error executing command: %s', e)
            sys.exit(1)

