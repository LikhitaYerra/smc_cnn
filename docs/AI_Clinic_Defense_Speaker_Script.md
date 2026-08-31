# AI Clinic Defense — Speaker Script

Core deck: Slides 1–21. Slides 22–24 are backup/Q&A only.

## 1. Title

[Timing: 40 seconds]

Good morning. We are presenting our AI Clinic project on CNN-adaptive sliding mode control for autonomous differential-drive robots under environmental uncertainty. Our goal was not only to build a robust controller, but to create a complete and explainable AI-control pipeline—from environment perception to controller adaptation and a live 3D digital twin. The project was completed by our five-person team under the supervision of Professor Vishvjit Thakar. I will first explain the control problem, then the CNN and PPO approaches, show the quantitative results, and finish with the digital twin demonstration.

## 2. Defense story

[Timing: 35 seconds]

The presentation follows one simple story. First, a fixed-gain controller cannot respond optimally to every operating condition. Second, we use a CNN to identify the condition and choose an interpretable controller preset. Third, we evaluate that idea consistently across five scenarios and against several baselines. Finally, we expose the entire system through a live digital twin. This roadmap is important because the digital twin is not a separate interface; it is the final layer of the same research pipeline.

## 3. Problem statement

[Timing: 60 seconds]

Sliding mode control is a strong baseline because it is robust to disturbances and modelling errors. The limitation is that its behavior depends directly on fixed gains and the boundary-layer width. Sensor noise requires more smoothing to avoid rapid actuator switching. An external push requires more aggressive heading correction. Wheel slip requires stronger gains to recover the lost motion. These requirements conflict. If we tune only for noise, recovery becomes slower; if we tune only for disturbance rejection, chattering can increase. This is the central problem: one static parameter set cannot be optimal in all five environments.

## 4. Gap and contributions

[Timing: 55 seconds]

The individual technologies are not new by themselves. Sliding mode control, CNN perception and reinforcement learning each have a large literature. Our research gap is the integration of these pieces into one compact and reproducible system where the CNN does not replace the controller—it supervises it. That keeps the actual control law interpretable. Our four contributions are the full pipeline, scenario-aware gain presets, a multi-controller benchmark including an oracle upper bound, and a live digital twin that makes the research repeatable during the defense.

## 5. Architecture

[Timing: 60 seconds]

This is the main system architecture. A grayscale occupancy map represents the operating condition. The lightweight CNN predicts one of five classes. That class selects a scenario-specific parameter preset containing the sliding-surface gains, velocity gains, boundary-layer width and angular smoothing. The SMC then calculates linear and angular velocity commands exactly as before. This distinction is important: the learned model is a supervisor, not an opaque end-to-end controller. The bottom branch shows our PPO alternative, which uses robot state and error to adapt parameters.

## 6. Robot and control law

[Timing: 70 seconds]

The robot is modeled as a standard differential-drive unicycle. Its position evolves through linear speed v and heading through angular speed omega. The non-holonomic constraint means it cannot move sideways, so lateral pushes are challenging. On the control side, we define sliding surfaces from tracking error and its derivative. The linear command corrects forward error. The angular command combines bearing correction with smooth hyperbolic-tangent switching. Finally, exponential smoothing reduces high-frequency oscillation. The most important design variable is phi: a wider boundary layer reduces chattering but permits more steady-state error.

## 7. Scenarios

[Timing: 45 seconds]

We use five controlled scenarios. Normal is the sanity check. Noise corrupts pose measurements. Disturbance applies a lateral push at eight seconds. Slip reduces effective velocity by thirty percent between ten and fourteen seconds. Combined applies all effects together and is therefore the hardest case. Every controller uses the same robot model, reference speed, simulation step and perturbation timing, so the comparison is fair. The normal scenario also verifies that adaptation does not introduce unnecessary behavior when no uncertainty exists.

## 8. CNN

[Timing: 65 seconds]

The CNN receives a sixty-four by sixty-four grayscale map. Each scenario has a distinct visual signature: a clean path, noisy pixels, an impact marker, a slip band, or all cues combined. The network has three convolutional blocks followed by a small classifier, for approximately five hundred and thirty-four thousand parameters. It reaches one hundred percent on the engineered test set. Because that dataset is deliberately separable, we also created more realistic cluttered maps; the CNN still reaches ninety-five point one percent. In deployment, one pre-mission inference selects the controller preset, so runtime cost is minimal.

