#!/usr/bin/env bash

SCRIPT_DIR=$(cd `dirname $0`; pwd)
SPDZ_ROOT=$SCRIPT_DIR/../MP-SPDZ
SPDZ_SCRIPTS=$SPDZ_ROOT/Scripts

export PLAYERS=${PLAYERS:-3}

if test "$THRESHOLD"; then
    t="-T $THRESHOLD"
fi

. $SPDZ_SCRIPTS/run-common.sh

run_player mal-shamir-offline.x $* $t || exit 1
