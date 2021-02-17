#!/usr/bin/python

import os
import sys
import time
import pickle
import subprocess
import numpy as np

from hyperactive import Hyperactive, DecisionTreeOptimizer, ParallelTemperingOptimizer, SimulatedAnnealingOptimizer, HillClimbingOptimizer, RandomRestartHillClimbingOptimizer, ParticleSwarmOptimizer, EvolutionStrategyOptimizer

def pnreval(space):


  clk = {}

  # construct command
  cmd = ("/usr/bin/nextpnr-ice40 --hx8k --package ct256 --json synth.json --pcf example.pcf --asc example.asc --placer-heap-alpha %f --placer-heap-beta %f --placer-heap-critexp %i --placer-heap-timingweight %i"
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
  #print( "space [%s] -> %f(Mhz) loss=%f" % (space.values(), clk[clkname], loss) )
  return loss



def main():

  space = {
#        'alpha'   : np.arange(0.025, 0.525, 0.025),
#        'beta'    : np.arange(0.500, 1.025, 0.025),
#        'critexp' : np.arange(1,     11,        1),
#        'tweight' : np.arange(1,     35,        5),
        'alpha'   : np.arange(0.005, 0.505, 0.005),
        'beta'    : np.arange(0.500, 1.005, 0.005),
        'critexp' : np.arange(1,     11,        1),
        'tweight' : np.arange(1,     35,        5),
  }

  optimizer = DecisionTreeOptimizer(
      tree_regressor="random_forest",
      xi=0.02,
      rand_rest_p=0.05)

#  optimizer = ParallelTemperingOptimizer(n_iter_swap=5, rand_rest_p=0.05)
#  optimizer = SimulatedAnnealingOptimizer(
#     epsilon=0.1,
#     distribution="laplace",
#     n_neighbours=4,
#     rand_rest_p=0.1,
#     p_accept=0.15,
#     norm_factor="adaptive",
#     annealing_rate=0.999,
#     start_temp=0.8,
#  )

#  optimizer = HillClimbingOptimizer(
#    epsilon=0.1, distribution="laplace", n_neighbours=4, rand_rest_p=0.1
#  )

#  optimizer = RandomRestartHillClimbingOptimizer(
#    epsilon=0.1,
#    distribution="laplace",
#    n_neighbours=4,
#    rand_rest_p=0.1,
#    n_iter_restart=20,
#  )

#  optimizer = ParticleSwarmOptimizer(
#    inertia=0.4,
#    cognitive_weight=0.7,
#    social_weight=0.7,
#    temp_weight=0.3,
#    rand_rest_p=0.05,
#  )

#  optimizer = EvolutionStrategyOptimizer(
#    mutation_rate=0.5, crossover_rate=0.5, rand_rest_p=0.05
#  )

  hyper = Hyperactive()
  hyper.add_search(pnreval, space, optimizer=optimizer, n_iter=1000, n_jobs=8)
  hyper.run()


if __name__ == "__main__":
  main()
