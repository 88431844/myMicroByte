"""Check the full 0.8 mm cap sweep and extract coupons from the saved design."""
from pathlib import Path
import sys, json
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, MeshPart, Mesh
ROOT=Path(__file__).resolve().parents[1]
source=App.openDocument(str(ROOT/'output/myMicrobyte_enclosure_v01.FCStd'))
source.recompute()
p=source.Parameters
num=lambda name:float(getattr(p,name))
caps=[o for o in source.Objects if o.Name.startswith('Cap_')]
references=[o for o in source.PCBReference.Group if hasattr(o,'Shape')]
result={'units':'mm','cap_travel_checked_mm':0.8,'scope':'Continuous cap sweep against shells, other caps, LCD and all retained fixed PCB models. The associated deforming switch is excluded; its real actuation travel remains unverified.','caps':[]}
for cap in caps:
 stem=source.getObject(cap.Name[4:]+'Stem')
 x,y=stem.Placement.Base.x,stem.Placement.Base.y
 sweep=[]
 for radius,z,h in [(num('StemR'),num('StemBottomZ'),num('FlangeBottomZ')-num('StemBottomZ')),
                    (num('FlangeR'),num('FlangeBottomZ'),num('FlangeT')),
                    (num('ButtonR'),num('FlangeBottomZ')+num('FlangeT'),num('ButtonTopZ')-num('FlangeBottomZ')-num('FlangeT'))]:
  sweep.append(Part.makeCylinder(radius,h+0.8,App.Vector(x,y,z-0.8)))
 swept=sweep[0].multiFuse(sweep[1:]).removeSplitter()
 obstacles=[source.RearShell,source.FrontShell]+[o for o in references if o.Label!=cap.Name[4:]]+[o for o in caps if o!=cap]
 collisions=[]
 for o in obstacles:
  if not swept.BoundBox.intersect(o.Shape.BoundBox):continue
  v=swept.common(o.Shape).Volume
  if v>0.001:collisions.append({'object':o.Label,'volume_mm3':v})
 own=next(o for o in references if o.Label==cap.Name[4:])
 result['caps'].append({'name':cap.Name,'rest_gap_to_switch_tip_mm':num('StemBottomZ')-own.Shape.BoundBox.ZMax,'collisions':collisions})
assert not any(row['collisions'] for row in result['caps']),result

# A conservative vertical bound, limited to the reference models and assumptions.
b=source.Battery_Assumed.Shape.BoundBox
covered=[]
for o in references:
 if o==source.Battery_Assumed:continue
 bb=o.Shape.BoundBox
 if bb.ZMin<=b.ZMin:continue
 if bb.XMin<b.XMax and bb.XMax>b.XMin and bb.YMin<b.YMax and bb.YMax>b.YMin:
  covered.append((bb.ZMin,o.Label))
lowest,label=min(covered)
result['battery_clearance']={'assumed_battery_mm':[b.XLength,b.YLength,b.ZLength],
 'lowest_overhead_reference':label,'overhead_min_z_mm':lowest,
 'battery_top_z_mm':b.ZMax,'reference_vertical_gap_mm':lowest-b.ZMax,
 'max_thickness_at_same_position_with_0_5mm_gap_mm':lowest-b.ZMin-0.5,
 'scope':'Bounding-box conservative estimate for retained models and provisional envelopes; excludes wires, solder and invalid omitted models.'}
fit=json.loads((ROOT/'reports/fit_check.json').read_text())
fit.pop('max_battery_height_at_center_mm',None)
fit['battery_clearance']=result['battery_clearance']
(ROOT/'reports/fit_check.json').write_text(json.dumps(fit,indent=2,ensure_ascii=False))

coupons=App.newDocument('myMicrobyte_Fit_Coupons')
objects=[]
def add(name,label,shape):
 assert shape.isValid() and len(shape.Solids)==1,name
 shape=shape.copy();bb=shape.BoundBox;shape.translate(App.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
 o=coupons.addObject('Part::Feature',name);o.Label=label;o.Shape=shape;objects.append(o)
 mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.04,AngularDeflection=0.1,Relative=False)
 assert mesh.isSolid(),name
 mesh.write(str(ROOT/'output'/('Fit_'+name+'.stl')))
 return o
a=source.AStem.Placement.Base
plate=source.FrontShell.Shape.common(Part.makeBox(10,10,num('Face'),App.Vector(a.x-5,a.y-5,num('FrontUnderZ'))))
plate.rotate(App.Vector(),App.Vector(1,0,0),180)
add('ButtonGuide','按钮导孔试片：实际前面板局部',plate)
post=source.FrontPost.Shape.cut(source.FrontPilot.Shape)
add('ScrewPilot','M2 预孔试柱：Ø1.7',post)
rear=source.RearShell.Shape.common(Part.makeBox(15,5.5,3.5,App.Vector(18,17,13)))
front=source.FrontShell.Shape.common(Part.makeBox(15,5.5,2.8,App.Vector(18,17,15.2)))
add('RearTongue','后壳止口试片',rear)
front.rotate(App.Vector(),App.Vector(1,0,0),180)
add('FrontReceiver','前壳止口试片',front)
# Space the four coupon objects for a readable native document.
for i,o in enumerate(objects):o.Placement.Base.x=i*20
coupons.recompute();coupons.saveAs(str(ROOT/'output/myMicrobyte_fit_coupons.FCStd'))
Part.export(objects,str(ROOT/'output/myMicrobyte_fit_coupons.step'))
result['coupons']=[{'name':o.Name,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'volume_mm3':o.Shape.Volume} for o in objects]
(ROOT/'reports/motion_and_coupons.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
print(json.dumps(result,indent=2,ensure_ascii=False))
