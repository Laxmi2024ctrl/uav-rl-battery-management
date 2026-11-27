import matplotlib.pyplot as plt

from env.battery import BatteryModel


# Simulation settings
battery = BatteryModel()

power_W = 150
dt = 5
cutoff_soc = 0.05

# Store simulation results
time_values = []
soc_values = []
voltage_values = []
temperature_values = []
current_values = []

elapsed_time = 0

while battery.soc > cutoff_soc:

    result = battery.step(power_W, dt)

    elapsed_time += dt

    time_values.append(elapsed_time / 60)
    soc_values.append(result["soc"] * 100)
    voltage_values.append(result["voltage"])
    temperature_values.append(result["temp"])
    current_values.append(result["current"])


# Create four-panel figure
fig, axes = plt.subplots(2, 2, figsize=(13, 9))

fig.suptitle(
    "Battery Performance Under Constant 150 W Load",
    fontsize=15,
    fontweight="bold"
)

# Plot 1: SoC
axes[0, 0].plot(time_values, soc_values)
axes[0, 0].set_title("State of Charge vs Time")
axes[0, 0].set_xlabel("Time (minutes)")
axes[0, 0].set_ylabel("SoC (%)")
axes[0, 0].grid(True)

# Plot 2: Voltage
axes[0, 1].plot(time_values, voltage_values)
axes[0, 1].set_title("Terminal Voltage vs Time")
axes[0, 1].set_xlabel("Time (minutes)")
axes[0, 1].set_ylabel("Voltage (V)")
axes[0, 1].grid(True)

# Plot 3: Temperature
axes[1, 0].plot(time_values, temperature_values)
axes[1, 0].set_title("Battery Temperature vs Time")
axes[1, 0].set_xlabel("Time (minutes)")
axes[1, 0].set_ylabel("Temperature (°C)")
axes[1, 0].grid(True)

# Plot 4: Current
axes[1, 1].plot(time_values, current_values)
axes[1, 1].set_title("Discharge Current vs Time")
axes[1, 1].set_xlabel("Time (minutes)")
axes[1, 1].set_ylabel("Current (A)")
axes[1, 1].grid(True)

plt.tight_layout()

# Save figure
plt.savefig(
    "figures/battery_curves.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Battery plots generated successfully.")
print(f"Simulation duration: {elapsed_time / 60:.2f} minutes")
print(f"Final SoC: {battery.soc * 100:.2f}%")