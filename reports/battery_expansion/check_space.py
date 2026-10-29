import sys,json,math
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
D=A.openDocument('output/v10/myMicrobyte_enclosure_v10.FCStd')
refs=[]
for g in [D.PCBReference,D.ConnectorKeepouts,D.Hardware_v10]:
 refs.extend(o for o in g.Group if not o.Name.startswith('Battery'))
refs=list({o.Name:o for o in refs}.values())
# Assess a wider frame in an in-memory copy; preserve the existing/printing files.
D.BatteryFrameInner.Length=57;D.BatteryFrameInner.Width=32;D.BatteryFrameInner.Placement.Base=A.Vector(-34,-20.3,1.2)
D.BatteryFrameOuter.Length=59.4;D.BatteryFrameOuter.Width=34.4;D.BatteryFrameOuter.Placement.Base=A.Vector(-35.2,-21.5,1.3)
D.recompute()
rear=D.RearShell_v10.Shape
results=[]
for name,l,w,t,x,y in [('existing',51,29,3.3,-29.5,-18.4),('larger_target',56,31,3.3,-33.5,-19.8),('length_edge',57,30,3.3,-34,-19),('width_edge',56,32,3.3,-33.5,-20.3),('303050_nominal',50,30,3,-30,-19),('303055_nominal',55,30,3,-33,-19),('thicker_pack',56,31,3.5,-33.5,-19.8),('merchant_measured',47.36,30.61,2.97,-30,-19.6)]:
 s=Part.makeBox(l,w,t,A.Vector(x,y,1.7));hits=[];gaps=[]
 for o in refs:
  a=s.BoundBox;b=o.Shape.BoundBox
  gap=math.sqrt(sum(max(0,getattr(a,k+"Min")-getattr(b,k+"Max"),getattr(b,k+"Min")-getattr(a,k+"Max"))**2 for k in "XYZ"));gaps.append((round(gap,4),o.Name))
  if gap<1e-6:
   vol=s.common(o.Shape).Volume
   if vol>1e-4:hits.append((o.Name,vol))
 shellvol=s.common(rear).Volume
 print(name,shellvol,flush=True)
 results.append(dict(name=name,pack_mm=[l,w,t],min_corner=[x,y,1.7],reference_intersections=hits,rear_intersection_mm3=shellvol,nearest=sorted(gaps)[:7],distance_method="conservative_axis_aligned_bounds"))
frame_hits=[]
for o in refs:
 if D.BatteryFrame.Shape.BoundBox.intersect(o.Shape.BoundBox):
  vol=D.BatteryFrame.Shape.common(o.Shape).Volume
  if vol>1e-4:frame_hits.append((o.Name,vol))
report={'frame_intersections':frame_hits,'frame_inner_mm':[57,32],'rear_valid':rear.isValid(),'rear_solids':len(rear.Solids),'cases':results,'not_applied_to_printing_job':True}
Path('reports/battery_expansion/space_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
# Save separate feasibility document; no printable export and no change to v10.
D.Battery_ToleranceEnvelope.Shape=Part.makeBox(56,31,3.3,A.Vector(-33.5,-19.8,1.7))
D.Battery_ToleranceEnvelope.Label='扩容可行性检查 56×31×3.3（未定版）'
D.recompute();D.saveAs(str(Path('reports/battery_expansion/enlarged_frame_study.FCStd').resolve()))
