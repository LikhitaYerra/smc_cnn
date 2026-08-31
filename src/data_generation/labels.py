SCENARIO_LABELS = {
    "normal": 0,
    "noise": 1,
    "disturbance": 2,
    "slip": 3,
    "combined": 4,
}

LABEL_TO_SCENARIO = {
    value: key for key, value in SCENARIO_LABELS.items()
}