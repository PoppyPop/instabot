#!/bin/bash
#


docker run -it --rm -v insta-config:/volume -v ${PWD}:/orig alpine \
    sh -c "cp -fa /orig/conf/* /volume/"


docker run -it --rm -v insta-cookies:/volume -v ${PWD}:/orig alpine \
    sh -c "cp -fa /orig/conf-cookies/* /volume/"