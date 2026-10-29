from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Mesh
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/v06'
doc=App.openDocument(str(OUT/'myMicrobyte_enclosure_v06.FCStd'));doc.recompute()
checks=[]
for n in ['RearShell','FrontShell','PowerSlider','AcousticLid']:
 obj=doc.getObject(n+'_v06');path=OUT/(n+'_print.stl');m=Mesh.Mesh(str(path));bb=m.BoundBox
 err=abs(m.Volume-obj.Shape.Volume)/obj.Shape.Volume
 assert obj.Shape.isValid() and len(obj.Shape.Solids)==1 and m.isSolid() and not m.hasNonManifolds() and not m.hasSelfIntersections() and err<.01 and abs(bb.ZMin)<.001,n
 checks.append(dict(part=n,solid=True,non_manifold=False,self_intersection=False,volume_relative_error=err,bounds_mm=[bb.XLength,bb.YLength,bb.ZLength],sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
r=dict(native_reopen_recompute='passed',print_parts=checks,native_sha256=hashlib.sha256((OUT/'myMicrobyte_enclosure_v06.FCStd').read_bytes()).hexdigest())
(ROOT/'reports/v06/export_validation_v06.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
