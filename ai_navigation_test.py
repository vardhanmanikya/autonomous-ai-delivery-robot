from perception.ai_detection import detect_obstacles


# Run AI obstacle detection
obstacles = detect_obstacles("bus.jpg")


print("\nAI Navigation Test")
print("------------------")

for obstacle in obstacles:

    object_name = obstacle["object"]
    confidence = obstacle["confidence"]
    position = obstacle["position"]

    print(
        f"Detected: {object_name} | "
        f"Confidence: {confidence:.2f} | "
        f"Position: {position}"
    )