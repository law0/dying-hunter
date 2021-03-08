#!/bin/bash
shDir=$( dirname "${BASH_SOURCE[0]}" )

pushd $shDir &>/dev/null
client_example/main.py $@
rc=$?
popd &>/dev/null
exit $rc
