#!/usr/bin/python

"""
/*********************************************************************
 * Software License Agreement (BSD License)
 *
 * Copyright (c) 2021
 *
 * Balint Cristian <cristian dot balint at gmail dot com>
 *
 * NextPNR hyperopt tunner.
 * Based on: https://github.com/hyperopt/hyperopt
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
  nexpnr-hoptim.py (Tunner for nextpnr)
"""

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

def evalpnr(space):

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

  loss = 1000.0 / np.exp( np.sqrt(clk[clkname]))

  print( "space [%s] -> %f(Mhz) loss=%f" % (space, clk[clkname], loss) )

  return{'loss': loss, 'status': STATUS_OK, 'eval_time': time.time(), 'attachments': {'time_module': pickle.dumps(time.time)}}

def main():

  if (sys.argv[1] != "nextpnr-ice40"):
    print("ERROR: only nexpnr-ice40 is supported")
    sys.exit(1)

  space = {
    'alpha'   : hp.quniform ('alpha',     0.010, 0.800, 0.010),
    'beta'    : hp.quniform ('beta',      0.300, 1.000, 0.010),
    'critexp' : hp.randint  ('critexp',   1,     10          ),
    'tweight' : hp.randint  ('tweight',   1,     40          ),
  }

  trials = Trials()

  best = fmin(fn = evalpnr,
              space = space,
              algo = tpe.suggest,
              parallelism = 1,
              max_evals = 100,
              trials = trials)

  print("\n\n")
  print("Best found: ", best)


if __name__ == "__main__":
  main()
