#!/bin/sh

for bench in {marlann,picorv32}
do

  echo "Brute-force in $bench"

  pushd $bench
  python nextpnr-explore.py
  popd

done
