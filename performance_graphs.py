import matplotlib.pyplot as plt


# Experimental results
tests = [
    "No Dynamic\nObstacle",
    "One Dynamic\nObstacle",
    "Multiple Dynamic\nObstacles"
]

initial_path = [14, 14, 14]
final_path = [14, 14, 14]

replans = [0, 1, 2]

planning_time = [
    0.278,
    0.436,
    0.628
]


# ============================================================
# GRAPH 1 — PATH LENGTH
# ============================================================

plt.figure(figsize=(8, 5))

x = range(len(tests))

plt.plot(
    x,
    initial_path,
    marker="o",
    label="Initial Path"
)

plt.plot(
    x,
    final_path,
    marker="o",
    label="Final Path"
)

plt.xticks(
    x,
    tests
)

plt.ylabel("Path Length (steps)")
plt.title("Initial vs Final Path Length")

plt.grid(True)

plt.legend()

plt.tight_layout()

plt.show()


# ============================================================
# GRAPH 2 — RE-PLANNING EVENTS
# ============================================================

plt.figure(figsize=(8, 5))

plt.bar(
    tests,
    replans
)

plt.ylabel("Number of Re-planning Events")
plt.title("A* Re-planning Events")

plt.grid(
    axis="y"
)

plt.tight_layout()

plt.show()


# ============================================================
# GRAPH 3 — PLANNING TIME
# ============================================================

plt.figure(figsize=(8, 5))

plt.plot(
    x,
    planning_time,
    marker="o"
)

plt.xticks(
    x,
    tests
)

plt.ylabel("Planning Time (ms)")
plt.title("A* Planning Time")

plt.grid(True)

plt.tight_layout()

plt.show()