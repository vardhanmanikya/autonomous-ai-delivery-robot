import csv
import matplotlib.pyplot as plt


# ============================================================
# READ RESULTS
# ============================================================

file_path = "results/repeated_performance_results.csv"

scenarios = []
planning_times = []
replanning_events = []
success_rates = []

with open(file_path, "r") as file:

    reader = csv.DictReader(file)

    for row in reader:

        scenarios.append(
            row["Scenario"]
        )

        planning_times.append(
            float(
                row["Average_Planning_Time_ms"]
            )
        )

        replanning_events.append(
            float(
                row["Average_Replanning_Events"]
            )
        )

        success_rates.append(
            float(
                row["Success_Rate_Percent"]
            )
        )


# ============================================================
# GRAPH 1 - PLANNING TIME
# ============================================================

plt.figure(figsize=(9, 6))

plt.bar(
    scenarios,
    planning_times
)

plt.title(
    "Average A* Planning Time"
)

plt.xlabel(
    "Scenario"
)

plt.ylabel(
    "Planning Time (ms)"
)

plt.xticks(
    rotation=10
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "results/repeated_planning_time.png",
    dpi=300
)

plt.show()


# ============================================================
# GRAPH 2 - RE-PLANNING EVENTS
# ============================================================

plt.figure(figsize=(9, 6))

plt.bar(
    scenarios,
    replanning_events
)

plt.title(
    "Average A* Re-planning Events"
)

plt.xlabel(
    "Scenario"
)

plt.ylabel(
    "Number of Re-planning Events"
)

plt.xticks(
    rotation=10
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "results/repeated_replanning_events.png",
    dpi=300
)

plt.show()


# ============================================================
# GRAPH 3 - SUCCESS RATE
# ============================================================

plt.figure(figsize=(9, 6))

plt.bar(
    scenarios,
    success_rates
)

plt.title(
    "Robot Delivery Success Rate"
)

plt.xlabel(
    "Scenario"
)

plt.ylabel(
    "Success Rate (%)"
)

plt.ylim(
    0,
    110
)

plt.xticks(
    rotation=10
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "results/repeated_success_rate.png",
    dpi=300
)

plt.show()


# ============================================================
# COMPLETION MESSAGE
# ============================================================

print()
print("==============================================")
print("   REPEATED RESULT GRAPHS GENERATED")
print("==============================================")

print()
print("Files created:")

print(
    "1. results/repeated_planning_time.png"
)

print(
    "2. results/repeated_replanning_events.png"
)

print(
    "3. results/repeated_success_rate.png"
)