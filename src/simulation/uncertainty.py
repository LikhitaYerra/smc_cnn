class WheelSlip:
    def __init__(
        self,
        start_time: float = 10.0,
        end_time: float = 14.0,
        slip_factor: float = 0.7,
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.slip_factor = slip_factor

    def apply(self, v: float, omega: float, current_time: float):
        if self.start_time <= current_time <= self.end_time:
            return v * self.slip_factor, omega * self.slip_factor

        return v, omega