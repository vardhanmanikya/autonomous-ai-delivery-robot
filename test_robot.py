from simulation.robot import Robot


robot = Robot((1, 1))

print("Robot Simulation Test")
print("---------------------")

print("Initial position:", robot.position)

robot.move_to((1, 2))
print("After movement:", robot.position)

robot.move_to((1, 3))
print("After movement:", robot.position)

robot.deliver_package()

print("Delivery completed:", robot.delivery_completed)

print("\nRobot Status")
print(robot.get_status())