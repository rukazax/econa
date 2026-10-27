#!/usr/bin/env python3
"""Reproducible preliminary panel comparison. SI units; no scantling approval."""
from pathlib import Path
import json, hashlib, math, platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'calculations/skin-comparison'; FIG=OUT/'figures'
OUT.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def polygon_area(points):
    if len(points)<3:return 0.
    return sum(np.linalg.norm(np.cross(points[i]-points[0],points[i+1]-points[0]))/2 for i in range(1,len(points)-1))
def clip(poly,z):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        ina=a[2]<=z;inb=b[2]<=z
        if ina:out.append(a)
        if ina!=inb:out.append(a+(b-a)*(z-a[2])/(b[2]-a[2]))
    return out
source=ROOT/'models/ECONA/ECONA_ECONA.FCStd'
passport=json.loads((ROOT/'calculations/closed-hulls/source.json').read_text())
assert sha(source)==passport['disk_sha256'], 'Source CAD changed: re-export skins before comparing materials'
areas=[]
for side in ['PortSkin','StarboardSkin']:
    pth=ROOT/'calculations/closed-hulls'/f'{side}-mesh.json'
    mesh=json.loads(pth.read_text());v=np.array(mesh['vertices'])/1000
    full=wet=0.
    for face in mesh['faces']:
        pts=list(v[face]);full+=polygon_area(pts);wet+=polygon_area(clip(pts,.52-.486100006))
    expected=next(r['area_m2'] for r in passport['skins'] if r['name']==side)
    assert abs(full-expected)<1e-5,(side,full,expected)
    areas.append({'side':side,'mesh_sha256':sha(pth),'total_m2':full,'below_052_m2':wet,'above_052_m2':full-wet})
A=sum(r['total_m2'] for r in areas);Aw=sum(r['below_052_m2'] for r in areas);Ad=A-Aw

# E1,E2,G12,G13,G23 Pa. Values tagged individually; G is never inferred from compression.
materials={
 'pine':{'rho':500,'E1':10e9,'E2':.5e9,'G12':.6e9,'G13':.6e9,'G23':.06e9,'nu12':.30,'status':'scenario, clear dry wood; species/grade/moisture not selected','limits_MPa':[20,2,3]},
 'fsf':{'rho':680,'E1':7e9,'E2':3e9,'G12':.6e9,'G13':.45e9,'G23':.45e9,'nu12':.20,'status':'E: SVEZA FSF minimum for 6.5-40 mm; extrapolation for 3-6 mm. Density/G/strength screening assumptions','limits_MPa':[20,10,3]},
 'glass':{'rho':None,'E1':20e9,'E2':14e9,'G12':4.5e9,'G13':3e9,'G23':3e9,'nu12':.16,'status':'wet-layup T11/epoxy scenario, not measured laminate properties','limits_MPa':[80,60,25]},
 'XPS':{'rho':45,'E1':20e6,'E2':20e6,'G12':6e6,'G13':6e6,'G23':6e6,'nu12':.25,'status':'E: H25 historical Technoplex analogue; G=6 MPa hypothetical sensitivity midpoint, NOT measured XPS property','shear_strength_MPa':None},
 'EPS':{'rho':30,'E1':10e6,'E2':10e6,'G12':6e6,'G13':6e6,'G23':6e6,'nu12':.25,'status':'E/density scenario; generic EPS G range 4-10 MPa in INNER-069; not a product passport','shear_strength_MPa':None},
 'PIR':{'rho':40,'E1':20e6,'E2':20e6,'G12':10e6,'G13':10e6,'G23':10e6,'nu12':.25,'status':'hypothetical E/G scenario; generic PUR data do not qualify PIR boards','shear_strength_MPa':None},
 'PVC':{'rho':80,'E1':80e6,'E2':80e6,'G12':23e6,'G13':23e6,'G23':23e6,'nu12':.25,'status':'Divinycell H80: nominal density, minimum compressive E used as in-plane isotropic analogue; minimum G and shear strength at 23C','shear_strength_MPa':.95},
 'SAN':{'rho':85,'E1':78e6,'E2':78e6,'G12':34e6,'G13':34e6,'G23':34e6,'nu12':.25,'status':'Corecell M80: typical E/G/strength, NOT guaranteed minimum; compressive E used as in-plane analogue','shear_strength_MPa':1.15},
 'balsa':{'rho':155,'E1':100e6,'E2':100e6,'G12':166e6,'G13':166e6,'G23':166e6,'nu12':.25,'status':'Diab ProBalsa 2022 nominal density/G=24076 psi converted to 166 MPa/shear=435 psi converted to 3 MPa; in-plane E scenario, not out-of-plane compression E','shear_strength_MPa':3.0},
}

