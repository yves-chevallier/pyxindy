#!/bin/sh

#
# err1 causes xindy to give up, thus there is no output available
#

if grep "ERROR: READ:" err1.xlg >/dev/null
then
    exit 0
else
    exit 1
fi
