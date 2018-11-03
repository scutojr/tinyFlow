#!/usr/bin/env bash

CWD=`cd $(dirname $0)/..;pwd`
TMP='/tmp/virtualenv'
PY_EXE='python'

virtualenv --always-copy -p ${PY_EXE} ${TMP}
$TMP/bin/pip install -U -r $CWD/requirements.txt
#mv $TMP $CWD