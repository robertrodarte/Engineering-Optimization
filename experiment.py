import csv
import math
import re
import time

from pulp import PULP_CBC_CMD, LpSolution, LpStatus, value

from instance import generate_instance
from model import build_model

# Define task size instances to run
SIZES = [5, 10, 15, 20, 25]
# Define how many seeds to run on each task size
SEEDS = [0, 1, 2]
# Max time limit an instance can run before being considered not optimal.
TIME_LIMIT_SEC = 120

# Define log paths
LOG_PATH = "cbc_log.txt"
OUTPUT_CSV = "experiment_results.csv"

# Used for parsing node count
NODE_RE = re.compile(r"Enumerated nodes:\s*(\d+)")

def parse_node_count(log_path):
    """
    Helper to parse node count from CBC text log

    :param log_path: Path to CBC log
    :return: Parsed node count
    """
    with open(log_path) as f:
        text = f.read()
    match = NODE_RE.search(text)
    return int(match.group(1)) if match else None


def cores_for(n_tasks, tasks_per_core=5, min_cores=2):
    """
    Core count scales with task count so lakc of cores isn't
    causing infeasibility as n_tasks grows

    :param n_tasks: Number of tasks
    :param tasks_per_core: How many tasks to assign per core
    :param min_cores: How many cores to start at
    :return: Number of cores to use for `n_tasks` tasks
    """
    return max(min_cores, math.ceil(n_tasks / tasks_per_core))


def run_once(instance, cuts):
    """
    Solve an instance once with cuts on or off.

    :param instance: Instance to run
    :param cuts: True if branch-and-cut, False if branch-and-bound
    :return: Dictionary of results
    """
    # Build the model to run
    model, _, _, _ = build_model(instance)
    # Run the model using CBC solver to configure specific settings
    solver = PULP_CBC_CMD(msg=False, cuts=cuts, timeLimit=TIME_LIMIT_SEC, logPath=LOG_PATH)

    # Begin tracking time
    t0 = time.perf_counter()
    # Solve the model using the configured settings
    model.solve(solver)
    # Stop tracking time
    elapsed = time.perf_counter() - t0

    # model.status only has 5 coarse buckets - CBC's PuLP parser relabels
    # a time-limit stop with a feasible incumbent as LpStatusOptimal, not
    # "Not Solved". model.sol_status is the only field that separates a
    # proven optimum (LpSolutionOptimal) from a time-capped guess
    # (LpSolutionIntegerFeasible), so both get recorded.
    status = LpStatus[model.status]
    sol_status = LpSolution[model.sol_status]
    return {
        "status": status,
        "sol_status": sol_status,
        "objective": value(model.objective),
        "nodes": parse_node_count(LOG_PATH),
        "time_sec": elapsed,
    }


def main():
    """
    Entry point for experiment
    """
    rows = []
    # Loop through all sizes defined
    for n_tasks in SIZES:
        n_cores = cores_for(n_tasks)
        # Run the instance for each seed
        for seed in SEEDS:
            # Create the instance
            instance = generate_instance(n_tasks=n_tasks, n_cores=n_cores, seed=seed)
            # Run on both branch-and-cut and branch-and-bound
            for cuts in (False, True):
                # Run the model, store the results, and print
                result = run_once(instance, cuts)
                row = {
                    "n_tasks": n_tasks,
                    "n_cores": n_cores,
                    "seed": seed,
                    "method": "branch_and_cut" if cuts else "branch_and_bound",
                    **result,
                }
                rows.append(row)
                print(f"n_tasks={n_tasks} seed={seed} method={row['method']:15s} "
                      f"status={row['status']:10s} sol_status={row['sol_status']:24s} "
                      f"nodes={row['nodes']} time={row['time_sec']:.3f}s")

    # Write a CSV file with all the results
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResults written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
