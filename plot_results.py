import csv
import os
from collections import defaultdict

import matplotlib.pyplot as plt

# Define plot variables
CSV_PATH = "experiment_results.csv"
FIG_DIR = "figures"
# Matches solve time cutoff (experiments.py)
TIME_LIMIT_SEC = 120  

# Plot customization
# branch_and_bound
BLUE = "#2a78d6"  
# branch_and_cut  
ORANGE = "#eb6834"  
INK = "#0b0b0b"
SECONDARY_INK = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"

METHOD_COLOR = {"branch_and_bound": BLUE, "branch_and_cut": ORANGE}
METHOD_LABEL = {
    "branch_and_bound": "branch_and_bound (cuts off)",
    "branch_and_cut": "branch_and_cut (cuts on)",
}


def load_rows():
    """
    Load each row from the csv file
    """
    with open(CSV_PATH, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["n_tasks"] = int(r["n_tasks"])
        r["seed"] = int(r["seed"])
        r["nodes"] = int(r["nodes"]) if r["nodes"] not in (None, "", "None") else None
        r["time_sec"] = float(r["time_sec"])
    return rows


def proven_pairs(rows):
    """
    Returns the pairs that actually found optimal solutions
    since that is what we want to compare
    """
    by_key = defaultdict(dict)
    for r in rows:
        by_key[(r["n_tasks"], r["seed"])][r["method"]] = r

    pairs = []
    # Look at the row and append only results where sol_status is found for both
    for (n_tasks, seed), methods in sorted(by_key.items()):
        bb, bc = methods.get("branch_and_bound"), methods.get("branch_and_cut")
        if (
            bb and bc
            and bb["sol_status"] == "Optimal Solution Found"
            and bc["sol_status"] == "Optimal Solution Found"
        ):
            pairs.append((n_tasks, seed, bb, bc))

    # Return the proven pairs
    return pairs


def style_axes(ax):
    """
    Styles the plots axes
    """
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(AXIS)
    ax.spines["bottom"].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(SECONDARY_INK)
    ax.yaxis.label.set_color(SECONDARY_INK)


def legend_handles():
    """
    Styles the legends    
    """
    return [
        plt.Line2D([0], [0], marker="o", linestyle="none", markerfacecolor=BLUE,
                   markeredgecolor=BLUE, markersize=7, label=METHOD_LABEL["branch_and_bound"]),
        plt.Line2D([0], [0], marker="o", linestyle="none", markerfacecolor=ORANGE,
                   markeredgecolor=ORANGE, markersize=7, label=METHOD_LABEL["branch_and_cut"]),
    ]


def dumbbell_plot(pairs, all_sizes, value_key, ylabel, title, out_path,
                   symlog_thresh=None):
    """
    Sets up the dumbbell plot for BB and BC comparison
    """
    fig, ax = plt.subplots(figsize=(7.5, 5), facecolor=SURFACE)
    style_axes(ax)

    seeds_by_size = defaultdict(list)
    for n_tasks, seed, _, _ in pairs:
        seeds_by_size[n_tasks].append(seed)

    for n_tasks, seed, bb, bc in pairs:
        seeds_here = sorted(seeds_by_size[n_tasks])
        idx = seeds_here.index(seed)
        offset = (idx - (len(seeds_here) - 1) / 2) * 0.6
        x = n_tasks + offset
        bb_v, bc_v = bb[value_key], bc[value_key]
        ax.plot([x, x], [bb_v, bc_v], color=MUTED, linewidth=1, zorder=1)
        ax.plot(x, bb_v, "o", color=BLUE, markersize=7, zorder=2)
        ax.plot(x, bc_v, "o", color=ORANGE, markersize=7, zorder=2)

    if symlog_thresh is not None:
        ax.set_yscale("symlog", linthresh=symlog_thresh)

    ax.set_xticks(all_sizes)
    ax.set_xlim(min(all_sizes) - 3, max(all_sizes) + 3)
    ax.set_xlabel("Number of tasks")
    ax.set_ylabel(ylabel)
    ax.set_title(title, color=INK, fontsize=12, loc="left", pad=38)
    ax.legend(handles=legend_handles(), loc="lower left", bbox_to_anchor=(0, 1.01, 1, 0.1),
              ncol=2, frameon=False, fontsize=9, labelcolor=SECONDARY_INK)

    missing = sorted(set(all_sizes) - set(seeds_by_size.keys()))
    if missing:
        note = ("Sizes with no bar: neither method proved optimality within "
                f"{TIME_LIMIT_SEC}s for any seed (n = {', '.join(str(m) for m in missing)})")
        fig.text(0.02, 0.01, note, fontsize=8, color=MUTED)

    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out_path, dpi=200, facecolor=SURFACE)
    plt.close(fig)


