#!/bin/bash

RUN_PORT=${PORT:-80}

DEBUG=${DEBUG:-0}

if [ $DEBUG -eq 1 ]; then
    echo "FastApi running in debug mode"
    /usr/local/bin/uvicorn main:app --host 0.0.0.0 --port $RUN_PORT --reload
else
    /usr/local/bin/uvicorn main:app --host 0.0.0.0 --port $RUN_PORT
fi
