#!/bin/sh

for bench in {marlann,picorv32}
do

  echo "Parse in $bench"

  pushd bench/$bench
  python ../../scripts/parse-results.py
  popd

done

