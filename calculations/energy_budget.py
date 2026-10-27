#!/usr/bin/env python3
"""First-order energy budget in explicit SI-derived units; not a speed prediction."""
import json, math, argparse
from pathlib import Path

def energy_budget(area_m2, efficiency, irradiation_kwh_m2_day, system_factor,
                  hotel_kwh_day, motor_kw, battery_kwh, soc_span, discharge_efficiency):
    values = [area_m2, efficiency, irradiation_kwh_m2_day, system_factor,
              hotel_kwh_day, motor_kw, battery_kwh, soc_span, discharge_efficiency]
    if not all(math.isfinite(v) for v in values): raise ValueError('Inputs must be finite')
    if any(v < 0 for v in values): raise ValueError('Inputs must be non-negative')
    if motor_kw <= 0: raise ValueError('Motor power must be positive')
    if any(not 0 <= v <= 1 for v in [efficiency,system_factor,soc_span,discharge_efficiency]):
        raise ValueError('Efficiencies and SOC span must be between zero and one')
    pv = area_m2 * efficiency * irradiation_kwh_m2_day * system_factor
    remaining = pv - hotel_kwh_day
    usable = battery_kwh * soc_span * discharge_efficiency
    return dict(pv_kwh_day=pv, net_after_hotel_kwh_day=remaining,
                solar_motor_hours_day=max(0,remaining)/motor_kw,
                hotel_deficit_kwh_day=max(0,-remaining),
                usable_battery_kwh=usable, battery_motor_only_hours=usable/motor_kw,
                status='illustrative_not_design',
                limits='No weather chronology, storage charging losses, speed model or emergency reserve included')

def shaft_torque_nm(power_kw, rpm):
    if not math.isfinite(power_kw) or not math.isfinite(rpm) or power_kw<0 or rpm<=0:
        raise ValueError('Require finite non-negative power and positive rpm')
    return power_kw*1000/(2*math.pi*rpm/60)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',default=str(Path(__file__).with_name('illustrative_energy.json')))
    a=p.parse_args(); print(json.dumps(energy_budget(**json.loads(Path(a.input).read_text())),ensure_ascii=False,indent=2))
