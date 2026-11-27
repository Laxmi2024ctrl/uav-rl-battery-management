# MDP specification: UAVBatteryEnv

Owner: Deva | Status: **draft for Day-1 approval** | Frozen at tag `env-v1`

The problem is a finite-horizon, discounted MDP (S, A, P, R, γ) with **γ = 0.99**.
Objective: find a policy π that maximises E[Σ_t γ^t r_t].

## 1. State / observation (9 values, float32)

| # | Variable | Raw range | Unit | Normalisation | Observation range |
|---|----------|-----------|------|---------------|-------------------|
| 0 | State of charge (SoC) | 0 – 1 | fraction | none | 0 – 1 |
| 1 | Pack terminal voltage | ~18 – 25.2 (6S) | V | ÷ 25 | ~0.7 – 1.0 |
| 2 | Battery temperature | ambient – ~60 | °C | ÷ 60 | ~0.3 – 1.0 |
| 3 | Current ground speed | 0 – 20 | m/s | ÷ 20 | 0 – 1 |
| 4 | Wind along flight axis (+ = tailwind) | −5 – +5 | m/s | ÷ 10 | −0.5 – 0.5 |
| 5 | Payload | 0 – 1 | kg | none | 0 – 1 |
| 6 | Remaining waypoints | 0 – N | count | ÷ N | 0 – 1 |
| 7 | Distance to next target | 0 – √2·L | m | ÷ L (area side) | 0 – 1.42 |
| 8 | Distance to home | 0 – √2·L | m | ÷ L | 0 – 1.42 |

## 2. Actions

| Mode | Space | Meaning | Used by |
|------|-------|---------|---------|
| Discrete | `Discrete(6)` | 0–4 → ground speed 0, 5, 10, 15, 20 m/s toward the current target; 5 → Return-to-Home at 10 m/s (latched until landing) | DQN, PPO, baselines |
| Continuous (`continuous=True`) | `Box([0], [20])` | ground speed in m/s; no RTH action, home is the target after the last waypoint | SAC, TD3 |

After the last waypoint the target automatically becomes home (0, 0).

## 3. Transition

- Time step dt = 5 s. The UAV moves `speed × dt` toward the target and snaps to it when within one step.
- Airspeed = |ground speed − wind|. Power P = Zeng et al. rotary-wing model × (1 + m_payload / 2 kg)^1.5.
- The battery is stepped once per step: `BatteryModel.step(power_W, dt, T_amb)` → SoC, voltage, current, temperature.
- Given the episode's sampled waypoints, wind and payload, the transition is **deterministic**. All randomness is in `reset(seed)`: waypoint layout, wind, payload (and starting SoC, see §7), drawn from one RNG.

## 4. Reward (env/reward.py)

r_t = −c_time + R_wp·1[waypoint] − c_E·I_eff/50 − c_soc·1[SoC < 0.2] − c_T·1[T > 45 °C] + 1[landed]·(R_land + 20·SoC_final) − R_crash·1[SoC ≤ 0.05]

| Term | Weight | Default | Why it is there |
|------|--------|---------|-----------------|
| Time cost | c_time | 0.01 / step | Push the agent to finish instead of hovering |
| Waypoint bonus | R_wp | 10 | Progress signal for completing the route |
| Energy cost | c_E | 0.5 | Penalise high current (faster drain via Peukert, more heating) |
| Low-SoC penalty | c_soc | 1.0 / step | Discourage flying below 20 % charge |
| Over-temperature penalty | c_T | 0.5 / step | LiPo degradation and safety above 45 °C |
| Safe landing | R_land (+20·SoC) | 50 | Mission success; more charge left = more margin |
| Crash | R_crash | 100 | Losing the UAV is the worst outcome |

All weights are in `DEFAULT_WEIGHTS`; ablations use `make_weights(c_E=0)` and so on, without editing the env.

## 5. Termination

| Condition | Flag |
|-----------|------|
| Safe landing at home (after all waypoints, or after RTH) | `terminated = True` |
| Crash: SoC ≤ 0.05 | `terminated = True` |
| Simulated time > 3000 s | `truncated = True` |

A mission is **completed** only if the UAV lands safely after visiting all N waypoints. A safe RTH landing with waypoints left counts as landed but not completed.

## 6. Info contract (env → reward.py / evaluate.py)

`env.step()` must return an `info` dict with these keys (Ujwal, please match these):

| Key | Type / unit | Used by |
|-----|-------------|---------|
| `waypoint_reached` | bool (this step) | reward |
| `i_eff_A` | float, A (Peukert-corrected current) | reward |
| `soc` | float, 0–1 | reward, evaluate |
| `temp_C` | float, °C | reward, evaluate |
| `landed` | bool | reward, evaluate |
| `crashed` | bool | reward, evaluate |
| `power_W` | float, W | evaluate, demo |
| `energy_Wh` | float, Wh drawn this step | evaluate |
| `sim_time_s` | float, s since reset | evaluate |
| `waypoints_reached` | int, cumulative | evaluate |
| `n_waypoints` | int, N | evaluate |

Constructor keyword arguments used for ablations: `continuous`, `reward_weights`, `use_wind`, `use_peukert`, `use_thermal` (the last two are passed through to the BatteryModel).

## 7. Proposed spec changes (decide before env-v1)

Running the baselines in a stand-in env built to the current spec showed:

| Setting | FixedSpeed | MaxRange | RTH25 | Problem |
|---------|-----------|----------|-------|---------|
| Current spec (500 m, full battery) | 100 % done, final SoC 0.90 | 100 %, 0.92 | identical to MaxRange | Battery uses only ~10 %: SoC limits never matter, RTH never triggers, nothing for RL to learn about battery management |
| **Proposed: 2000 m area, start SoC ~ U(0.4, 1.0)** | 83 % done, 17 crashes, return 58.9 | 89 %, 11 crashes, 82.9 | 81 %, **0 crashes**, **97.6** | Baselines differ clearly; RTH vs. continue is a real trade-off |

Proposals:
1. **Area 500 m → 2000 m** and **random starting SoC U(0.4, 1.0)** (a partly charged pack), sampled in `reset(seed)`.
2. Battery temperature stays below about 28 °C in every run (I²R0 ≈ 2 W), so the 45 °C penalty and the "no temperature model" ablation would show no effect. Option: randomise ambient temperature (for example 0–40 °C) so heat and cold-capacity loss both matter. Yash Raj and Ujwal to decide.
3. Max-range speed = 18.3 m/s (continuous). In the discrete env the closest equivalent is **20 m/s** (8.9 J/m against 9.2 J/m at 15 m/s).