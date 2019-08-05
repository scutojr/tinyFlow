#!/usr/bin/env bash

CWD=`cd $(dirname $0)/..;pwd`
source $CWD/dev-support/start_test_env.sh

docker run --rm=true -it \
    --name tobot_runner \
    --network=$NETWORK_NAME \
    -w $PROJECT_ROOT \
    -v $CWD:$PROJECT_ROOT \
    --dns "$DNS_SERVER" \
    $image_tmp
