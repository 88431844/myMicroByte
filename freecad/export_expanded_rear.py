import sys,json
from pathlib import Path
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part,MeshPart
root=Path(__file__).resolve().parents[1]
d=A.openDocument(str(root/'reports/battery_expansion/enlarged_frame_study.FCStd'))
s=d.RearShell_v10.Shape
assert s.isValid() and len(s.Solids)==1
assert d.BatteryFrameInner.Length.Value==57 and d.BatteryFrameInner.Width.Value==32
b=s.BoundBox
print("rear bounds",b,flush=True)
pack=Part.makeBox(56,31,3.3,A.Vector(-33.5,-19.8,1.7))
assert pack.common(s).Volume<1e-5
sh=s.copy();sh.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
m=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.025,AngularDeflection=.10,Relative=False)
err=abs(m.Volume-s.Volume)/s.Volume
assert m.isSolid() and not m.hasNonManifolds() and not m.hasSelfIntersections() and err<.001
out=root/'printing/A1_blue_PLA_expanded_rear_2'
for n in (1,2):m.write(str(out/f'RearExpanded_{n}.stl'))
r=dict(valid=True,solids=1,frame_inner=[57,32],pack_max=[56,31,3.3],mesh_volume_error=err,bounds=[b.XLength,b.YLength,b.ZLength],orientation='rear exterior down, interior up',count=2)
(root/'reports/expanded_rear_2/model_validation.json').write_text(json.dumps(r,indent=2))
print(r)