# Additional light/medium structural grades; keep construction foams separate.
for key,rho,ec,gg,strength,base in [
 ('PVC45',48,45,12,.46,'PVC'),('PVC60',60,60,16,.63,'PVC'),('PVC100',100,115,28,1.4,'PVC'),
 ('SAN60',65,48,23,.78,'SAN'),('SAN100',107.5,112,44,1.47,'SAN')]:
    materials[key]={**materials[base],'rho':rho,'E1':ec*1e6,'E2':ec*1e6,'G12':gg*1e6,'G13':gg*1e6,'G23':gg*1e6,'shear_strength_MPa':strength,'status':f'{key}: same passport basis as {base}; rho nominal, E compressive analogue, G/shear minimum for PVC and typical for SAN'}

inputs={'date':'2026-10-11','user_pine_layers_mm':[8,8,8],'user_relative_angles_deg':[0,45,90],
 'absolute_angle_assumption':'outside to inside, first layer longitudinal X; no user confirmation of absolute orientation',
 'user_external_T11_layers':{'below_052':3,'above_052':2},'fabric_dry_kg_m2':.385,'fiber_density_kg_m3':2550,'resin_density_kg_m3':1150,
 'resin_fiber_mass_ratio':1.,'resin_ratio_sensitivity':[.7,1.,1.4],
 'glue_kg_m2_per_wood_or_core_interface':.22,'wood_sealing_kg_m2_per_face':.15,'finish_kg_m2':{'below':.6,'above':.4},
 'installed_joint_patch_allowance_fraction':.10,'procurement_waste_fraction':.15,
 'pressure_Pa':20000,'span_m':.6,'deflection_limit_span_divisor':100,
 'pressure_sensitivity_Pa':[10000,20000,40000],'span_sensitivity_m':[.4,.6,.8],
 'core_thickness_grid_mm':[15,20,25,30,40,50],'fsf_face_grid_mm':[3,4,6,8],'pine_inner_face_grid_mm':[4,6,8,10],
 'inner_glass_layer_grid':[2,3,4,6],
 'source_cad_sha256':sha(source),'materials':materials,
 'scope':'independent flat one-way strips in X/Y with full ABD coupling, free membrane resultants; transverse shear added; no shell curvature, frame stiffness, impact, fatigue, fracture, bond failure or whole-vessel strength solved',
 'screening_strength_limits':'assigned reduced scenario stresses, not regulatory allowables. Core shear threshold min/3 only for PVC; typical/3 for SAN conditional. Other foams/balsa unqualified.'}

def qb(mat,angle):
    m=materials[mat];e1,e2,g,nu=[m[k] for k in ('E1','E2','G12','nu12')];den=1-nu*nu*e2/e1
    q11=e1/den;q22=e2/den;q12=nu*e2/den;q66=g
    c=np.cos(np.radians(angle));s=np.sin(np.radians(angle));c2=c*c;s2=s*s
    a=q11*c2*c2+2*(q12+2*q66)*s2*c2+q22*s2*s2
    b=q11*s2*s2+2*(q12+2*q66)*s2*c2+q22*c2*c2
    d=(q11+q22-4*q66)*s2*c2+q12*(s2*s2+c2*c2)
    e=(q11-q12-2*q66)*c*c*c*s-(q22-q12-2*q66)*c*s*s*s
    f=(q11-q12-2*q66)*c*s*s*s-(q22-q12-2*q66)*c*c*c*s
    h=(q11+q22-2*q12-2*q66)*s2*c2+q66*(s2*s2+c2*c2)
    return np.array([[a,d,e],[d,b,f],[e,f,h]])
