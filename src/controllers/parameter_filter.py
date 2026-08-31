class ParameterFilter:
    def __init__(self, alpha: float = 0.8):
        self.alpha = alpha
        self.previous_params = None

    def apply(self, new_params: dict) -> dict:
        if self.previous_params is None:
            self.previous_params = new_params.copy()
            return new_params.copy()

        filtered_params = {}

        for key, value in new_params.items():
            previous_value = self.previous_params[key]
            filtered_value = self.alpha * previous_value + (1.0 - self.alpha) * value
            filtered_params[key] = filtered_value

        self.previous_params = filtered_params.copy()

        return filtered_params

    def reset(self):
        self.previous_params = None