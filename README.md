# Real-Time Task Scheduling MILP: Branch-and-Bound vs. Branch-and-Cut

EE 603 – Engineering Optimization

Tests whether branch-and-cut (Gomory mixed-integer cuts) offers a meaningful
solve-time / node-count advantage over plain branch-and-bound on real-time
task scheduling MILP instances.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install pulp matplotlib
```

## Commands

**Sanity check** — solves the hand-verified instance
with default solver settings and prints the schedule:

```bash
python multi_core.py
```

**Run the branch-and-bound vs. branch-and-cut sweep** — solves instances at
`n_tasks = 5, 10, 15, 20, 25` (3 random seeds each, cores scaled via
`cores_for()`), once with CBC cuts off and once with cuts on, each capped at
120s. Writes per-run status/node-count/solve-time to `experiment_results.csv`
and the CBC solver log to `cbc_log.txt`:

```bash
python experiment.py
```

**Generate comparison figures** — reads `experiment_results.csv` and writes
`nodes_vs_size.png`, `time_vs_size.png`, and `solved_rate.png` to `figures/`:

```bash
python plot_results.py
```

Run the three in order (`experiment.py` before `plot_results.py`) after any
change to `instance.py`, `model.py`, or the sweep parameters in `experiment.py`,
since the figures are generated from `experiment_results.csv` and won't
update themselves.

## Notes

- `single_core.py` is the original single-core LP prototype, superseded by
  the multi-core model but kept as-is.