## 9. Preset logic

[Timing: 55 seconds]

This slide explains the system's interpretability. For each class we know exactly which parameters change and why. Under noise we widen phi and increase smoothing, which suppresses angular chattering. Under disturbance we increase lateral surface and angular correction gains, which improves recovery after the push. Under slip we raise both positional sliding gains to compensate for lost velocity. The combined preset balances these competing requirements. This is a key advantage over an end-to-end neural controller: every adaptation can be inspected, justified and bounded.

## 10. PPO

[Timing: 60 seconds]

We also implemented PPO as a learning-based comparison. The observation contains tracking error, error rate, a smoothed jitter measure and uncertainty flags. The actor-critic policy selects one of the same five SMC presets every zero point two seconds. Its reward penalizes error, chattering and control effort. After eighty thousand training steps, PPO reaches the lowest combined-scenario chattering value of forty-eight point nine. However, it performs worse under disturbance and slip. Therefore, our conclusion is balanced: PPO is promising, but the CNN supervisor is currently more reliable and more interpretable for this dataset.

## 11. Evaluation protocol

[Timing: 45 seconds]

The main experiment lasts twenty seconds at a ten-millisecond time step. The robot tracks a straight reference at zero point three meters per second. Fixed seeds make the perturbations reproducible. We compare five controller variants, including an oracle that knows the true scenario and therefore defines the practical ceiling. We report four metrics because tracking error alone is incomplete. RMSE captures overall accuracy, final error measures recovery, chattering reflects actuator smoothness, and control effort reflects energy and mechanical demand.

## 12. Headline results

[Timing: 65 seconds]

These are the four numbers I want the panel to remember. Under noise, CNN adaptation reduces chattering by thirty-five point seven percent. After an external disturbance, final error improves by fourteen point four percent. Under wheel slip, final error improves by thirty-two point seven percent. On realistic maps, the classifier reaches ninety-five point one percent accuracy. In the disturbance test, CNN final error is only two point three millimeters above the oracle. We also report the limitation honestly: reducing noise-induced chattering increases steady-state error because of the wider boundary layer.

## 13. Trajectory results

[Timing: 55 seconds]

This figure shows the actual robot trajectories in the combined scenario. The dashed line is the desired path. Up to the push, the controllers remain close together. At approximately two point four meters, the lateral disturbance creates the sharp deviation. Classical SMC produces the largest overshoot and wider recovery loop. CNN-adaptive SMC returns more tightly because the disturbance preset increases heading correction. PPO lies between the two. The key point is that all three controllers receive the exact same disturbance; the difference comes from parameter adaptation.

## 14. Tracking error

[Timing: 55 seconds]

The time-series view makes the experiment easier to interpret. During the first eight seconds, only measurement noise is active. At eight seconds, the external push causes an immediate error spike. From ten to fourteen seconds, wheel slip slows the robot and creates a second error increase. After fourteen seconds, all controllers recover. Classical SMC reaches the highest peak and remains above the adaptive methods for much of the recovery. This plot confirms that the trajectory difference is not a visual artifact; it corresponds to lower tracking error over time.

## 15. Trade-off

[Timing: 60 seconds]

These two charts must be read together. On the left, RMSE is similar between classical and CNN-adaptive control, and the combined scenario remains the hardest. Under noise, the adaptive controller accepts a small loss in precision. On the right, we see why: chattering falls dramatically under noise and combined uncertainty. This is not a free improvement; it is a deliberate engineering trade-off. Smoother angular commands protect actuators and reduce instability, while the controller preserves competitive tracking accuracy.

## 16. Heatmap discussion

[Timing: 60 seconds]

The heatmap gives the most honest summary. Green means CNN-adaptive is better; red means worse. Under noise, the main benefit is smoothness, while final error increases. Under disturbance and slip, the main benefit is final recovery, while effort or chattering may increase because the controller becomes more aggressive. Under combined uncertainty, chattering improves strongly but RMSE changes very little. Therefore, our claim is not that CNN adaptation wins every cell. Our claim is that it makes the trade-off context-aware and explainable.

