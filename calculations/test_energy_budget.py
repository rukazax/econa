import math
import pytest
from energy_budget import energy_budget, shaft_torque_nm

def example(**changes):
    data=dict(area_m2=30,efficiency=.22,irradiation_kwh_m2_day=4,system_factor=.75,
              hotel_kwh_day=6,motor_kw=10,battery_kwh=20,soc_span=.8,discharge_efficiency=.95)
    data.update(changes);return energy_budget(**data)

def test_hand_calculated_energy_and_storage():
    r=example();assert r['pv_kwh_day']==pytest.approx(19.8)
    assert r['solar_motor_hours_day']==pytest.approx(1.38)
    assert r['usable_battery_kwh']==pytest.approx(15.2)

def test_dark_day_preserves_hotel_deficit():
    r=example(irradiation_kwh_m2_day=0)
    assert r['solar_motor_hours_day']==0 and r['hotel_deficit_kwh_day']==6

@pytest.mark.parametrize('changes',[{'motor_kw':0},{'efficiency':1.1},{'area_m2':-1},{'battery_kwh':math.nan}])
def test_invalid_inputs_rejected(changes):
    with pytest.raises(ValueError):example(**changes)

def test_shaft_power_conservation():
    q=shaft_torque_nm(10,600)
    assert q==pytest.approx(159.154943)
    assert q*(2*math.pi*600/60)==pytest.approx(10000)
