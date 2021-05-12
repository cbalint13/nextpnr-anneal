#!/usr/bin/python

"""
/*********************************************************************
 * Software License Agreement (BSD License)
 *
 * Copyright (c) 2021
 *
 * Balint Cristian <cristian dot balint at gmail dot com>
 *
 * NextPNR brute force experiment result parser.
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
  parse-results.py (Data parser)
"""

import os
import sys
import time
import glob
import lzma
import subprocess
import numpy as np

opath = "experiments"

nLastTick = -1
def TermProgress( dfComplete, pszMessage, pProgressArg ):

    global nLastTick
    nThisTick = (int) (dfComplete * 40.0)

    if nThisTick < 0:
        nThisTick = 0
    if nThisTick > 40:
        nThisTick = 40

    # Have we started a new progress run?  
    if nThisTick < nLastTick and nLastTick >= 39:
        nLastTick = -1

    if nThisTick <= nLastTick:
        return True

    while nThisTick > nLastTick:
        nLastTick = nLastTick + 1
        if (nLastTick % 4) == 0:
            sys.stdout.write('%d' % ((nLastTick / 4) * 10))
        else:
            sys.stdout.write('.')

    if nThisTick == 40:
        print(" - done." )
    else:
        sys.stdout.flush()

    return True

def main():

  alpha   = np.nan
  beta    = np.nan
  critexp = np.nan
  tweigth = np.nan

  filenames = glob.glob("%s/*.xz" % opath)

  idx = 0
  stats = {}
  for f in filenames:

    clk = {}
    data = { 'alpha': np.nan,
             'beta': np.nan,
             'critexp': np.nan,
             'tweight': np.nan,
             'clkmax': {},
             'cells': {
                 'LUT4': np.nan,
                 'LUT4_DFF': np.nan,
                 'DFF': np.nan,
                 'CARRY': np.nan,
                 'LEGAL': np.nan }
           }

    # split to lines
    lines = lzma.open(f).read().decode().splitlines()

    # check if log is terminated
    if ( not "Info: Program finished normally" in lines[-1] ):
      print("Logfile unterminated SKIP.")
      continue

    for e in f.split('.log')[0].split('-'):
      if ('alpha' in e):
        data['alpha'] = float(e.split('_')[1])
        continue
      if ('beta' in e):
        data['beta'] = float(e.split('_')[1])
        continue
      if ('critexp' in e):
        data['critexp'] = int(e.split('_')[1])
        continue
      if ('tweight' in e):
        data['tweight'] = int(e.split('_')[1])
        continue

    # iterate lines
    for l in lines:
      if 'LCs used as LUT4 only' in l:
        data['cells']['LUT4'] = int(l.split()[1])
        continue
      if 'LCs used as LUT4 and DFF' in l:
        data['cells']['LUT4_DFF'] = int(l.split()[1])
        continue
      if 'LCs used as DFF only' in l:
        data['cells']['DFF'] = int(l.split()[1])
        continue
      if 'LCs used as CARRY only' in l:
        data['cells']['CARRY'] = int(l.split()[1])
        continue
      if 'LCs used to legalise carry chains' in l:
        data['cells']['LEGAL'] = int(l.split()[1])
      if 'Max frequency for clock' in l:
        clkname = l.split()[5].replace('\'','').replace(':','')
        clk['%s' % clkname] = float(l.split()[6])
        continue

    # all design clocks
    data['clkmax'] = clk

    idx += 1
    stats[idx] = data
    TermProgress( float(idx) / float(len(filenames)), None, None)

  import json
  with open('log-data.json', 'w') as jsonfile:
    json.dump(stats, jsonfile, indent=4)

if __name__ == "__main__":
  main()