## 17. Multi-controller benchmark

[Timing: 55 seconds]

This benchmark provides context beyond the classical baseline. Fuzzy gain scheduling reduces noise chattering modestly, but CNN and oracle are clearly lower. Under disturbance, CNN reaches seventeen point nine millimeters compared with the oracle's fifteen point six. Under slip, CNN and oracle are nearly identical. PPO is best on combined chattering but weak under slip and disturbance. Overall, the CNN supervisor offers the strongest balance of performance, interpretability and low runtime cost.

## 18. Live demo

[Timing: 30 seconds, then switch to browser for 3–4 minutes]

This is the live digital twin. The left panel controls controller mode, scenario, trajectory and speed. The center visualizes the robot and its path in a hospital corridor. The right panel shows live metrics. I will now switch to the browser. First I press T to run the controller tour. Then I open Compare to benchmark all three controllers. If time allows, I show the dual path view and replay. 

DEMO RECOVERY LINE: If the live demo fails, say: 'The system is also recorded here; this screenshot and the following quantitative results were generated by the same backend.'

## 19. Limitations

[Timing: 50 seconds]

We want to be precise about the limits of the evidence. Most occupancy maps are synthetic, and the realistic set is still procedural rather than real LiDAR. The CNN currently classifies once before the mission. Parameter presets are hand-tuned, and the controller is evaluated in a two-dimensional kinematic simulation with fixed seeds. Finally, PPO remains an experimental extension. Therefore, this work demonstrates feasibility and a reproducible architecture; it does not yet prove generalisation to a physical robot or arbitrary terrain.

## 20. Conclusion

[Timing: 60 seconds]

To conclude, we built a complete perception-control-demonstration pipeline. The CNN makes sliding mode control context-aware without replacing its interpretable control law. The main evidence is a thirty-five point seven percent chattering reduction under noise, up to thirty-two point seven percent better final recovery, ninety-five point one percent classification on realistic maps, and a working digital twin. The next step is to move from procedural maps and fixed scenarios to real LiDAR, continuous online inference, Monte Carlo evaluation and a physical differential-drive robot. The core message is that explainable AI can improve robust control while preserving engineering transparency.

## 21. Q&A

[Timing: Q&A]

Thank you for your attention. We are ready for your questions.

LIKELY QUESTION — Why CNN if random forest is slightly better on realistic maps?
ANSWER: The CNN integrates naturally with image features and scales to richer spatial inputs. The random forest result confirms that the current cues are separable; the CNN is the extensible architecture for future LiDAR and camera maps.

LIKELY QUESTION — Is 100% accuracy overfitting?
ANSWER: It reflects engineered class separability, not real-world performance. That is why we separately report 95.1% on cluttered maps and state physical validation as future work.

LIKELY QUESTION — Why is CNN not better on every metric?
ANSWER: Smoothing and tracking precision conflict. The Lyapunov bound predicts that a wider boundary layer reduces chattering while widening steady-state error.

LIKELY QUESTION — Why not use PPO alone?
ANSWER: Current PPO is competitive on combined chattering but weaker under slip and disturbance. CNN supervision is more reliable, interpretable and cheaper at runtime.

## 22. Backup presets

[Backup slide — use only if asked about exact controller parameters]

These are the complete scenario-specific parameter values. Point out that noise raises phi and smoothing, disturbance raises lateral and angular correction, and slip raises both position gains. The combined preset is a compromise.

## 23. Backup stability

[Backup slide — use if asked about stability]

We use the composite Lyapunov function based on the three sliding surfaces. Because x times tanh of x over phi is positive away from zero, the derivative is negative outside a bounded disturbance-dependent region. This gives uniform ultimate boundedness. Inside the boundary layer, the error bound grows with phi. That is why noise smoothing reduces chattering but can increase steady-state error.

## 24. Backup implementation

[Backup slide — use if asked about implementation]

The simulation and evaluation are Python-based. PyTorch handles CNN and PPO. FastAPI streams state over WebSocket, while React and Three.js render the 3D twin. Runs can be recorded, replayed and exported. The project includes trained checkpoints and scripts for regeneration.
