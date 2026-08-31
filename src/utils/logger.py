import os
import pandas as pd


def save_simulation_log(log_data, save_path: str):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    df = pd.DataFrame(log_data)
    df.to_csv(save_path, index=False)

    print(f"Simulation log saved to: {save_path}")
    return df