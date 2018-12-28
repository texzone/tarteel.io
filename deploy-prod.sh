#!/usr/bin/env bash

# exit on any failure
set -e

REPO=tarteel
PORT=80

# stop and remove existing container
if [ -n "$(docker ps --all --quiet --filter name=^/${REPO}$)" ]; then
  docker stop ${REPO}
  docker rm ${REPO}
fi

# get APP_PATH (parent of config)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_PATH="$SCRIPT_DIR/"

# start container
set -x
args+=(
  --name=${REPO}
  --cpus="1.0"
  --memory=2g
  --restart=always
  --volume=${APP_PATH}:/app
  --workdir=/app
  --detach
  --publish $PORT:8000
  --env TERM=xterm-256color
  --env ENV=development
  --tty
  nikolaik/python-nodejs:latest
  /bin/sh -c "npm install yuglify sass && pip3 install -r requirements.txt && ./manage.py makemigrations && ./manage.py migrate && ./manage.py runserver 0.0.0.0:8000"
)
docker run "${args[@]}"

echo "started $REPO"
# container logs
docker logs --follow ${REPO}
