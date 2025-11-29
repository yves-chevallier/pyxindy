#!/bin/sh

#
# err2 causes xindy to give up, thus there is no output available
#

if grep "ERROR: EVAL:" err2.xlg >/dev/null
then
    exit 0
else
    exit 1
fi
