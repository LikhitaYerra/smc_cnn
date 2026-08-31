class ExternalDisturbance:
    def __init__(
        self,
        start_time: float = 8.0,
        duration: float = 0.5,
        dx: float = 0.0,
        dy: float = 0.4,
        dtheta: float = 0.0,
    ):
        self.start_time = start_time
        self.end_time = start_time + duration
        self.dx = dx
        self.dy = dy
        self.dtheta = dtheta
        self.applied = False

    def apply(self, robot, current_time: float):
        if self.applied:
            return

        if self.start_time <= current_time <= self.end_time:
            robot.state.x += self.dx
            robot.state.y += self.dy
            robot.state.theta += self.dtheta
            self.applied = True