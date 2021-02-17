#!/usr/bin/python

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
