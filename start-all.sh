#!/bin/bash

#for i in {6001..6048}
for i in {6001..6001}
do
    redis-server redis$i.conf
done

#for i in {7001..7048}
for i in {7001..7001}
do
    redis-server redis$i.conf
done

#for i in {8001..8021}
for i in {8001..8003}
do
    redis-sentinel sentinel$i.conf
done
