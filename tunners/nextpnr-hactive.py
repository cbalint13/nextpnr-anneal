#!/usr/bin/python3

"""
/*********************************************************************
 * Software License Agreement (BSD License)
 *
 * Copyright (c) 2021
 *
 * Balint Cristian <cristian dot balint at gmail dot com>
 *
 * NextPNR hyperactive tunner.
 * Based on: https://github.com/SimonBlanke/Hyperactive
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
  nexpnr-hactive.py (Tunner for nextpnr)
"""

import os
import sys
import time
import pickle
import subprocess
import numpy as np

from hyperactive import Hyperactive, DecisionTreeOptimizer, \
                        ParallelTemperingOptimizer, SimulatedAnnealingOptimizer, HillClimbingOptimizer, \
                        RandomRestartHillClimbingOptimizer, ParticleSwarmOptimizer, EvolutionStrategyOptimizer \

verbose = False

def evalpnr(space):

  # nextpnr args
  args = ' '.join(map(str, sys.argv[1:]))

  # suppress quiet mode
  args = args.replace('-q','')

  # append optimisation parameters
  cmd = ("%s --placer-heap-alpha %f --placer-heap-beta %f --placer-heap-critexp %i --placer-heap-timingweight %i"
      % (args, space['alpha'], space['beta'], space['critexp'], space['tweight']))

  # launch process
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

  clk = {}
  # parse process logs
  while ( process.poll() is None ):
    output = process.stdout.readline().decode()
    if 'Max frequency for clock' in output:
      clkname = output.split()[5].replace('\'','').replace(':','')
      clk['%s' % clkname] = float(output.split()[6])
      continue

  loss = clk[clkname]
  if (verbose):
    print( "space [%s] -> %f(Mhz) loss=%f" % (space.values(), clk[clkname], loss) )
  return loss

def main():

  n_jobs = 8
  spaces = list()

  # list of weights
  tweight = np.arange(1, 40, 5)

  # split space on weights
  for k in range(0, n_jobs):
    space = {
      'alpha'   : np.arange(0.025, 0.525, 0.025),
      'beta'    : np.arange(0.500, 1.025, 0.025),
      'critexp' : np.arange(1,     11,        1),
      'tweight' : np.array([tweight[k]]        )
    }
    spaces.append(space)

  optimizer = DecisionTreeOptimizer(
      tree_regressor="random_forest",
      xi=0.02,
      rand_rest_p=0.05)

  hyper = Hyperactive()
  for k in range(0, n_jobs-1):
    hyper.add_search(evalpnr, spaces[k], optimizer=optimizer, n_iter=10)

  hyper.run()

if __name__ == "__main__":
  main()
