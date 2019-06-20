#!/usr/bin/env bash

PROJECT_ROOT='/tmp/ojr'
CWD=`cd $(dirname $0)/..;pwd`
IMAGE_TAG='workflow:test'
NETWORK_NAME='wf_test'

MONGO_SERVER='mongo_test_server'
MONGO_IMAGE='mongo:3.2'

AMQ_SERVER='amq_test_server'
AMQ_IMAGE='webcenter/activemq:latest'

PORT=54321

# create customized network
network=`docker network ls | grep $NETWORK_NAME`
if [ ! -n "$network" ]
then
    docker network create $NETWORK_NAME
fi

function start_db() {
    local db_name=$1
    local image=$2
    local isRunning=`docker container ls | grep $db_name`
    local deadDb=`docker ps -a -f "name=$db_name" | grep $db_name`
    if [ ! -n "$isRunning" ]
    then
        if [ -n "$deadDb" ]
        then
            containerId=`echo $deadDb | awk '{print $1}'`
            docker container start $containerId
        else
            docker run --name=$db_name --network=$NETWORK_NAME -d $image
        fi
    fi
}

# start mongodb server in the background
start_db $MONGO_SERVER  $MONGO_IMAGE

# start activeMq server in the background
start_db $AMQ_SERVER  $AMQ_IMAGE

image_tmp='workflow:test_tmp'

docker build -t $image_tmp - <<image
FROM ${IMAGE_TAG}
ENV PYTHONPATH=${PYTHONPATH}:${PROJECT_ROOT} LC_ALL=C
image

docker run --rm=true -it \
    --network=$NETWORK_NAME \
    -w $PROJECT_ROOT \
    -v $CWD:$PROJECT_ROOT \
    -p $PORT:$PORT \
    $image_tmp