def layers(c,wet=True,resin_ratio=1.):
    outer=3 if wet else 2;tply=.385/2550+.385*resin_ratio/1150
    lst=[('glass',tply,0)]*outer
    if c['family']=='pine24':lst += [('pine',.008,a) for a in c.get('angles',[0,45,90])]
    elif c['family']=='fsf_solid':lst += [('fsf',c['face_out']/1000,0)]
    elif c['family'] in ('wood_foam','hybrid'):
        lst += [('fsf',c['face_out']/1000,0),(c['core'],c['core_mm']/1000,0),(c['inner'],c['face_in']/1000,0)]
    else:lst += [(c['core'],c['core_mm']/1000,0)]+[('glass',tply,0)]*c['inner_layers']
    return lst
def panel(c,pres=20000,span=.6,wet=True,resin_ratio=1.,g_xps=None):
    lst=layers(c,wet,resin_ratio);th=sum(t for _,t,_ in lst);z=-th/2
    aa=np.zeros((3,3));bb=aa.copy();dd=aa.copy();records=[]
    for mat,t,ang in lst:
        q=qb(mat,ang);z2=z+t;aa+=q*t;bb+=q*(z2*z2-z*z)/2;dd+=q*(z2**3-z**3)/3;records.append((mat,ang,z,z2,q));z=z2
    de=dd-bb@np.linalg.solve(aa,bb);di=np.linalg.inv(de)
    dx=1/di[0,0];dy=1/di[1,1];mx=pres*span**2/8;v=pres*span/2
    core=c.get('core');tc=c.get('core_mm',0)/1000
    if core:
        gg=g_xps if core=='XPS' and g_xps is not None else materials[core]['G13'];ks=gg*tc;tau=v/tc/1e6
        strength=materials[core].get('shear_strength_MPa');core_util=tau/(strength/3) if strength else None
    else:
        gx=[];gy=[]
        for mat,t,a in lst:
            prop=materials[mat];co=np.cos(np.radians(a))**2;si=1-co
            gx.append(t*(co/prop['G13']+si/prop['G23']));gy.append(t*(si/prop['G13']+co/prop['G23']))
        ks=min((5/6)*th*th/sum(gx),(5/6)*th*th/sum(gy));tau=1.5*v/th/1e6;core_util=None
    shear=pres*span**2/(8*ks);wx=5*pres*span**4/(384*dx)+shear;wy=5*pres*span**4/(384*dy)+shear
    util=0.;maxstress=0.;coupling=0.
    for axis in [0,1]:
        moment=np.zeros(3);moment[axis]=mx;k=di@moment;eps=-np.linalg.solve(aa,bb@k)
        coupling=max(coupling,abs(k[2]/k[axis]))
        for mat,ang,z1,z2,q in records:
            if mat not in ['pine','fsf','glass']:continue
            co=np.cos(np.radians(ang));si=np.sin(np.radians(ang));lim=materials[mat]['limits_MPa']
            for z in [z1,z2]:
                sx,sy,txy=q@(eps+z*k)/1e6
                local=[co*co*sx+si*si*sy+2*co*si*txy,si*si*sx+co*co*sy-2*co*si*txy,-co*si*sx+co*si*sy+(co*co-si*si)*txy]
                util=max(util,max(abs(a)/b for a,b in zip(local,lim)));maxstress=max(maxstress,max(abs(a) for a in local))
    return {'thickness_mm':th*1000,'D_x_Nm':dx,'D_y_Nm':dy,'deflection_x_mm':wx*1000,'deflection_y_mm':wy*1000,'shear_deflection_mm':shear*1000,'face_stress_max_MPa':maxstress,'face_screen_util':util,'core_shear_MPa':tau if core else None,'core_screen_util':core_util,'twist_curvature_ratio':coupling,'stiffness_screen':max(wx,wy)<=span/100,'face_screen':util<=1,'core_screen':core_util<=1 if core_util is not None else None}
