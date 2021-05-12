#!/usr/bin/python

"""
/*********************************************************************
 * Software License Agreement (BSD License)
 *
 * Copyright (c) 2021
 *
 * Balint Cristian <cristian dot balint at gmail dot com>
 *
 * NextPNR optuna tunner.
 * Based on: https://github.com/optuna/optuna
 *
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *
 *   * Neither the name of the copyright holders nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 *
 *********************************************************************/
"""

"""
  nexpnr-optuna.py (Tunner for nextpnr)
"""

import os
import sys
import time
import pickle
import subprocess
import numpy as np

import optuna

verobse = False

def evalpnr(trial):

  space = {
        'alpha'   : trial.suggest_discrete_uniform ('alpha',     0.025, 0.500, 0.025),
        'beta'    : trial.suggest_discrete_uniform ('beta',      0.500, 1.000, 0.500),
        'critexp' : trial.suggest_int              ('critexp',   1,     15   ),
        'tweight' : trial.suggest_int              ('tweight',   5,     40   )
  }

  # nextpnr args
  args = ' '.join(map(str, sys.argv[1:]))

  # suppress quiet mode
  args = args.replace('-q','')

  # append optimisation parameters
  cmd = ("%s --placer-heap-alpha %f --placer-heap-beta %f --placer-heap-critexp %i --placer-heap-timingweight %i"
          % (space['alpha'], space['beta'], space['critexp'], space['tweight']))

  # launch process
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

  clk = {}
  # parse process log
  while ( process.poll() is None ):
    output = process.stdout.readline().decode()
    if 'Max frequency for clock' in output:
      clkname = output.split()[5].replace('\'','').replace(':','')
      clk['%s' % clkname] = float(output.split()[6])
      continue

  loss = clk[clkname]
  if (verbose):
    print( "space [%s] -> %f(Mhz) loss=%f" % (space, clk[clkname], loss) )

  return loss

def main():

  if (sys.argv[1] != "nextpnr-ice40"):
    print("ERROR: only nexpnr-ice40 is supported")
    sys.exit(1)

  study = optuna.create_study(direction='maximize', sampler=optuna.samplers.CmaEsSampler())
  study.optimize(evalpnr, n_trials=100)

if __name__ == "__main__":
  main()
