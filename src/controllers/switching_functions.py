import math


def sign(value: float) -> float:
    if value > 0:
        return 1.0
    if value < 0:
        return -1.0
    return 0.0


def saturation(value: float) -> float:
    if value > 1.0:
        return 1.0
    if value < -1.0:
        return -1.0
    return value


def tanh_switch(value: float) -> float:
    return math.tanh(value)


def apply_switching(value: float, phi: float, switching_type: str) -> float:
    if phi <= 0:
        raise ValueError("phi must be greater than 0")

    scaled_value = value / phi

    if switching_type == "sign":
        return sign(scaled_value)

    if switching_type == "sat":
        return saturation(scaled_value)

    if switching_type == "tanh":
        return tanh_switch(scaled_value)

    raise ValueError(f"Unknown switching type: {switching_type}")