def mass(c,wet,resin_ratio=1.):
    n=3 if wet else 2;g=n*.385*(1+resin_ratio);wood=core=0.
    if c['family']=='pine24':wood=.024*500;glue=.44;seal=.3
    elif c['family']=='fsf_solid':wood=c['face_out']*.001*680;glue=0;seal=.3
    elif c['family'] in ['wood_foam','hybrid']:
        wood=c['face_out']*.001*680+c['face_in']*.001*materials[c['inner']]['rho'];core=c['core_mm']*.001*materials[c['core']]['rho'];glue=.44;seal=.3
    else:
        g+=c['inner_layers']*.385*(1+resin_ratio);core=c['core_mm']*.001*materials[c['core']]['rho'];glue=.44;seal=0
    finish=.6 if wet else .4
    return {'wood':wood,'core':core,'glass_and_laminating_resin':g,'bond':glue,'sealing':seal,'finish':finish,'total':wood+core+g+glue+seal+finish}
families={'pine24':'Сосна 8/8/8, 0/45/90°','fsf_solid':'ФСФ монолит','wood_foam':'ФСФ / пена / ФСФ','hybrid':'ФСФ / пена / сосна','glass_foam':'Стекло / сердечник / стекло'}
candidates=[{'family':'pine24','name':'Сосна 8/8/8 мм; 0/45/90°'},*[{'family':'fsf_solid','face_out':t,'name':f'ФСФ {t} мм'} for t in [6,9,12,15,18,21,24,27,30,36]]]
for core in ['XPS','EPS','PIR','PVC']:
    for t in inputs['core_thickness_grid_mm']:
        for fo in inputs['fsf_face_grid_mm']:
            for fi in inputs['fsf_face_grid_mm']:
                candidates.append({'family':'wood_foam','core':core,'core_mm':t,'inner':'fsf','face_out':fo,'face_in':fi,'name':f'ФСФ {fo} / {core} {t} / ФСФ {fi}'})
            for fi in inputs['pine_inner_face_grid_mm']:
                candidates.append({'family':'hybrid','core':core,'core_mm':t,'inner':'pine','face_out':fo,'face_in':fi,'name':f'ФСФ {fo} / {core} {t} / сосна {fi}'})
for core in ['PVC','SAN','balsa','PVC45','PVC60','PVC100','SAN60','SAN100']:
    for t in inputs['core_thickness_grid_mm']:
        for ni in inputs['inner_glass_layer_grid']:
            candidates.append({'family':'glass_foam','core':core,'core_mm':t,'inner_layers':ni,'name':f'Т11 / {core} {t} / Т11 {ni} слоя внутри'})
for i,c in enumerate(candidates):
    c['id']=i;c['wet']=panel(c);c['dry']=panel(c,wet=False)
    c['mass_wet']=mass(c,True);c['mass_dry']=mass(c,False)
    c['net_shell_kg']=Aw*c['mass_wet']['total']+Ad*c['mass_dry']['total'];c['installed_shell_kg']=1.1*c['net_shell_kg']
    c['screen_pass']=all(r['stiffness_screen'] and r['face_screen'] and r['core_screen'] is not False for r in [c['wet'],c['dry']])
    c['qualification']='documented core min (panel still untested)' if c.get('core','').startswith('PVC') else 'typical core data (panel still untested)' if c.get('core','').startswith('SAN') or c.get('core')=='balsa' else 'core unqualified' if c.get('core') else 'wood grade and wet adhesive unqualified'

