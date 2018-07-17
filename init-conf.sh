#!/bin/bash
#


docker run -it --rm -v insta-config:/volume -v ${PWD}:/orig alpine \
    sh -c "cp -fa /orig/conf/* /volume/"


