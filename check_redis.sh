for i in {6001..6048}; do echo "-- $i" && redis-cli -p $i info | grep db0; done
