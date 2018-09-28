#!/bin/bash
#

git pull

./init-conf.sh

docker-compose down

docker-compose up -d
