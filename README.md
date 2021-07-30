
# An effort to test various annealers for nextpnr

---

## NextPNR hyperparam optimization

Running the tunner is simple, just prepend one:
![MANGO](https://github.com/cbalint13/nextpnr-anneal/raw/master/images/tunning-pnr.gif)

* The goal of tunner is to significantly shorten the time to explore the best parameters given a configuration [space](https://github.com/cbalint13/nextpnr-anneal/blob/master/bench/marlann/nextpnr-explore.py#L60-L63).
* The tunner will **find near the best one** in orders of magnitude shorter time compared to exhaustive brute force.
  
Available annelars for nextpnr are in ```tunners```:

  | Tunner | MultiAlgo | Parallel |
  |-----------------------------------------------------------|---|---|
  | [Mango](https://github.com/ARM-software/mango)            | N | Y |
  | [HyperActive](https://github.com/SimonBlanke/Hyperactive) | Y | N |
  | [Optuna](https://github.com/optuna/optuna)                | Y | N |
  | [HyperOpt](https://github.com/hyperopt/hyperopt)          | Y | N |


## The brute force experiment

Given a configuration [space](https://github.com/cbalint13/nextpnr-anneal/blob/master/bench/marlann/nextpnr-explore.py#L60-L63) expensive but complete brute force exploration can be done:
  
  * ```0-explore-brute.sh``` will explore the space (will take some time)
  * ```1-parse-results.sh``` will aggregate log results into a JSON file
  * ```2-graph-results.sh``` will display histogram occurences of yielded clock speeds
 
| Experiment | Image1 | Image2 |
| ---------- | ------ | ------ |
| MARLANN    |<img src="images/marlann-graph.png" width="500" height="300">Default: 28.21 Mhz|<img src="images/marlann-graph-spiclk.png" width="500" height="300">Default: 96.79 Mhz|
| PicoRV32   |<img src="images/picorv32-graph.png" width="500" height="300">Default: 89.79 Mhz||



## Future goal (WiP)

Given parameter space:

  * track early features extracted from several nexpnr startups
  * encode early features in metric measurable feature vectors
  * generate a cost model (xgboost) in TVM [autotune](https://github.com/apache/tvm/issues/1311) fashion
  * try fit/estimate/predict out from learned model the best set
