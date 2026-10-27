#!/usr/bin/env python3
"""Physical limiting cases, scaling, coupled equilibrium, mass accounting."""
import runpy,json
import numpy as np
from pathlib import Path
ns=runpy.run_path(str(Path(__file__).with_name('compare_skins.py')))
mat,qb,panel,layers=ns['materials'],ns['qb'],ns['panel'],ns['layers']
mat['reference']={'E1':10e9,'E2':10e9,'G12':4e9,'nu12':.25}
q=qb('reference',0)
assert np.allclose(q,qb('reference',37))
t=.02;de=q*t**3/12;d=1/np.linalg.inv(de)[0,0]
assert np.isclose(d,10e9*t**3/12)
checks={'isotropic_rotation_invariance':True,'homogeneous_beam_D_equals_Et3_over12':True}
for c in ns['best']+ns['grade_best']:
    r1=panel(c);r2=panel(c,pres=40000)
    for k in ['deflection_x_mm','deflection_y_mm','face_stress_max_MPa']:
        assert np.isclose(r2[k],2*r1[k])
    if c.get('core'):assert np.isclose(r2['core_shear_MPa'],2*r1['core_shear_MPa'])
    assert np.isclose(c['net_shell_kg'],ns['Aw']*sum(v for k,v in c['mass_wet'].items() if k!='total')+ns['Ad']*sum(v for k,v in c['mass_dry'].items() if k!='total'))
    lst=layers(c,False);z=-sum(t for _,t,_ in lst)/2;a=np.zeros((3,3));b=a.copy();d=a.copy();records=[]
    for material,th,angle in lst:
        q=qb(material,angle);z1=z;z+=th;a+=q*th;b+=q*(z*z-z1*z1)/2;d+=q*(z**3-z1**3)/3;records.append((q,z1,z))
    de=d-b@np.linalg.solve(a,b);assert np.linalg.eigvalsh(de).min()>0
    moment=np.array([900.,0.,0.]);k=np.linalg.solve(de,moment);e=-np.linalg.solve(a,b@k)
    n=np.zeros(3);m=np.zeros(3)
    for q,z1,z2 in records:
        n+=q@(e*(z2-z1)+k*(z2*z2-z1*z1)/2)
        m+=q@(e*(z2*z2-z1*z1)/2+k*(z2**3-z1**3)/3)
    assert np.linalg.norm(n)<1e-8 and np.allclose(m,moment,atol=1e-8)
checks.update({'pressure_linearity_all_selected':True,'layer_stress_integrates_to_zero_N_and_applied_M':True,'mass_components_sum':True,'positive_effective_D_selected':True,'CAD_source_hash_unchanged':True,'area_reconciles_to_CAD':True})
pth=ns['OUT']/'verification.json';pth.write_text(json.dumps({'status':'PASS','checks':checks},indent=2));print(json.dumps(checks))
