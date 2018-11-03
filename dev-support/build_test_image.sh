#!/usr/bin/env bash

CWD=`cd $(dirname $0);pwd`
IMAGE_TAG='workflow:test'
docker build -t $IMAGE_TAG $CWD/image_test