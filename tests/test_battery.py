import pytest

from env.battery import BatteryModel


def test_initial_state():
    battery = BatteryModel()

    assert battery.soc == 1.0
    assert battery.temp == 25.0
    assert battery.v1 == 0.0
    assert battery.stress == 0.0


def test_ocv_decreases_with_soc():
    battery = BatteryModel()

    high = battery.calculate_ocv(1.0)
    low = battery.calculate_ocv(0.2)

    assert high > low


def test_capacity_reduces_at_low_temperature():
    battery = BatteryModel()

    normal = battery.calculate_capacity(25)
    cold = battery.calculate_capacity(0)

    assert cold < normal


def test_peukert_effect():
    battery = BatteryModel()

    effective = battery.calculate_effective_current(10)

    assert effective > 10


def test_step_reduces_soc():
    battery = BatteryModel()

    initial_soc = battery.soc

    result = battery.step(150, 5)

    assert result["soc"] < initial_soc


def test_voltage_remains_positive():
    battery = BatteryModel()

    result = battery.step(150, 5)

    assert result["voltage"] > 0


def test_invalid_power():
    battery = BatteryModel()

    with pytest.raises(ValueError):
        battery.step(-100, 5)


def test_invalid_time():
    battery = BatteryModel()

    with pytest.raises(ValueError):
        battery.step(100, 0)
        
def test_reset_restores_initial_state():
    battery = BatteryModel()

    battery.step(150, 5)
    battery.reset()

    assert battery.soc == 1.0
    assert battery.temp == 25.0
    assert battery.v1 == 0.0
    assert battery.stress == 0.0


def test_thermal_switch():
    battery = BatteryModel(use_thermal=False)

    battery.step(150, 5)

    assert battery.temp == 25.0


def test_degradation_switch():
    battery = BatteryModel(use_degradation=False)

    battery.step(150, 5)

    assert battery.stress == 0.0


def test_rc_switch():
    battery = BatteryModel(use_rc=False)

    battery.step(150, 5)

    assert battery.v1 == 0.0


def test_invalid_ambient_temperature():
    battery = BatteryModel()

    with pytest.raises(ValueError):
        battery.step(100, 5, float("nan"))

def test_depleted_battery_does_not_supply_power():
    battery = BatteryModel()

    battery.soc = 0.0

    result = battery.step(150, 5)

    assert result["soc"] == 0.0
    assert result["current"] == 0.0