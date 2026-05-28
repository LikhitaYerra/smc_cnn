import matplotlib.pyplot as plt


def plot_robot_path(xs, ys, title="Robot Path", save_path=None):
    plt.figure(figsize=(7, 7))
    plt.plot(xs, ys, label="Robot path")
    plt.scatter(xs[0], ys[0], marker="o", label="Start")
    plt.scatter(xs[-1], ys[-1], marker="x", label="End")
    plt.xlabel("x position")
    plt.ylabel("y position")
    plt.title(title)
    plt.axis("equal")
    plt.grid(True)
    plt.legend()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()



def plot_reference_trajectory(x_d, y_d, title="Reference Trajectory", save_path=None):
    plt.figure(figsize=(7, 7))
    plt.plot(x_d, y_d, label="Desired trajectory")
    plt.scatter(x_d[0], y_d[0], marker="o", label="Start")
    plt.scatter(x_d[-1], y_d[-1], marker="x", label="End")
    plt.xlabel("x position")
    plt.ylabel("y position")
    plt.title(title)
    plt.axis("equal")
    plt.grid(True)
    plt.legend()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()


def plot_tracking_error(times, errors, title="Tracking Error", save_path=None):
    plt.figure(figsize=(9, 5))
    plt.plot(times, errors, label="Distance error")
    plt.xlabel("Time [s]")
    plt.ylabel("Error [m]")
    plt.title(title)
    plt.grid(True)
    plt.legend()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()



def plot_sliding_surfaces(times, sx_values, sy_values, stheta_values, save_path=None):
    plt.figure(figsize=(10, 5))
    plt.plot(times, sx_values, label="s_x")
    plt.plot(times, sy_values, label="s_y")
    plt.plot(times, stheta_values, label="s_theta")
    plt.xlabel("Time [s]")
    plt.ylabel("Sliding surface value")
    plt.title("Sliding Surfaces")
    plt.grid(True)
    plt.legend()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()

def plot_control_signals(times, v_values, omega_values, title="Control Signals", save_path=None):
    plt.figure(figsize=(10, 5))
    plt.plot(times, v_values, label="Linear velocity v")
    plt.plot(times, omega_values, label="Angular velocity omega")
    plt.xlabel("Time [s]")
    plt.ylabel("Control command")
    plt.title(title)
    plt.grid(True)
    plt.legend()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()