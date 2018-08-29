#!/bin/bash
#

docker volume create insta-config --label backup=yes

docker volume create insta-cookies --label backup=yes