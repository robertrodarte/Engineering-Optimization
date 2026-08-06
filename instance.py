import math
import random
from dataclasses import dataclass, field


@dataclass
class Instance:
    """
    Used to create generated instances for model
    """
    tasks: list
    cores: list
    processing_time: dict   
    deadline: dict          
    memory: dict            
    ram_capacity: dict      
    precedence: dict = field(default_factory=dict) 


def hand_verified_instance():
    """
    Hard coded instance to check by hand
    Used in preliminary report
    """
    return Instance(
        tasks=['T1', 'T2', 'T3', 'T4'],
        cores=['C1', 'C2'],
        processing_time={'T1': 3, 'T2': 2, 'T3': 4, 'T4': 2},
        deadline={'T1': 10, 'T2': 8, 'T3': 15, 'T4': 6},
        memory={'T1': 4, 'T2': 3, 'T3': 5, 'T4': 2},
        ram_capacity={'C1': 6, 'C2': 8},
        precedence={'T2': ['T1']},
    )


def generate_instance(n_tasks, n_cores=2, seed=None, p_range=(1, 5),
                       mem_range=(1, 5), precedence_prob=0.3,
                       deadline_slack=(1.2, 2.0), ram_slack=1.3):
    """
    Generates random (not guaranteed) feasible instances

    :param n_tasks: Number of tasks
    :param n_cores: Number of cores
    :param seed: Seed to use for rng
    :param p_range: Range to generate processing time
    :param mem_range: Range to generate memory size
    :param precedence_prob: Probability to assign precedence
    :param deadline_slack: Used to create slack in deadline vars
    :param ram_slack: Used to create slack in ram vars
    :return: A random instance.
    """
    rng = random.Random(seed)

    # Set tasks and cores
    tasks = [f'T{i + 1}' for i in range(n_tasks)]
    cores = [f'C{j + 1}' for j in range(n_cores)]

    # Generate processing time and memory variables for each task
    processing_time = {t: rng.randint(*p_range) for t in tasks}
    memory = {t: rng.randint(*mem_range) for t in tasks}

    # Generate precedence values for each task
    precedence = {}
    for idx, t in enumerate(tasks):
        preds = [tasks[j] for j in range(idx) if rng.random() < precedence_prob]
        if preds:
            precedence[t] = preds

    # Set deadline values for each task
    # Slack is introduced to reduce the risk
    # of generating an infeasible instance
    deadline = {}
    earliest_finish = {}
    for t in tasks:
        preds = precedence.get(t, [])
        earliest_start = max((earliest_finish[p] for p in preds), default=0)
        earliest_finish[t] = earliest_start + processing_time[t]
        slack = rng.uniform(*deadline_slack)
        deadline[t] = math.ceil(earliest_finish[t] * slack)

    # Set RAM variables for each CORE
    total_memory = sum(memory.values())
    ram_capacity = {c: math.ceil(total_memory / n_cores * ram_slack) for c in cores}

    # Return the instance to use for the model
    return Instance(tasks, cores, processing_time, deadline, memory,
                     ram_capacity, precedence)