groups=[('pine24',None),('fsf_solid',None),('wood_foam','XPS'),('hybrid','XPS'),('wood_foam','EPS'),('wood_foam','PIR'),('wood_foam','PVC'),('glass_foam','PVC'),('glass_foam','SAN'),('glass_foam','balsa')]
best=[]
for fam,core in groups:
    pool=[c for c in candidates if c['family']==fam and c.get('core')==core]
    passed=[c for c in pool if c['screen_pass']]
    selected=min(passed or pool,key=lambda c:c['installed_shell_kg']).copy();selected['group_pass_count']=len(passed);selected['group_count']=len(pool);best.append(selected)
grade_best=[]
for core in ['PVC45','PVC60','PVC','PVC100','SAN60','SAN','SAN100']:
    pool=[c for c in candidates if c['family']=='glass_foam' and c['core']==core and c['screen_pass']]
    grade_best.append(min(pool,key=lambda c:c['installed_shell_kg']))
sens=[]
for c in best:
    for p0 in inputs['pressure_sensitivity_Pa']:
        for l0 in inputs['span_sensitivity_m']:
            r=panel(c,p0,l0,wet=False);sens.append({'id':c['id'],'pressure_Pa':p0,'span_m':l0,**r})
xps_sens=[]
for c in best:
    if c.get('core')=='XPS':
        for g in [3e6,6e6,10e6]:xps_sens.append({'id':c['id'],'G_MPa':g/1e6,**panel(c,wet=False,g_xps=g)})
orientation=[]
for ang in [[0,45,90],[-45,0,45],[0,90,0]]:
    c={'family':'pine24','angles':ang};orientation.append({'angles_deg':ang,**panel(c,wet=False)})
resin=[]
for c in best:
    for rr in inputs['resin_ratio_sensitivity']:
        m=1.1*(Aw*mass(c,True,rr)['total']+Ad*mass(c,False,rr)['total']);resin.append({'id':c['id'],'ratio':rr,'installed_shell_kg':m,**panel(c,wet=False,resin_ratio=rr)})
