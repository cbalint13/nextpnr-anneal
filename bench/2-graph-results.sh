#!/bin/sh

for bench in {marlann,picorv32}
do

  echo "Graph in $bench"

  pushd $bench
  python ../../scripts/graph-results.py
  popd

done

