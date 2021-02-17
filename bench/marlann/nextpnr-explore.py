#!/usr/bin/python

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