result={'geometry':{'source_cad_sha256':sha(source),'areas':areas,'total_m2':A,'below_052_m2':Aw,'above_052_m2':Ad,'scope':'only exported PortSkin/StarboardSkin, excludes computational caps/deck/transom construction not in skins'},'enumerated_count':len(candidates),'selected':best,'grade_selected':grade_best,'candidates':candidates,'panel_sensitivity':sens,'xps_G_sensitivity':xps_sens,'pine_orientation_sensitivity':orientation,'resin_sensitivity':resin,'external_fabric_dry_kg':.385*(3*Aw+2*Ad),'external_fabric_procurement_m2':1.15*(3*Aw+2*Ad),'checks':{'skin_area_matches_CAD':True,'positive_ABD':all(c['dry']['D_x_Nm']>0 and c['dry']['D_y_Nm']>0 for c in candidates),'python':platform.python_version(),'numpy':np.__version__}}
(OUT/'inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2));(OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=lambda v:v.item()))

fig,ax=plt.subplots(figsize=(10,5.5));labels=[c['name'].replace(' слоя внутри',' вн.').replace('Т11 / ','') for c in best];y=np.arange(len(best));colors=['#bb7d39' if c['family']=='pine24' else '#568b9c' if c.get('core') in ['PVC','SAN'] else '#99a483' for c in best]
ax.barh(y,[c['installed_shell_kg'] for c in best],color=colors);ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlabel('Оба поплавка: обшивка + 10% стыки, кг');ax.set_title('Минимальная масса среди прошедших сценарный экран\n20 кПа, пролёт 0,6 м; это не допуск к эксплуатации');ax.grid(axis='x',alpha=.25)
for i,c in enumerate(best):ax.text(c['installed_shell_kg']+15,i,f"{c['installed_shell_kg']:.0f}"+(' *' if c.get('core') not in ['PVC','SAN','balsa',None] else ''),va='center')
ax.set_xlim(0,max(c['installed_shell_kg'] for c in best)*1.15);fig.tight_layout();fig.savefig(FIG/'mass-comparison.png',dpi=170);plt.close(fig)

fig,axs=plt.subplots(2,2,figsize=(10,7));sketches=[('Сосна: 8 / 8 / 8 мм', [('Т11: 3 снизу / 2 сверху',2,'#7bb5c4'),('сосна 8 мм · 0°',8,'#dcbd8b'),('сосна 8 мм · 45°',8,'#cfa474'),('сосна 8 мм · 90°',8,'#dcbd8b')]),('ФСФ / пена / ФСФ',[('Т11: 3 / 2 слоя',2,'#7bb5c4'),('наружная ФСФ',4,'#cfa474'),('сердечник',30,'#e4edf0'),('внутренняя ФСФ',4,'#cfa474')]),('ФСФ / пена / сосна',[('Т11: 3 / 2 слоя',2,'#7bb5c4'),('наружная ФСФ',4,'#cfa474'),('сердечник',30,'#e4edf0'),('сосна, вдоль X',6,'#dcbd8b')]),('Стекло / пена / стекло',[('наружная Т11: 3 / 2',2,'#7bb5c4'),('PVC или SAN',30,'#e4edf0'),('внутренняя Т11: расчёт',2,'#7bb5c4')])]
for ax,(title,ls) in zip(axs.flat,sketches):
    h=0
    for label,t,col in reversed(ls):
        height=max(t,4);ax.add_patch(Rectangle((0,h),1,height,facecolor=col,edgecolor='#314c5b'));ax.text(.03,h+height/2,label,va='center',fontsize=9);h+=height
    ax.annotate('ВОДА / НАРУЖУ',(.5,h+2),ha='center',fontsize=9);ax.set_xlim(-.02,1.02);ax.set_ylim(-2,h+9);ax.axis('off');ax.set_title(title,fontsize=11)
fig.suptitle('Эскизы пакетов · не в масштабе · эпоксидные швы между слоями',fontsize=12);fig.tight_layout();fig.savefig(FIG/'layer-sketches.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5))
for c in [best[0],best[2],best[3],best[7],best[8]]:
    ls=np.linspace(.3,.9,40);ax.plot(ls,[max(panel(c,span=l,wet=False)[k] for k in ['deflection_x_mm','deflection_y_mm']) for l in ls],label=c['name'].replace(' слоя внутри',' вн.'))
ax.plot(ls,ls*10,'k--',label='Выбранный экран L/100');ax.set_ylim(0,25);ax.set_xlabel('Свободный пролёт, м');ax.set_ylabel('Прогиб слабого направления, мм');ax.set_title('Надводная зона, 20 кПа: чувствительность к шагу опор');ax.legend(fontsize=8);ax.grid(alpha=.25);fig.tight_layout();fig.savefig(FIG/'span-sensitivity.png',dpi=170);plt.close(fig)

fig,ax=plt.subplots(figsize=(10,4.5));v=json.loads((ROOT/'calculations/closed-hulls/PortSkin-mesh.json').read_text());verts=np.array(v['vertices'])/1000;ax.scatter(verts[:,0],verts[:,2]+.486100006,s=1,c=verts[:,2]+.486100006,cmap='cividis');ax.axhline(.52,c='#267f78',lw=2,label='Граница 3 / 2 слоя: T = 0,52 м');ax.text(.3,.27,f'3 слоя Т11 · {Aw:.2f} м², оба поплавка',fontsize=11);ax.text(6,1.5,f'2 слоя Т11 · {Ad:.2f} м²',fontsize=11);ax.set_xlabel('X исходной модели, м');ax.set_ylabel('Высота над основной плоскостью, м');ax.set_title('Зоны наружной оклейки на существующей обшивке');ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(FIG/'coating-zones.png',dpi=180);plt.close(fig)
print(json.dumps({'area':result['geometry'],'fabric_dry_kg':result['external_fabric_dry_kg'],'count':len(candidates),'best':[{'id':c['id'],'name':c['name'],'mass':round(c['installed_shell_kg'],1),'pass':bool(c['screen_pass']),'w_mm':round(max(c['dry']['deflection_x_mm'],c['dry']['deflection_y_mm']),2),'face_util':round(c['dry']['face_screen_util'],2)} for c in best]},ensure_ascii=False,indent=2))
