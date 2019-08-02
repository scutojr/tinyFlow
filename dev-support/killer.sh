#!/usr/bin/env bash


function kill_process() {
    local procName="$1"
    ps -ef |grep "$procName" | grep python | awk '{print $2}' | xargs -I PID kill -9 PID
}


if [ "$1" = "all" ]
then
    kill_process "tobot"
    kill_process "runner"
elif [ "$1" = "runner" ] 
then
    kill_process "runner"
fi
