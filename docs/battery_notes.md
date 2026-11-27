# Battery Model — Technical Notes

## 1. Overview

The battery model simulates the electrical, thermal and degradation-related behaviour of a lithium-polymer (LiPo) battery pack for an autonomous UAV.

It provides battery-state information to the UAV simulation environment, allowing reinforcement learning agents to consider energy consumption, voltage variation and battery temperature.

The model includes:

- State of Charge (SoC) estimation
- Peukert effect
- Open Circuit Voltage (OCV)
- First-order Thevenin equivalent circuit
- Thermal dynamics
- C-rate-based degradation stress tracking
- Configurable feature switches for ablation experiments

## 2. Battery Configuration

The initial configuration represents a 6S LiPo battery.

| Parameter | Value | Unit |
|---|---:|---|
| Number of cells | 6 | — |
| Nominal capacity | 5.0 | Ah |
| Internal resistance (R0) | 0.03 | Ω |
| Polarisation resistance (R1) | 0.015 | Ω |
| Polarisation capacitance (C1) | 2000 | F |
| Peukert exponent | 1.15 | — |
| Reference current | 5.0 | A |
| Thermal capacity | 300 | J/°C |
| Heat transfer coefficient | 2.0 | W/°C |
| Temperature coefficient | 0.005 | 1/°C |
| Reference temperature | 20 | °C |
| Ambient temperature | 25 | °C |

**Note:** R1 and C1 are provisional modelling parameters. They have not yet been calibrated against experimental battery data.

## 3. State of Charge Model

State of Charge represents the remaining usable battery capacity as a fraction between 0 and 1.

The update equation is:

SoC(k+1) = SoC(k) − [I_eff × Δt] / [3600 × Q(T)]

Where:

- I_eff = effective current (A)
- Δt = simulation time step (seconds)
- Q(T) = temperature-dependent capacity (Ah)

The SoC value is constrained to the interval [0, 1].

## 4. Open Circuit Voltage Model

The OCV model approximates the relationship between battery SoC and open-circuit voltage.

OCV(SoC) = 6 × [3.3 + 0.9 × SoC − 0.3 × exp(−20 × SoC)]

The model represents a six-cell battery pack.

Expected voltage:

| SoC | OCV |
|---|---:|
| 100% | Approximately 25.2 V |
| 50% | Approximately 22.5 V |
| 0% | 18.0 V |

## 5. Peukert Effect

The Peukert effect accounts for the reduction in effective battery capacity at higher discharge currents.

I_eff = I × (I / I_ref)^(k − 1)

Where:

- I = actual discharge current
- I_ref = reference current (5 A)
- k = Peukert exponent (1.15)

A higher discharge current produces disproportionately greater effective capacity consumption.

## 6. Electrical Equivalent Circuit

A first-order Thevenin equivalent circuit represents the battery's internal voltage behaviour.

Terminal voltage:

V_term = OCV(SoC) − I × R0 − V1

Polarisation voltage dynamics:

dV1/dt = −V1/(R1 × C1) + I/C1

The RC component models transient voltage behaviour caused by battery polarisation.

The current is calculated using the power-demand relationship:

P = I × V_term

Because terminal voltage depends on current, the implementation solves the resulting quadratic equation.

## 7. Thermal Model

Battery temperature changes due to internal resistive heating and heat transfer to the surroundings.

C_th × dT/dt = I² × R0 − h × (T − T_amb)

Where:

- C_th = thermal capacity
- h = heat transfer coefficient
- T = battery temperature
- T_amb = ambient temperature

The model uses an explicit Euler integration method.

## 8. Temperature-Dependent Capacity

Available battery capacity is adjusted for temperatures below the reference temperature.

Q(T) = Q_nom × [1 − α × max(0, T_ref − T)]

Where:

- Q_nom = nominal capacity
- α = temperature coefficient
- T_ref = reference temperature (20°C)

The current implementation does not reduce capacity at temperatures above the reference temperature.

## 9. Degradation Stress Tracking

A cumulative stress indicator tracks the effect of discharge current on battery usage.

Stress(k+1) = Stress(k) + (I/Q_nom)² × Δt

