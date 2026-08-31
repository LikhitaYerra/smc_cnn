from src.controllers.adaptive_smc_controller import AdaptiveSlidingModeController
from src.controllers.fuzzy_gain_scheduler import FuzzyGainScheduler


class FuzzySlidingModeController:
    """Fuzzy-logic gain scheduler wrapped around the SMC core."""

    def __init__(
        self,
        switching_type: str = "tanh",
        position_dead_zone: float = 0.01,
        theta_dead_zone: float = 0.01,
        parameter_filter_alpha: float = 0.85,
        update_interval_steps: int = 10,
    ):
        self.scheduler = FuzzyGainScheduler()
        self.update_interval_steps = update_interval_steps
        self._step_counter = 0
        self._last_tracking_error = 0.0
        self._last_omega = 0.0

        initial_params = self.scheduler.BASE_PARAMS.copy()
        self.adaptive = AdaptiveSlidingModeController(
            initial_params=initial_params,
            switching_type=switching_type,
            position_dead_zone=position_dead_zone,
            theta_dead_zone=theta_dead_zone,
            parameter_filter_alpha=parameter_filter_alpha,
        )

    def reset(self):
        self.scheduler.reset()
        self._step_counter = 0
        self._last_tracking_error = 0.0
        self._last_omega = 0.0
        self.adaptive.reset()

    def compute_control(self, *args, **kwargs):
        v, omega, error, surface = self.adaptive.compute_control(*args, **kwargs)

        tracking_error = (error.ex ** 2 + error.ey ** 2) ** 0.5
        self.scheduler.observe(tracking_error, self._last_omega)
        self._last_tracking_error = tracking_error
        self._last_omega = omega

        self._step_counter += 1
        if self._step_counter % self.update_interval_steps == 0:
            new_params = self.scheduler.infer(tracking_error)
            self.adaptive.update_parameters(new_params)

        return v, omega, error, surface
