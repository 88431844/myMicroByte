"""Reopen native CAD and validate its print meshes without changing the model."""
from pathlib import Path
import sys, json, hashlib
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Mesh, Part

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/v03'
doc = App.openDocument(str(OUT / 'myMicrobyte_enclosure_v03.FCStd'))
doc.recompute()
objects = [('RearShell', doc.RearShell_v03), ('FrontShell', doc.FrontShell_v03),
           ('PowerSlider', doc.PowerSlider_v03)]
objects += [('Cap_' + o.Name[7:], o) for o in doc.Objects if o.Name.startswith('Button_')]
checks = []
for name, obj in objects:
    assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1, name
    path = OUT / (name + '_print.stl')
    mesh = Mesh.Mesh(str(path))
    error = abs(mesh.Volume - obj.Shape.Volume) / obj.Shape.Volume
    bounds = mesh.BoundBox
    assert mesh.isSolid() and error < .01 and abs(bounds.ZMin) < .001, name
    checks.append(dict(name=name, solid=True, volume_relative_error=error,
                       print_bounds_mm=[bounds.XLength, bounds.YLength, bounds.ZLength],
                       bed_z_min=bounds.ZMin, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))

# Check the advertised finished-pack allowance against the retained board,
# connector envelopes and shells, in addition to the nominal battery check.
b = doc.Battery_Assumed.Shape.BoundBox
cx, cy = (b.XMin + b.XMax) / 2, (b.YMin + b.YMax) / 2
pack = Part.makeBox(56, 36, 5, App.Vector(cx - 28, cy - 18, b.ZMin))
pack_checks = []
refs = list(doc.PCBReference.Group) + list(doc.ConnectorKeepouts.Group)
for obj in [doc.RearShell_v03, doc.FrontShell_v03] + refs:
    if obj.Name == 'Battery_Assumed' or obj.Shape.isNull():
        continue
    overlap = pack.common(obj.Shape).Volume if pack.BoundBox.intersect(obj.Shape.BoundBox) else 0
    pack_checks.append(dict(name=obj.Name, clearance_mm=pack.distToShape(obj.Shape)[0], overlap_mm3=overlap))

report = dict(native_reopen_recompute='passed', print_stl_count=len(checks), stl_checks=checks,
              native_sha256=hashlib.sha256((OUT/'myMicrobyte_enclosure_v03.FCStd').read_bytes()).hexdigest(),
              finished_pack_envelope_mm=[56,36,5], finished_pack_checks=pack_checks)
(ROOT/'reports/v03/export_validation_v03.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'print_stls':len(checks),'max_volume_relative_error':max(c['volume_relative_error'] for c in checks),
                  'pack_collisions':[c for c in pack_checks if c['overlap_mm3'] > .001],
                  'minimum_pack_clearances':sorted(pack_checks,key=lambda c:c['clearance_mm'])[:5]},ensure_ascii=False,indent=2))
