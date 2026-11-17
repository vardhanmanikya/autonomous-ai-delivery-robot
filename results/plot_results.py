import csv
import matplotlib.pyplot as plt


# ============================================================
# READ RESULTS
# ============================================================

file_path = "results/performance_results.csv"

scenarios = []
initial_paths = []
final_paths = []
replanning_events = []
planning_times = []


with open(file_path, "r") as file:

    reader = csv.DictReader(file)

    for row in reader:

        scenarios.append(row["Scenario"])

        initial_paths.append(
            int(row["Initial_Path_Length"])
        )

        final_paths.append(
            int(row["Final_Path_Length"])
        )

        replanning_events.append(
            int(row["Replanning_Events"])
        )

        planning_times.append(
            float(row["Planning_Time_ms"])
        )


# ============================================================
# GRAPH 1
# INITIAL VS FINAL PATH LENGTH
# ============================================================

plt.figure(figsize=(9, 5))

plt.plot(
    scenarios,
    initial_paths,
    marker="o",
    label="Initial Path"
)

plt.plot(
    scenarios,
    final_paths,
    marker="o",
    label="Final Path"
)

plt.title("Initial vs Final Path Length")

plt.xlabel("Scenario")

plt.ylabel("Path Length (steps)")

plt.grid(True)

plt.legend()

plt.xticks(
    rotation=15
)

plt.tight_layout()

plt.savefig(
    "results/path_length_comparison.png",
    dpi=300
)

plt.show()


# ============================================================
# GRAPH 2
# RE-PLANNING EVENTS
# ============================================================

plt.figure(figsize=(9, 5))

plt.bar(
    scenarios,
    replanning_events
)

plt.title("A* Re-planning Events")

plt.xlabel("Scenario")

plt.ylabel("Number of Re-planning Events")

plt.grid(
    axis="y"
)

plt.xticks(
    rotation=15
)

plt.tight_layout()

plt.savefig(
    "results/replanning_events.png",
    dpi=300
)

plt.show()


# ============================================================
# GRAPH 3
# PLANNING TIME
# ============================================================

plt.figure(figsize=(9, 5))

plt.plot(
    scenarios,
    planning_times,
    marker="o"
)

plt.title("A* Planning Time")

plt.xlabel("Scenario")

plt.ylabel("Planning Time (ms)")

plt.grid(True)

plt.xticks(
    rotation=15
)

plt.tight_layout()

plt.savefig(
    "results/planning_time.png",
    dpi=300
)

plt.show()


print("\n==============================================")
print("       RESULT GRAPHS GENERATED")
print("==============================================")

print("\nFiles created:")

print(
    "1. results/path_length_comparison.png"
)

print(
    "2. results/replanning_events.png"
)

print(
    "3. results/planning_time.png"
)