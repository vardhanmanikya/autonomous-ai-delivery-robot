from perception.ai_detection import detect_obstacles


# Detect objects from the image
obstacles = detect_obstacles("bus.jpg")


print("\nAI to Grid Mapping")
print("------------------")


for obstacle in obstacles:

    position = obstacle["position"]
    object_name = obstacle["object"]
    confidence = obstacle["confidence"]

    if confidence < 0.70:
        continue

    if position == "LEFT":
        grid_position = "(3, 4)"

    elif position == "CENTER":
        grid_position = "(4, 4)"

    else:
        grid_position = "(5, 4)"

    print(
        f"{object_name} detected at {position} "
        f"→ simulated grid cell {grid_position}"
    )