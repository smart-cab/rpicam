#!/usr/bin/sh
echo $(docker inspect --format "{{.NetworkSettings.Networks.smartcab.Gateway}}" redis) > redis_ip
