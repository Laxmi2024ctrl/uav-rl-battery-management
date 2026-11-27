class BatteryModel:
    """
    Battery model for a 6S LiPo UAV battery.

    Models:
    - State of Charge (SoC)
    - Peukert effect
    - 1-RC Thevenin equivalent circuit
    - Thermal behaviour
    - Battery degradation stress
    """

    def __init__(
    self,
    use_peukert=True,
    use_rc=True,
    use_thermal=True,
    use_temp_capacity=True,
    use_degradation=True):
        self.params = {
            # Battery specifications
            "Q_nom": 5.0,          # Nominal capacity (Ah)
            "num_cells": 6,

            # Electrical parameters
            "R0": 0.03,             # Ohmic resistance (ohm)
            "R1": 0.015,            # Polarization resistance (ohm)
            "C1": 2000.0,            # Polarization capacitance (F)

            # Peukert parameters
            "peukert_k": 1.15,
            "I_ref": 5.0,            # Reference current (A)

            # Thermal parameters
            "C_th": 300.0,           # Thermal capacity (J/deg C)
            "h": 2.0,                # Cooling coefficient (W/deg C)
            "alpha": 0.005,          # Temperature coefficient
            "T_ref": 20.0,           # Reference temperature (deg C)

            # Default environment
            "T_amb": 25.0,            # Ambient temperature (deg C)
        }
        
        self.use_peukert = use_peukert
        self.use_rc = use_rc
        self.use_thermal = use_thermal
        self.use_temp_capacity = use_temp_capacity
        self.use_degradation = use_degradation

        # Initial battery state
        self.reset()

    def reset(self):
        """Reset battery to fully charged initial condition."""
        self.soc = 1.0
        self.temp = self.params["T_amb"]
        self.v1 = 0.0
        self.stress = 0.0
        
    def calculate_ocv(self, soc):
        """
        Calculate open-circuit voltage.

        Args:
            soc (float): State of charge (0 to 1).

        Returns:
            float: Pack open-circuit voltage (V).
        """
        import numpy as np

        soc = np.clip(soc, 0.0, 1.0)

        return self.params["num_cells"] * (
            3.3 + 0.9 * soc - 0.3 * np.exp(-20 * soc)
        )
        
    def calculate_capacity(self, temperature):
        """
        Calculate available battery capacity based on temperature.

        Args:
            temperature (float): Battery temperature (deg C).

        Returns:
            float: Available capacity (Ah).
        """
        p = self.params

        capacity_factor = 1 - p["alpha"] * max(
            0.0, p["T_ref"] - temperature
        )

        return p["Q_nom"] * max(0.0, capacity_factor)
    
    def calculate_effective_current(self, current):
        """
        Apply Peukert correction to discharge current.

        Args:
            current (float): Actual discharge current (A).

        Returns:
            float: Effective discharge current (A).
        """
        p = self.params

        if current <= 0:
            return 0.0

        return current * (
            current / p["I_ref"]
        ) ** (p["peukert_k"] - 1)
        
    def calculate_current(self, power_W):
        """
        Calculate discharge current and terminal voltage.

        Args:
            power_W (float): Requested battery power (W).

        Returns:
            tuple: (current in A, terminal voltage in V)
        """
        if power_W < 0:
            raise ValueError("Charging power is not supported yet.")

        if power_W == 0:
            voltage = max(
                0.0,
                self.calculate_ocv(self.soc) - self.v1
            )
            return 0.0, voltage

        p = self.params

        ocv = self.calculate_ocv(self.soc)
        resistance = p["R0"]
        available_voltage = ocv - (
         self.v1 if self.use_rc else 0.0
        )

        discriminant = (
            available_voltage**2
            - 4 * resistance * power_W
        )

        if discriminant < 0:
            raise ValueError(
                "Requested power exceeds battery's feasible output."
            )

        current = (
            available_voltage - discriminant**0.5
        ) / (2 * resistance)

        voltage = available_voltage - current * resistance

        return current, voltage
    
    def update_rc_voltage(self, current, dt):
        """
        Update RC polarization voltage.

        Args:
            current (float): Discharge current (A).
            dt (float): Time step (s).

        Returns:
            float: Updated polarization voltage (V).
        """
        import math

        p = self.params

        decay = math.exp(
            -dt / (p["R1"] * p["C1"])
        )

        self.v1 = (
            self.v1 * decay
            + current * p["R1"] * (1 - decay)
        )

        return self.v1
    
    def update_temperature(self, current, dt, T_amb):
        """
        Update battery temperature.

        Args:
            current (float): Discharge current (A).
            dt (float): Time step (s).
            T_amb (float): Ambient temperature (deg C).

        Returns:
            float: Updated battery temperature (deg C).
        """
        p = self.params

        heat_generated = current**2 * p["R0"]
        heat_dissipated = p["h"] * (self.temp - T_amb)

        temperature_change = (
            (heat_generated - heat_dissipated)
            / p["C_th"]
        ) * dt

        self.temp += temperature_change

        return self.temp
    
    def update_stress(self, current, dt):
        """
        Accumulate battery stress due to discharge current.

        Args:
            current (float): Discharge current (A).
            dt (float): Time step (s).

        Returns:
            float: Cumulative stress indicator.
        """
        q_nom = self.params["Q_nom"]

        self.stress += (current / q_nom) ** 2 * dt

        return self.stress
    
    def step(self, power_W, dt, T_amb=None):
        """
        Advance the battery simulation by one time step.

        Args:
            power_W (float): Requested battery power (W).
            dt (float): Simulation time step (s).
            T_amb (float): Ambient temperature (deg C).

        Returns:
            dict: Updated battery state containing:
                soc (float): State of charge (0 to 1).
                voltage (float): Terminal voltage during this step (V).
                current (float): Discharge current (A).
                temp (float): Battery temperature after this step (deg C).
        """

        import math

        if not math.isfinite(power_W) or power_W < 0:
            raise ValueError("power_W must be finite and non-negative.")

        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be finite and positive.")

        if T_amb is None:
            T_amb = self.params["T_amb"]

        if not math.isfinite(T_amb):
            raise ValueError("T_amb must be finite.")
        
        # Prevent further discharge when the battery is depleted
        if self.soc <= 0.0:
            voltage = self.calculate_ocv(self.soc)

            if self.use_rc:
                voltage = max(0.0, voltage - self.v1)

            return {
                "soc": self.soc,
                "voltage": voltage,
                "current": 0.0,
                "temp": self.temp
            }

        # 1. Calculate current and terminal voltage
        current, voltage = self.calculate_current(power_W)

        # 2. Apply Peukert correction
        if self.use_peukert:
            effective_current = self.calculate_effective_current(current)
        else:
            effective_current = current

        # 3. Calculate available capacity
        if self.use_temp_capacity:
            capacity = self.calculate_capacity(self.temp)
        else:
            capacity = self.params["Q_nom"]

        # 4. Update State of Charge
        if current > 0:
            self.soc -= (
                effective_current * dt
            ) / (3600.0 * capacity)

        self.soc = max(0.0, min(1.0, self.soc))

        # 5. Update RC polarization voltage
        if self.use_rc:
            self.update_rc_voltage(current, dt)

        # 6. Update battery temperature
        if self.use_thermal:
            self.update_temperature(current, dt, T_amb)

        # 7. Accumulate degradation stress
        if self.use_degradation:
            self.update_stress(current, dt)

        return {
            "soc": self.soc,
            "voltage": voltage,
            "current": current,
            "temp": self.temp
        }
