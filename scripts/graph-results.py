#!/usr/bin/python

"""
/*********************************************************************
 * Software License Agreement (BSD License)
 *
 * Copyright (c) 2021
 *
 * Balint Cristian <cristian dot balint at gmail dot com>
 *
 * NextPNR brute force experiment graph plotter.
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
  graph-results.py (Graph plotter)
"""

import matplotlib
import numpy as np
from matplotlib import cm
from matplotlib.ticker import LinearLocator
import matplotlib.pyplot as plt


def main():

  import json
  with open('log-data.json', 'r') as jsonfile:
    data = json.load(jsonfile)

  clks = {}
  alphas = []
  betas = []

  idx = 0
  clkmax = {}
  for c in data:

    for d in data[c]['clkmax']:
      val = data[c]['clkmax'][d]
      # init dict
      if (d not in clks):
        clks['%s' % d] = []
        clkmax['%s' % d] = 0
      # store
      clks['%s' % d].append(val)
      # pick best
      if (clkmax['%s' % d] < val):
        clkmax['%s' % d] = val
        print( data[c] )

  for clk in clks:

    clkmin = np.min(clks[clk])
    clkmax = np.max(clks[clk])

    num_bins = 200
    fig, ax = plt.subplots()
    # histogram of the data
    n, bins, patches = ax.hist(clks[clk], num_bins, density=0)
    # max / min
    ax.axvline( clkmin, linestyle='dotted', color='#EE0000')
    ax.axvline( clkmax, linestyle='dotted', color='#00EE00')
    # labels
    ax.set_xlabel('Clocks (Mhz)\n(min=%.2f / max=%.2f)' % (clkmin, clkmax))
    ax.set_ylabel('Occurence')
    ax.set_title(r'Histogram of Clocks [%s]' % clk.replace('$','_'))

    # Tweak spacing to prevent clipping of ylabel
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
  main()
