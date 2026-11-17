
"""Side-by-side autonomous delivery simulations for three obstacle scenarios."""

import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_FILE = os.path.join(APP_DIR, "main.py")

POLL_INTERVAL_MS = 150
GRID_SIZE = 10
CELL_SIZE = 31
GRID_START_X = 29
GRID_START_Y = 8

SCENARIOS = (
    ("none", "NO DYNAMIC OBSTACLE", 0),
    ("one", "ONE DYNAMIC OBSTACLE", 1),
    ("multiple", "MULTIPLE DYNAMIC OBSTACLES", "2–6"),
)

STATIC_OBSTACLES = (
    {(row, 4) for row in range(3, 7)}
    | {(6, col) for col in range(4, 8)}
)

DESTINATION = (8, 8)

# --------------------------------------------------
# MAIN WINDOW
# --------------------------------------------------

root = tk.Tk()
root.title("Autonomous AI Delivery Robot — Scenario Comparison")
root.geometry("1300x790")
root.minsize(1120, 720)
root.configure(bg="#eef2f6")

tk.Label(
    root,
    text="AUTONOMOUS AI DELIVERY ROBOT",
    bg="#eef2f6",
    font=("Arial", 21, "bold")
).pack(pady=(13, 2))

tk.Label(
    root,
    text="Live comparison · three independent 10×10 simulations",
    bg="#eef2f6",
    fg="#465568",
    font=("Arial", 11)
).pack(pady=(0, 10))

cards = tk.Frame(root, bg="#eef2f6")
cards.pack(fill="both", expand=True, padx=14, pady=4)

panels = {}
workers = {}

# --------------------------------------------------
# CREATE THREE PANELS
# --------------------------------------------------

def make_panel(parent, key, title, target):

    box = tk.LabelFrame(
        parent,
        text=title,
        font=("Arial", 11, "bold"),
        bg="white",
        padx=8,
        pady=8,
        labelanchor="n"
    )

    box.pack(
        side="left",
        fill="both",
        expand=True,
        padx=6
    )

    canvas = tk.Canvas(
        box,
        width=GRID_SIZE * CELL_SIZE + 60,
        height=GRID_SIZE * CELL_SIZE + 38,
        bg="white",
        highlightthickness=0
    )

    canvas.pack(pady=(3, 5))

    detail = tk.Label(
        box,
        text="Waiting to start",
        bg="white",
        fg="#263445",
        font=("Arial", 9),
        justify="left",
        anchor="w",
        wraplength=335
    )

    detail.pack(fill="x", padx=4, pady=4)

    panels[key] = {
        "canvas": canvas,
        "detail": detail,
        "target": target,
        "status_file": os.path.join(
            APP_DIR,
            f"status_{key}.json"
        ),
        "last_status": {}
    }

    return box


for key, title, target in SCENARIOS:
    make_panel(cards, key, title, target)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

footer = tk.Frame(root, bg="#eef2f6")

footer.pack(
    fill="x",
    padx=22,
    pady=(3, 12)
)

hint = tk.Label(
    footer,
    text="Each panel runs its own robot, route planner, obstacle set, and status channel.",
    bg="#eef2f6",
    fg="#465568",
    font=("Arial", 9)
)

hint.pack(side="left")

run_label = tk.Label(
    footer,
    text="Ready",
    bg="#eef2f6",
    font=("Arial", 10, "bold")
)

run_label.pack(side="right", padx=12)


# --------------------------------------------------
# DRAW GRID
# --------------------------------------------------

