#!/usr/bin/env bash

HERE=$(cd `dirname $0`; pwd)
SPDZROOT=$HERE/../MP-SPDZ

export PLAYERS=${PLAYERS:-3}

if test "$THRESHOLD"; then
    t="-T $THRESHOLD"
fi

. $SPDZROOT/Scripts/run-common.sh

run_player mal-shamir-offline.x $* $t || exit 1
