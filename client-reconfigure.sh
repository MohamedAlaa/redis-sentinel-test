#!/bin/bash

master=$1
role=$2
state=$3
old_ip=$4
old_port=$5
new_ip=$6
new_port=$7

python twemproxy-reconfigure.py $old_ip $old_port $new_ip $new_port "twemproxy.yml" "sudo restart twemproxy" --log reconfigure.log
