from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value

tasks = ['T1', 'T2', 'T3', 'T4']
cores = ['C1', 'C2']
processing_time = {'T1': 3, 'T2': 2, 'T3': 4, 'T4': 2}
deadline = {'T1': 10, 'T2': 8, 'T3': 15, 'T4': 6}

model = LpProblem("Task_Scheduling_MultiCore", LpMinimize)

# Initialize start time to 0 for each task
start = {t: LpVariable(f"start_{t}", lowBound=0) for t in tasks}

# Binary assignment (x[t,c] = 1 if task t assigned to core c)
x = {(t, c): LpVariable(f"x_{t}_{c}", cat="Binary") for t in tasks for c in cores}

# Objective as minimize total completion time
model += lpSum(start[t] + processing_time[t] for t in tasks)

# Assignment constraint
for t in tasks:
    model += lpSum(x[t, c] for c in cores) == 1

# Deadline constraint
for t in tasks:
    model += start[t] + processing_time[t] <= deadline[t]

# Precedence constraint
model += start['T2'] >= start['T1'] + processing_time['T1']

model.solve()
print("Status:", LpStatus[model.status])
for t in tasks:
    assigned_core = [c for c in cores if value(x[t, c]) == 1][0]
    print(f"{t}: core = {assigned_core}, start = {value(start[t])}, finish = {value(start[t]) + processing_time[t]}")
print("Objective (total completion time):", value(model.objective))