from src.controllers.smc_controller import SlidingModeController
from src.controllers.parameter_filter import ParameterFilter


class AdaptiveSlidingModeController:
    def __init__(
        self,
        initial_params: dict,
        switching_type: str = "sat",
        position_dead_zone: float = 0.01,
        theta_dead_zone: float = 0.01,
        parameter_filter_alpha: float = 0.8,
    ):
        self.switching_type = switching_type
        self.position_dead_zone = position_dead_zone
        self.theta_dead_zone = theta_dead_zone

        self.parameter_filter = ParameterFilter(alpha=parameter_filter_alpha)

        self.controller = self._create_controller(initial_params)

    def _create_controller(self, params: dict):
        return SlidingModeController(
            lambda_x=params["lambda_x"],
            lambda_y=params["lambda_y"],
            lambda_theta=params["lambda_theta"],
            k_v=params["k_v"],
            k_omega=params["k_omega"],
            phi=params["phi"],
            max_v=params["max_v"],
            max_omega=params["max_omega"],
            switching_type=self.switching_type,
            omega_smoothing=params["omega_smoothing"],
            position_dead_zone=self.position_dead_zone,
            theta_dead_zone=self.theta_dead_zone,
        )

    def update_parameters(self, new_params: dict):
        filtered_params = self.parameter_filter.apply(new_params)

        old_surface_calculator = self.controller.surface_calculator
        previous_omega = self.controller.previous_omega

        self.controller = self._create_controller(filtered_params)

        self.controller.surface_calculator = old_surface_calculator
        self.controller.previous_omega = previous_omega

        return filtered_params

    def compute_control(self, *args, **kwargs):
        return self.controller.compute_control(*args, **kwargs)

    def reset(self):
        self.controller.reset()
        self.parameter_filter.reset()