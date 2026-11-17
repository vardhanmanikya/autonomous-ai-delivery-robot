class Robot:
    """
    Simulated delivery robot.
    """

    def __init__(self, start_position):
        self.position = start_position
        self.total_moves = 0
        self.delivery_completed = False

    def move_to(self, new_position):
        """
        Move the robot to a new grid position.
        """

        self.position = new_position
        self.total_moves += 1

    def deliver_package(self):
        """
        Mark the package as delivered.
        """

        self.delivery_completed = True

    def get_status(self):
        """
        Return the current robot status.
        """

        return {
            "position": self.position,
            "total_moves": self.total_moves,
            "delivery_completed": self.delivery_completed
        }