def solved_rate_plot(rows, out_path):
    """
    Puts together a plot to compare solved rate
    """
    sizes = sorted(set(r["n_tasks"] for r in rows))
    seeds_per_size = defaultdict(set)
    for r in rows:
        seeds_per_size[r["n_tasks"]].add(r["seed"])

    counts = {m: [] for m in METHOD_COLOR}
    for n_tasks in sizes:
        for m in counts:
            n_proven = sum(
                1 for r in rows
                if r["n_tasks"] == n_tasks and r["method"] == m
                and r["sol_status"] == "Optimal Solution Found"
            )
            counts[m].append(n_proven)

    fig, ax = plt.subplots(figsize=(7.5, 4.5), facecolor=SURFACE)
    style_axes(ax)

    x = range(len(sizes))
    width = 0.32
    bars = {
        m: ax.bar([i + (width / 2 if m == "branch_and_cut" else -width / 2) for i in x],
                   counts[m], width, color=METHOD_COLOR[m], label=METHOD_LABEL[m], zorder=2)
        for m in counts
    }
    for method_bars in bars.values():
        for b in method_bars:
            h = b.get_height()
            ax.annotate(str(int(h)), (b.get_x() + b.get_width() / 2, h),
                        textcoords="offset points", xytext=(0, 3), ha="center",
                        fontsize=9, color=SECONDARY_INK)

    max_seeds = max(len(s) for s in seeds_per_size.values())
    ax.set_xticks(list(x))
    ax.set_xticklabels([str(s) for s in sizes])
    ax.set_ylim(0, max_seeds + 0.6)
    ax.set_yticks(range(max_seeds + 1))
    ax.set_xlabel("Number of tasks")
    ax.set_ylabel(f"Seeds proven optimal (of {max_seeds}, {TIME_LIMIT_SEC}s cap)")
    ax.set_title("Solved-to-optimality rate by instance size", color=INK,
                 fontsize=12, loc="left", pad=12)
    ax.legend(loc="upper right", frameon=False, fontsize=9, labelcolor=SECONDARY_INK)

    fig.tight_layout()
    fig.savefig(out_path, dpi=200, facecolor=SURFACE)
    plt.close(fig)


def main():
    rows = load_rows()
    pairs = proven_pairs(rows)
    all_sizes = sorted(set(r["n_tasks"] for r in rows))

    os.makedirs(FIG_DIR, exist_ok=True)

    dumbbell_plot(
        pairs, all_sizes, "nodes", "Nodes explored (symlog scale)",
        "Nodes explored: branch_and_bound vs. branch_and_cut\n"
        "(instances both methods proved optimal)",
        os.path.join(FIG_DIR, "nodes_vs_size.png"),
        symlog_thresh=5,
    )
    dumbbell_plot(
        pairs, all_sizes, "time_sec", "Solve time, seconds (symlog scale)",
        "Solve time: branch_and_bound vs. branch_and_cut\n"
        "(instances both methods proved optimal)",
        os.path.join(FIG_DIR, "time_vs_size.png"),
        symlog_thresh=0.05,
    )
    solved_rate_plot(rows, os.path.join(FIG_DIR, "solved_rate.png"))

    print(f"Wrote figures to {FIG_DIR}/")


if __name__ == "__main__":
    main()
