#!/usr/bin/python3

"""
/*********************************************************************
 * Software License Agreement (BSD License)
 *
 * Copyright (c) 2021
 *
 * Balint Cristian <cristian dot balint at gmail dot com>
 *
 * NextPNR mango tunner.
 * Based on: https://github.com/ARM-software/mango
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
  nextpnr-mango.py (Tunner for nexpnr with parallel support)
"""

import os
import sys
import subprocess

from mango import Tuner, scheduler

verbose = False

@scheduler.parallel(n_jobs=-1)
def evalpnr(alpha, beta, critexp, tweight):

  # nextpnr args
  args = ' '.join(map(str, sys.argv[1:]))

  # suppress quiet mode
  args = args.replace('-q','')

  # append optimisation parameters
  cmd = ("%s --placer-heap-alpha %f --placer-heap-beta %f --placer-heap-critexp %i --placer-heap-timingweight %i"
      % (args, alpha, beta, critexp, tweight))

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

  loss = 0.0
  for key in clk:
    loss += clk[key]
  if (verbose):
    print("[alpha=%.3f beta=%.3f critexp=%i tweight=%i] -> %f(Mhz) loss=%f [%s]" %
           (alpha, beta, critexp, tweight, clk[clkname], loss, clk) )
  return loss

def main():

  if (sys.argv[1] != "nextpnr-ice40"):
    print("ERROR: only nexpnr-ice40 is supported")
    sys.exit(1)

  space = {
        'alpha'   : [x * .025 for x in range( 1,21)], # 0.025->0.5 (.25 step)
        'beta'    : [x * .025 for x in range(20,41)], # 0.500->1.0 (.25 step)
        'critexp' : range(1,11, 1),
        'tweight' : range(1,35, 5),
  }

  cfg = dict(num_iteration=20)
  tuner = Tuner(space, evalpnr, cfg)
  results = tuner.maximize()

  print("Best clock: %s Mhz" % results["best_objective"])
  print("Best parameters: [%s]" % results["best_params"])


if __name__ == "__main__":
  main()
