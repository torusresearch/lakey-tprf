#!/usr/bin/env bash

prog="${PROG:-lakey2}"
prime="${PRIME:-57896044618658097711785492504343953926634992332820282019728792003956566065153}"

./MP-SPDZ/compile.py -O -P $prime $prog &&
./Scripts/mal-shamir-offline.sh -P $prime $prog &&
./MP-SPDZ/Scripts/mal-shamir.sh -P $prime -F $prog
