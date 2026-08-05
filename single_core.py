from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, value

tasks = ['T1', 'T2', 'T3']
processing_time = {'T1': 3, 'T2': 2, 'T3': 4}
deadline = {'T1': 10, 'T2': 8, 'T3': 15}

model = LpProblem("Task_Scheduling", LpMinimize)

# Initialize start time to 0 for each task
start = {t: LpVariable(f"start_{t}", lowBound=0) for t in tasks}

# Objective as minimize total completion time
model += lpSum(start[t] + processing_time[t] for t in tasks)

# Deadline constraint
for t in tasks:
    model += start[t] + processing_time[t] <= deadline[t]

# Precedence constraint
model += start['T2'] >= start['T1'] + processing_time['T1']

model.solve()
print("Status:", LpStatus[model.status])
for t in tasks:
    print(f"{t}: start = {value(start[t])}, finish = {value(start[t]) + processing_time[t]}")
print("Objective (total completion time):", value(model.objective))