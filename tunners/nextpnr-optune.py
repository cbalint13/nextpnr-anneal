#!/usr/bin/python

import os
import sys
import time
import pickle
import subprocess
import numpy as np

import optuna

#def objective(trial):
#    return train_evaluate(params)

def pnreval(trial):

  space = {
        'alpha'   : trial.suggest_discrete_uniform ('alpha',     0.025, 0.500, 0.025),
        'beta'    : trial.suggest_discrete_uniform ('beta',      0.500, 1.000, 0.500),
        'critexp' : trial.suggest_int              ('critexp',   1,     15   ),
        'tweight' : trial.suggest_int              ('tweight',   5,     40   )
  }

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

  loss = clk[clkname]
  #print( "space [%s] -> %f(Mhz) loss=%f" % (space, clk[clkname], loss) )
  return loss



def main():

  study = optuna.create_study(direction='maximize', sampler=optuna.samplers.CmaEsSampler())
  study.optimize(pnreval, n_trials=500)

if __name__ == "__main__":
  main()
