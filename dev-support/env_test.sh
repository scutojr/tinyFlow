#!/usr/bin/env bash

function get_docker_ip() {
    local ip=`docker-machine.exe ls | awk '$4 ~ /Running/ {print $5}' | sed 's/tcp:\/\/\([0-9\.]\+\):[0-9]*/\1/'`
    echo $ip ojr
}

