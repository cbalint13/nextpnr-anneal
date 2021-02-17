#!/usr/bin/python

import os
import sys
import time
import pickle
import subprocess
import numpy as np
from hyperopt import Trials, STATUS_OK, tpe, hp, fmin


nthreads = 16
opath = "experiments"

r_alpha   = np.arange(0.025, 0.525, 0.025)
r_beta    = np.arange(0.500, 1.025, 0.025)
r_critexp = np.arange(    1,    11,     1)
r_tweight = np.arange(    1,    35,     5)

def pnreval(space):

  clk = {}

  # construct command
  cmd = ("/usr/bin/nextpnr-ice40 -v --hx8k --package ct256 --json synth.json --pcf example.pcf --asc example.asc --placer-heap-alpha %f --placer-heap-beta %f --placer-heap-critexp %i --placer-heap-timingweight %i"
          % (space['alpha'], space['beta'], space['critexp'], space['tweight']))

  # launch process
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

  # parse for speed (MHz) in log
  while ( process.poll() is None ):
    output = process.stdout.readline().decode()
    #print( output.strip() )
    if 'Max frequency for clock' in output:
      clkname = output.split()[5].replace('\'','').replace(':','')
      clk['%s' % clkname] = float(output.split()[6])
      continue

  loss = 1000.0 / np.exp( np.sqrt(clk[clkname]))

  print( "space [%s] -> %f(Mhz) loss=%f" % (space, clk[clkname], loss) )

  return{'loss': loss, 'status': STATUS_OK, 'eval_time': time.time(), 'attachments': {'time_module': pickle.dumps(time.time)}}

def main():

  space = {
    'alpha'   : hp.quniform ('alpha',     0.010, 0.800, 0.010),
    'beta'    : hp.quniform ('beta',      0.300, 1.000, 0.010),
    'critexp' : hp.randint  ('critexp',   1,     10          ),
    'tweight' : hp.randint  ('tweight',   1,     40          ),
  }


  trials = Trials()

  best = fmin(fn = pnreval,
              space = space,
              algo = tpe.suggest,
              parallelism = 1,
              max_evals = 100,
              trials = trials)

  print("\n\n")
  print("Best found: ", best)
  pnreval(best)


if __name__ == "__main__":
  main()
