import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import json
import os


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title("Autonomous AI Delivery Robot")

root.geometry("1000x650")

root.resizable(False, False)


# ============================================================
# TITLE
# ============================================================

title = tk.Label(
    root,
    text="AUTONOMOUS AI DELIVERY ROBOT",
    font=("Arial", 24, "bold")
)

title.pack(pady=20)


subtitle = tk.Label(
    root,
    text="AI-Based Navigation and Dynamic Obstacle Avoidance",
    font=("Arial", 12)
)

subtitle.pack()


# ============================================================
# MAIN FRAME
# ============================================================

main_frame = tk.Frame(root)

main_frame.pack(
    fill="both",
    expand=True,
    padx=30,
    pady=20
)


# ============================================================
# SIMULATION AREA
# ============================================================

simulation_frame = tk.LabelFrame(
    main_frame,
    text="Simulation",
    font=("Arial", 14, "bold"),
    width=600,
    height=400
)

simulation_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 15)
)

simulation_frame.pack_propagate(False)


simulation_label = tk.Label(
    simulation_frame,
    text="Robot Simulation\n\n"
         "🤖 Robot: (1, 1)\n\n"
         "⭐ Destination: (8, 8)\n\n"
         "⬛ Static Obstacles\n\n"
         "❌ Dynamic Obstacles",
    font=("Arial", 16),
    justify="center"
)

simulation_label.pack(
    expand=True
)


# ============================================================
# SYSTEM STATUS AREA
# ============================================================

status_frame = tk.LabelFrame(
    main_frame,
    text="System Status",
    font=("Arial", 14, "bold"),
    width=300,
    height=400
)

status_frame.pack(
    side="right",
    fill="y"
)

status_frame.pack_propagate(False)


# ============================================================
# AI VISION
# ============================================================

tk.Label(
    status_frame,
    text="AI Vision",
    font=("Arial", 11, "bold")
).pack(pady=(20, 2))


ai_status = tk.Label(
    status_frame,
    text="READY",
    font=("Arial", 12)
)

ai_status.pack()


# ============================================================
# A* PLANNER
# ============================================================

tk.Label(
    status_frame,
    text="A* Planner",
    font=("Arial", 11, "bold")
).pack(pady=(20, 2))


astar_status = tk.Label(
    status_frame,
    text="READY",
    font=("Arial", 12)
)

astar_status.pack()


# ============================================================
# ROBOT STATUS
# ============================================================

tk.Label(
    status_frame,
    text="Robot Status",
    font=("Arial", 11, "bold")
).pack(pady=(20, 2))


robot_status = tk.Label(
    status_frame,
    text="IDLE",
    font=("Arial", 12)
)

robot_status.pack()


# ============================================================
# RE-PLANNING EVENTS
# ============================================================

tk.Label(
    status_frame,
    text="Re-planning Events",
    font=("Arial", 11, "bold")
).pack(pady=(20, 2))


replanning_status = tk.Label(
    status_frame,
    text="0",
    font=("Arial", 12)
)

replanning_status.pack()


# ============================================================
# DELIVERY STATUS
# ============================================================

tk.Label(
    status_frame,
    text="Delivery",
    font=("Arial", 11, "bold")
).pack(pady=(20, 2))


delivery_status = tk.Label(
    status_frame,
    text="NOT STARTED",
    font=("Arial", 12)
)

delivery_status.pack()


# ============================================================
# ROBOT POSITION
# ============================================================

tk.Label(
    status_frame,
    text="Robot Position",
    font=("Arial", 11, "bold")
).pack(pady=(20, 2))


position_status = tk.Label(
    status_frame,
    text="(1, 1)",
    font=("Arial", 12)
)

position_status.pack()


# ============================================================
# READ STATUS.JSON
# ============================================================

def read_status():

    if not os.path.exists("status.json"):
        return

    try:

        with open(
            "status.json",
            "r"
        ) as file:

            status = json.load(file)


        # Update AI status
        ai_status.config(
            text=status.get(
                "ai_status",
                "READY"
            )
        )


        # Update A* status
        astar_status.config(
            text=status.get(
                "astar_status",
                "READY"
            )
        )


        # Update robot status
        robot_status.config(
            text=status.get(
                "robot_status",
                "IDLE"
            )
        )


        # Update re-planning events
        replanning_status.config(
            text=str(
                status.get(
                    "replanning_events",
                    0
                )
            )
        )


        # Update delivery
        delivery_status.config(
            text=status.get(
                "delivery_status",
                "NOT STARTED"
            )
        )


        # Update robot position
        position = status.get(
            "robot_position",
            [1, 1]
        )

        position_status.config(
            text=f"({position[0]}, {position[1]})"
        )


        # Update simulation text
        simulation_label.config(
            text=
            "Robot Simulation\n\n"
            f"🤖 Robot: ({position[0]}, {position[1]})\n\n"
            "⭐ Destination: (8, 8)\n\n"
            "⬛ Static Obstacles\n\n"
            "❌ Dynamic Obstacles"
        )


    except Exception:
        pass


    # Check status again after 500 milliseconds
    root.after(
        500,
        read_status
    )


# ============================================================
# START DELIVERY
# ============================================================

def start_delivery():

    # Reset visible values immediately
    ai_status.config(
        text="STARTING"
    )

    astar_status.config(
        text="STARTING"
    )

    robot_status.config(
        text="INITIALIZING"
    )

    delivery_status.config(
        text="STARTING"
    )


    # Run the actual main.py
    subprocess.Popen(
        [
            sys.executable,
            "main.py"
        ]
    )


# ============================================================
# START BUTTON
# ============================================================

start_button = ttk.Button(
    root,
    text="START DELIVERY",
    command=start_delivery
)

start_button.pack(
    pady=20
)


# ============================================================
# START STATUS MONITOR
# ============================================================

read_status()


# ============================================================
# RUN DASHBOARD
# ============================================================

root.mainloop()