This provides a simple measure of accumulated high-current stress.

**Limitation:** The stress value is not a direct measurement of battery State of Health or percentage capacity fade. A calibrated degradation model would be required to estimate actual battery ageing.

## 10. Feature Switches

The model supports configurable components for ablation experiments.

| Feature switch | Function |
|---|---|
| use_peukert | Enables or disables Peukert correction |
| use_rc | Enables or disables RC polarisation dynamics |
| use_thermal | Enables or disables thermal dynamics |
| use_temp_capacity | Enables or disables temperature-dependent capacity |
| use_degradation | Enables or disables stress accumulation |

These switches allow individual battery-model components to be disabled while evaluating their contribution to UAV endurance optimisation.

## 11. Software Interface

The main implementation is located in:

`env/battery.py`

The primary interface is:

```python
class BatteryModel:
    def reset(self):
        ...

    def step(self, power_W, dt, T_amb=None):
        ...
```

The step method returns:

```python
{
    "soc": soc,
    "voltage": voltage,
    "current": current,
    "temp": temperature
}
```

Input units:

| Input | Unit |
|---|---|
| power_W | Watts |
| dt | Seconds |
| T_amb | °C |

Output units:

| Output | Unit |
|---|---|
| soc | Fraction (0–1) |
| voltage | Volts |
| current | Amperes |
| temp | °C |

## 12. Validation Results

The battery model has undergone initial functional and numerical validation.

### 12.1 Discharge-rate validation

| Discharge rate | Current | Simulated duration | Final temperature |
|---|---:|---:|---:|
| 1C | 5 A | 60.08 min | 25.37°C |
| 2C | 10 A | 27.08 min | 26.50°C |
| 3C | 15 A | 17.00 min | 28.37°C |

The results demonstrate that higher discharge rates reduce simulated endurance and increase battery temperature.

### 12.2 Constant-power validation

Under a constant 150 W load:

| Parameter | Initial value | At operational cutoff |
|---|---:|---:|
| SoC | 100% | 4.91% |
| Terminal voltage | 25.02 V | 19.082 V |
| Current | 5.995 A | 7.861 A |
| Temperature | 25°C | 25.86°C |

The operational cutoff was reached after approximately 40.58 minutes.

### 12.3 Automated Testing

The automated test suite contains 14 tests, implemented using pytest.

All 14 tests passed successfully.

The tests cover:

- Initial battery state and reset functionality
- OCV behaviour
- Temperature-dependent capacity
- Peukert correction
- SoC reduction during discharge
- Positive terminal voltage
- RC voltage dynamics
- Thermal response
- Degradation stress accumulation
- Feature switches for model ablation
- Invalid power input
- Invalid time-step input
- Invalid ambient temperature
- Protection against power delivery when the battery is fully depleted

## 13. Visualisation

The battery performance plots are stored at:

`figures/battery_curves.png`

The figure contains four plots:

1. State of Charge versus Time
2. Terminal Voltage versus Time
3. Battery Temperature versus Time
4. Discharge Current versus Time

The plots represent a simulated constant-power discharge experiment at 150 W, ending at the 5% operational cutoff.

## 14. Current Limitations

The current implementation is an analytical simulation model, not a fully calibrated electrochemical battery model.

Its limitations include:

1. The OCV relationship is an approximate mathematical representation.
2. RC parameters are provisional and require calibration.
3. Thermal modelling considers resistive heating through R0 but omits other heat-generation mechanisms.
4. Degradation stress is an indicator rather than a calibrated battery ageing prediction.
5. No experimental battery dataset has yet been used for parameter identification.
6. Operational cutoff enforcement must be handled by the UAV simulation environment.
7. Battery behaviour under realistic time-varying UAV power demand still requires integrated testing.

## 15. Conclusion

The implemented battery model provides a modular representation of battery energy consumption, voltage dynamics, thermal behaviour and discharge-related stress.

Initial tests demonstrate consistent behaviour across multiple discharge rates and under constant-power operation.

The model is intended for integration into the Gymnasium-based UAV environment, where its battery-state outputs will support reinforcement learning-based endurance optimisation.