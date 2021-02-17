#!/bin/sh

for bench in {marlann,picorv32}
do

  echo "Brute-force in $bench"

  pushd bench/$bench
  python nextpnr-explore.py
  popd

done
