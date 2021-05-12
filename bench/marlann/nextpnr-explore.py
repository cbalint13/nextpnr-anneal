#!/usr/bin/python

"""
/*********************************************************************
 * Software License Agreement (BSD License)
 *
 * Copyright (c) 2021
 *
 * Balint Cristian <cristian dot balint at gmail dot com>
 *
 * NextPNR bruteforce explorer.
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
  nexpnr-explore.py (Brute force expoler)
"""

import os
import sys
import time
import subprocess
import numpy as np


nthreads = 16
opath = "experiments"

r_alpha   = np.arange(0.025, 0.525, 0.025)
r_beta    = np.arange(0.500, 1.025, 0.025)
r_critexp = np.arange(    1,    11,     1)
r_tweight = np.arange(    1,    35,     5)



def nprocs():
  return len(subprocess.Popen("ps ax | grep nextpnr | grep -v grep | grep -v xz", shell=True, stdout=subprocess.PIPE).communicate()[0].splitlines())

def main():

  space_size = len(r_alpha) * len(r_beta) * len(r_critexp) * len(r_tweight)

  print("Explore space size: %i" % space_size)

  if (not os.path.exists(opath)):
    os.mkdir(opath)

  idx = 0;
  for alpha in r_alpha:
    for beta in r_beta:
      for critexp in r_critexp:
        for tweight in r_tweight:

            idx += 1
            logfile = "nextpnr-alpha_%.3f-beta_%.3f-critexp_%i-tweight_%i" \
                    %  (alpha, beta, critexp, tweight)

            while (nprocs() > nthreads):
               time.sleep(1.0)

            filepath = "%s/%s" % (opath,logfile)
            if not os.path.isfile("%s.xz" % filepath):
              print("#%i/%i [%s]" % (idx, space_size, logfile))
              cmd = ("/usr/bin/nextpnr-ice40 -q -v -l %s.log --up5k --package sg48 --seed 1234 --router router1 --freq 24 --asc marlann.asc --pcf marlann_qpi.pcf --json marlann.json --placer-heap-alpha %f --placer-heap-beta %f --placer-heap-critexp %i --placer-heap-timingweight %i; xz -9 %s.log"
                      % (filepath, alpha, beta, critexp, tweight, filepath))
              os.popen(cmd)
            else:
              print("#%i/%i [%s] exists: SKIP" % (idx, space_size, logfile))

if __name__ == "__main__":
  main()
