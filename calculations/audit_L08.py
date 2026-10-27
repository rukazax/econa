#!/usr/bin/env python3
"""Arithmetic reproduction of L08; not validation of RRR rules or an ECONA design."""
import json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def calculate():
    h,L,B,T,H,lam=2.,10.7,1.3,.7,1.6,20.
    base=30.8*h*L*B/lam
    alpha=.81
    return {
        'scope':'Arithmetic of the formulas printed in L08 only; rule coefficients are not independently validated',
        'source':'library/user/L08.pdf',
        'M1_kNm':-.5*11.3*B-45.1*1.4,
        'M2_kNm':-11.3*(.5*(B+1.51)-.35)-45.1*1.4,
        'M3_as_substituted_kNm':base*(T*(H-T/2)*.642-B**2*.745/12),
        'M3_using_defined_m1_m6_kNm':base*(T*(H-T/2)*.745-B**2*.642/12),
        'Tprime_with_T_kN':base*T*.745,
        'Tprime_missing_T_kN':base*.745,
        'Ttriple_prime_multiplier_with_T_kN':base*T,
        'Ttriple_prime_multiplier_printed_without_T_kN':base,
        'm2_correction_coefficient':(.57+.33*alpha)*.065**2,
        'm3_correction_coefficient':1.4*(alpha*.065)**2,
        'm4_correction_coefficient':(1.5-.1*alpha**2)*.065**2,
        'm2prime_factor_at_phi15':1-(.57+.33*alpha)*(.065*math.sin(math.radians(15)))**2,
        'm2prime_printed_factor_at_phi15':6.874e-4*math.sin(math.radians(15))**2,
        'm3prime_factor_at_phi15':1-1.4*(alpha*.065*math.sin(math.radians(15)))**2,
        'm3prime_printed_factor_at_phi15':.996*math.sin(math.radians(15))**2,
        'page7_sigma_MPa':150000/(18776*1e-6)/1e6,
    }

if __name__=='__main__':
    result=calculate()
    (ROOT/'calculations/L08_arithmetic_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
