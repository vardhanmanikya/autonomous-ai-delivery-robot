from ultralytics import YOLO


# Load YOLO model
model = YOLO("yolo26n.pt")


def detect_obstacles(image_path):

    results = model(image_path)

    detected_objects = []

    for result in results:

        image_width = result.orig_shape[1]

        for box in result.boxes:

            # Object class
            class_id = int(box.cls[0])
            class_name = result.names[class_id]

            # Confidence
            confidence = float(box.conf[0])

            # Bounding box
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # Object center
            center_x = (x1 + x2) / 2

            # Determine position
            if center_x < image_width / 3:
                position = "LEFT"

            elif center_x < 2 * image_width / 3:
                position = "CENTER"

            else:
                position = "RIGHT"

            # Store detection
            detected_objects.append({
                "object": class_name,
                "confidence": confidence,
                "position": position,
                "bounding_box": (x1, y1, x2, y2)
            })

    return detected_objects


# Test the detector
if __name__ == "__main__":

    obstacles = detect_obstacles("bus.jpg")

    print("\nDetected Obstacles")
    print("------------------")

    for obstacle in obstacles:

        print(
            f"{obstacle['object']} | "
            f"Confidence: {obstacle['confidence']:.2f} | "
            f"Position: {obstacle['position']}"
        )