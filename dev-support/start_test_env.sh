#!/usr/bin/env bash

PROJECT_ROOT='/tmp/ojr'
CWD=`cd $(dirname $0)/..;pwd`
IMAGE_TAG='workflow:test'
NETWORK_NAME='wf_test'
MONGO_SERVER='mongo_test_server'

# create customized network
network=`docker network ls | grep $NETWORK_NAME`
if [ ! -n "$network" ]
then
    docker network create $NETWORK_NAME
fi

# start mongodb server in the background
runningMongo=`docker container ls | grep $MONGO_SERVER`
deadMongo=`docker ps -a -f "name=$MONGO_SERVER" | grep $MONGO_SERVER`
if [ ! -n "$runningMongo" ]
then
    if [ -n "$deadMongo" ]
    then
        mongoId=`echo $deadMongo | awk '{print $1}'`
        docker container start $mongoId
    else
        docker run --name=$MONGO_SERVER --network=$NETWORK_NAME -d mongo:3.2
    fi
fi

image_tmp='workflow:test_tmp'

docker build -t $image_tmp - <<image
FROM ${IMAGE_TAG}
ENV PYTHONPATH=${PYTHONPATH}:${PROJECT_ROOT} LC_ALL=C
image

docker run --rm=true -it \
    --network=$NETWORK_NAME \
    -w $PROJECT_ROOT \
    -v $CWD:$PROJECT_ROOT \
    $image_tmp
