from itertools import combinations

from pulp import LpProblem, LpMinimize, LpVariable, LpStatus, lpSum, value


def build_model(instance):
    """
    Build the MILP for a given Instance. 
    
    :param instance: Generated instance
    :return: (model, x, start, y).
    """
    # Set variables
    tasks, cores = instance.tasks, instance.cores
    p, d = instance.processing_time, instance.deadline
    mem, ram = instance.memory, instance.ram_capacity

    # Create model
    model = LpProblem("Task_Scheduling_MultiCore", LpMinimize)

    # Create model variables
    start = {t: LpVariable(f"start_{t}", lowBound=0) for t in tasks}
    x = {(t, c): LpVariable(f"x_{t}_{c}", cat="Binary") for t in tasks for c in cores}
    y = {(i, k): LpVariable(f"y_{i}_{k}", cat="Binary") for i, k in combinations(tasks, 2)}

    # Objective function: minimize sum(start_i + p_i)
    model += lpSum(start[t] + p[t] for t in tasks)

    # Assignment constraint
    for t in tasks:
        model += lpSum(x[t, c] for c in cores) == 1

    # Memory constraint
    for c in cores:
        model += lpSum(x[t, c] * mem[t] for t in tasks) <= ram[c]

    # Deadline constraint
    for t in tasks:
        model += start[t] + p[t] <= d[t]

    # Precedence constraint
    for t in tasks:
        for pred in instance.precedence.get(t, []):
            model += start[t] >= start[pred] + p[pred]

    # Same-core overlap constraint
    # M is used to "deactivate" a constraint
    M = max(d.values())
    # For each combination, apply same-core overlap constraints
    for i, k in combinations(tasks, 2):
        for c in cores:
            # M * (1 - y[i, k]) and y = 1: Allow T_i to go first
            # M * (1 - y[i, k]) and y = 0: Allow T_k to go first
            # M * (2 - x[i, c] - x[k, c]): If 0, tasks share the same CORE, otherwise constraint not applied.
            model += start[k] >= start[i] + p[i] - M * (1 - y[i, k]) - M * (2 - x[i, c] - x[k, c])
            model += start[i] >= start[k] + p[k] - M * y[i, k] - M * (2 - x[i, c] - x[k, c])

    return model, x, start, y


def report(model, instance, x, start):
    """
    Print model results.

    :param model: Model to use for results
    :param instance: Instance used with model
    :param x: Binary assignment decision variables used with model
    :param start: Continuous start time variables used with model
    :return: None
    """
    print("Status:", LpStatus[model.status])
    for t in instance.tasks:
        assigned_core = [c for c in instance.cores if value(x[t, c]) == 1][0]
        finish = value(start[t]) + instance.processing_time[t]
        print(f"{t}: core = {assigned_core}, start = {value(start[t])}, finish = {finish}")
    print("Objective (total completion time):", value(model.objective))