def draw_grid(canvas, status):

    canvas.delete("all")

    # Draw grid and static obstacles
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):

            x1 = GRID_START_X + col * CELL_SIZE
            y1 = GRID_START_Y + row * CELL_SIZE

            fill = (
                "#263445"
                if (row, col) in STATIC_OBSTACLES
                else "#f8fafc"
            )

            canvas.create_rectangle(
                x1,
                y1,
                x1 + CELL_SIZE,
                y1 + CELL_SIZE,
                fill=fill,
                outline="#cbd5e1"
            )

    # Draw robot route
    path = status.get("path", [])

    if isinstance(path, list) and len(path) > 1:

        coords = []

        for point in path:

            if not isinstance(point, (list, tuple)):
                continue

            if len(point) != 2:
                continue

            row, col = point

            if (
                isinstance(row, int)
                and isinstance(col, int)
                and 0 <= row < GRID_SIZE
                and 0 <= col < GRID_SIZE
            ):

                coords.extend((
                    GRID_START_X + col * CELL_SIZE + CELL_SIZE / 2,
                    GRID_START_Y + row * CELL_SIZE + CELL_SIZE / 2
                ))

        if len(coords) >= 4:

            canvas.create_line(
                *coords,
                fill="#45a668",
                width=3,
                arrow="last"
            )

    # Draw dynamic obstacles
    if status.get("dynamic_obstacle_visible", False):

        obstacles = status.get("dynamic_obstacles", [])

        if not obstacles and status.get("dynamic_obstacle"):
            obstacles = [status["dynamic_obstacle"]]

        for point in obstacles:

            if not isinstance(point, (list, tuple)):
                continue

            if len(point) != 2:
                continue

            row, col = point

            if (
                not isinstance(row, int)
                or not isinstance(col, int)
                or not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE)
            ):
                continue

            x1 = GRID_START_X + col * CELL_SIZE
            y1 = GRID_START_Y + row * CELL_SIZE

            canvas.create_rectangle(
                x1 + 3,
                y1 + 3,
                x1 + CELL_SIZE - 3,
                y1 + CELL_SIZE - 3,
                fill="#fff1da",
                outline="#ed8a19",
                width=2
            )

            canvas.create_line(
                x1 + 7,
                y1 + 7,
                x1 + CELL_SIZE - 7,
                y1 + CELL_SIZE - 7,
                fill="#df6b12",
                width=2
            )

            canvas.create_line(
                x1 + CELL_SIZE - 7,
                y1 + 7,
                x1 + 7,
                y1 + CELL_SIZE - 7,
                fill="#df6b12",
                width=2
            )

    # Draw destination
    row, col = DESTINATION

    cx = GRID_START_X + col * CELL_SIZE + CELL_SIZE / 2
    cy = GRID_START_Y + row * CELL_SIZE + CELL_SIZE / 2

    canvas.create_text(
        cx,
        cy,
        text="★",
        font=("Arial", 18, "bold"),
        fill="#d83232"
    )

    # Draw robot
    position = status.get("robot_position", [1, 1])

    if isinstance(position, (list, tuple)) and len(position) == 2:

        row, col = position

        if (
            isinstance(row, int)
            and isinstance(col, int)
            and 0 <= row < GRID_SIZE
            and 0 <= col < GRID_SIZE
        ):

            cx = GRID_START_X + col * CELL_SIZE + CELL_SIZE / 2
            cy = GRID_START_Y + row * CELL_SIZE + CELL_SIZE / 2

            canvas.create_oval(
                cx - 10,
                cy - 10,
                cx + 10,
                cy + 10,
                fill="#2474d2",
                outline="#154a91",
                width=2
            )

            canvas.create_text(
                cx,
                cy,
                text="R",
                fill="white",
                font=("Arial", 8, "bold")
            )


# --------------------------------------------------
# READ STATUS FILES
# --------------------------------------------------

