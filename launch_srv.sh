#!/bin/bash
shDir=$( dirname "${BASH_SOURCE[0]}" )

pushd $shDir &>/dev/null
srv/main.py $@
rc=$?
popd &>/dev/null
exit $rc
