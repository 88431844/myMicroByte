"""Geometric insertion/retention audit, not an elastic stress or fatigue simulation."""
from pathlib import Path
import sys,json
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part
ROOT=Path(__file__).resolve().parents[1]
d=App.openDocument(str(ROOT/'output/v08/myMicrobyte_enclosure_v08.FCStd'))
slide=d.PowerSlider_v08.Shape
keepers=[d.SliderKeeper0.Shape,d.SliderKeeper1.Shape]
fixed=d.RearRigidWithoutSpeakerSprings.Shape
refs=[o.Shape for o in d.PCBReference.Group if o.Name not in ['Ref_SW3','Speaker_1510']]
refs.append(d.Ref_SW3.Shape.common(Part.makeBox(10,14,5,App.Vector(29.5,-12,6))))
flexed=[]
for k in keepers:
 m=App.Matrix();m.A13=.3/(10.45-4.25);m.A14=-4.25*m.A13
 flexed.append(k.transformGeometry(m))
obstacles=Part.makeCompound([fixed]+refs+flexed)
maxvol=0;fail=[]
for iz in range(121):
 z=iz*.1
 s=slide.copy();s.translate(App.Vector(0,0,z))
 vol=s.common(obstacles).Volume;maxvol=max(maxvol,vol)
 if vol>.001:fail.append({'insertion_z':z,'volume':vol})
# Prove geometric retention for whole travel and both limits of lateral guide play.
# Raise flange by 0.20 mm: 0.15 mm nominal free play followed by 0.05 mm engagement.
retained=[]
for iy in range(37):
 dy=-.55+iy*.1
 for dx in [-.15,0,.25]:
  s=slide.copy();s.translate(App.Vector(dx,dy,.20))
  overlap=s.common(Part.makeCompound(keepers)).Volume
  retained.append(overlap)
  if overlap<.0001:fail.append({'unretained_y':dy,'x_play':dx,'overlap':overlap})
# Above the attached root, deflected clips must have space in the printed wall.
free=Part.makeBox(10,40,20,App.Vector(38,-20,4.45))
clipwall=[k.common(free).common(fixed).Volume for k in flexed]
if max(clipwall)>.001:fail.append({'flexed_keeper_wall_collision':clipwall})
report={'revision':'0.8','insertion':{'direction':'vertical, rest Y, keepers spread outward','sample_spacing_mm':.1,'range_mm':[0,12],'keeper_tip_spread_mm':.3,'max_overlap_volume_mm3':maxvol},'retention':{'sampled_y_range_mm':[-.55,3.05],'sampled_x_play_mm':[-.15,0,.25],'nominal_vertical_play_mm':.15,'vertical_retention_probe_mm':.2,'minimum_hook_overlap_mm3':min(retained)},'flexed_keeper_vs_wall_overlap_mm3':clipwall,'failures':fail,'limitations':['Affine shear is only a clearance approximation, not finite element analysis.','Printed tab strength, PLA flex fatigue, actual switch end positions and actuation must be tested.','Guide animation does not animate tab deformation.']}
(ROOT/'reports/v08/slider_install_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
assert not fail