def read_status():

    active = 0

    for key, panel in panels.items():

        status = panel["last_status"]

        try:

            with open(
                panel["status_file"],
                "r",
                encoding="utf-8"
            ) as file:

                loaded_status = json.load(file)

            if isinstance(loaded_status, dict):

                status = loaded_status
                panel["last_status"] = loaded_status

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError
        ):

            process = workers.get(key)

            if process is not None and process.poll() is not None:

                panel["detail"].config(
                    text=(
                        f"WORKER EXITED: {process.returncode}\n"
                        "Last known position retained."
                    )
                )

                draw_grid(panel["canvas"], status)
                continue

        obstacle_count = status.get(
            "dynamic_obstacle_count",
            len(status.get("dynamic_obstacles", []))
        )

        delivery = status.get(
            "delivery_status",
            "NOT STARTED"
        )

        if delivery == "IN PROGRESS":
            active += 1

        position = status.get(
            "robot_position",
            [1, 1]
        )

        if isinstance(position, (list, tuple)) and len(position) == 2:
            position_text = f"({position[0]}, {position[1]})"
        else:
            position_text = "—"

        panel["detail"].config(
            text=(
                f"Robot: {status.get('robot_status', 'IDLE')}    "
                f"Delivery: {delivery}\n"

                f"Position: {position_text}    "
                f"Dynamic obstacles: {obstacle_count} / {panel['target']}\n"

                f"Re-plans: {status.get('replanning_events', 0)}    "
                f"A*: {status.get('astar_status', 'READY')}\n"

                f"Route: {status.get('shortest_route_steps', '—')} "
                f"steps shortest · "
                f"{status.get('alternative_route_steps', '—')} alternative\n"

                f"Route update: {status.get('route_alert', 'None')}"
            )
        )

        draw_grid(panel["canvas"], status)

    running_processes = [
        process
        for process in workers.values()
        if process.poll() is None
    ]

    if workers and not running_processes:

        run_label.config(text="All scenarios finished")

    elif running_processes:

        run_label.config(
            text=f"Running · {active} scenario(s) moving"
        )

    root.after(POLL_INTERVAL_MS, read_status)


# --------------------------------------------------
# START ALL THREE SIMULATIONS
# --------------------------------------------------

def start_comparison():

    global workers

    if any(
        process.poll() is None
        for process in workers.values()
    ):

        run_label.config(text="Comparison is already running")
        return

    if not os.path.isfile(MAIN_FILE):

        run_label.config(
            text="main.py not found beside dashboard.py"
        )
        return

    workers = {}

    for panel in panels.values():

        panel["last_status"] = {}
        panel["detail"].config(text="Starting…")
        draw_grid(panel["canvas"], {})

    try:

        for key, title, target in SCENARIOS:

            status_path = panels[key]["status_file"]

            try:

                if os.path.exists(status_path):
                    os.remove(status_path)

            except OSError as error:

                print(
                    f"[DASHBOARD WARNING] Could not remove old status: {error}",
                    flush=True
                )

            workers[key] = subprocess.Popen(
                [
                    sys.executable,
                    MAIN_FILE,
                    "--scenario",
                    key,
                    "--status-file",
                    status_path,
                    "--headless"
                ],
                cwd=APP_DIR
            )

    except OSError as error:

        run_label.config(
            text=f"Could not start all scenarios: {error}"
        )

        for process in workers.values():

            if process.poll() is None:
                process.terminate()

        return

    run_label.config(text="Starting three scenarios…")


# --------------------------------------------------
# CLOSE DASHBOARD
# --------------------------------------------------

def close_dashboard():

    for process in workers.values():

        if process.poll() is None:

            try:
                process.terminate()

            except OSError:
                pass

    root.destroy()


# --------------------------------------------------
# BUTTON
# --------------------------------------------------

start_button = ttk.Button(
    footer,
    text="START / RESTART COMPARISON",
    command=start_comparison
)

start_button.pack(side="right", padx=4)


# --------------------------------------------------
# INITIALIZE DASHBOARD
# --------------------------------------------------

root.protocol(
    "WM_DELETE_WINDOW",
    close_dashboard
)

for panel in panels.values():

    draw_grid(panel["canvas"], {})

read_status()

root.mainloop()
