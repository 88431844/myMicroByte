"""Generate a one-plate controlled fit trial from v0.8, with physical part IDs."""
from pathlib import Path
import sys,json,math,hashlib
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App,Part,MeshPart,Mesh
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/v08_trials';REP=ROOT/'reports/v08_trials'
OUT.mkdir(parents=True,exist_ok=True);REP.mkdir(parents=True,exist_ok=True)
base=App.openDocument(str(ROOT/'output/v08/myMicrobyte_enclosure_v08.FCStd'))
parts={
 'F1':base.FrontShellFlat_v08.Shape.copy(),
 'F3':base.FrontShellRaised_v08.Shape.copy(),
 'R1':base.RearShell_v08.Shape.copy(),
 'S1':base.PowerSlider_v08.Shape.copy(),
 'L1':base.AcousticLid_v08.Shape.copy(),
 'L2':base.AcousticLid_v08.Shape.copy(),
}
refshapes={o.Name:o.Shape.copy() for o in base.PCBReference.Group}
refs={o.Name:o.Shape.copy() for o in base.ConnectorKeepouts.Group}
source= (ROOT/'freecad/update_enclosure_v08.py').read_text().split('printables=[rear,front,raised,slider,lid]')[0]
# Rebuild the original features for each change, preserving rounded outer edges.
for code,edits,objname in [
 ('F2',[("Face=1.4,","Face=1.1,")],'FrontShellFlat_v08'),
 ('F4',[("ButtonHole=6.6,","ButtonHole=6.4,"),("w=6.8 if n=='A'","w=6.6 if n=='A'")],'FrontShellFlat_v08'),
 ('R2',[("box('SliderInnerOpenTrack',1.70,","box('SliderInnerOpenTrack',1.55,"),("box('SliderOuterOpenTrack',5,7.2,7,41.70,","box('SliderOuterOpenTrack',5,7.2,7,41.60,")],'RearShell_v08')]:
 text=source.replace("OUT=ROOT/'output/v08'; REPORT=ROOT/'reports/v08'","OUT=ROOT/'output/v08_trials'; REPORT=ROOT/'reports/v08_trials'")
 text=text.replace("App.newDocument('myMicrobyte_v08')",f"App.newDocument('trial_{code}')")
 for before,after in edits:
  assert before in text,(code,before)
  text=text.replace(before,after)
 ns={'__file__':str(ROOT/'freecad/update_enclosure_v08.py')}
 exec(compile(text,str(ROOT/'freecad/update_enclosure_v08.py'),'exec'),ns)
 d=ns['doc'];parts[code]=d.getObject(objname).Shape.copy()
 print('Generated',code,flush=True);App.closeDocument(d.Name)
# Wider/narrower sockets from the original uncut slider blank, only that dimension changes.
cy=-6.3186;cz=7.85
for code,width in [('S2',1.50),('S3',1.85)]:
 slot=Part.makeBox(1.55,width,6,App.Vector(40.05,cy-width/2,cz-2.8))
 parts[code]=base.SliderWithGrip.Shape.cut(slot).removeSplitter()
# Simple monoline marks (no font dependency), recessed to preserve contact and fit surfaces.
paths={
 'F':[[(0,0),(0,1),(.65,1)],[(0,.55),(.5,.55)]],
 'R':[[(0,0),(0,1),(.5,1),(.65,.85),(.65,.65),(.5,.5),(0,.5)],[(.35,.5),(.7,0)]],
 '1': [[(.15,.8),(.4,1),(.4,0)],[(.1,0),(.7,0)]],
 '2': [[(0,.8),(.15,1),(.5,1),(.7,.8),(.7,.65),(0,0),(.7,0)]],
 '3': [[(0,1),(.7,1),(.4,.55),(.7,.4),(.7,.15),(.5,0),(0,0)]],
 '4': [[(.55,0),(.55,1),(0,.3),(.75,.3)]],
}
def glyphs(word,height,stroke,cx,cy,z,depth):
 seg=[];advance=1.05*height;left=cx-((len(word)-1)*advance+.75*height)/2
 for i,ch in enumerate(word):
  for chain in paths[ch]:
   for a,b in zip(chain,chain[1:]):
    a=(left+i*advance+a[0]*height,cy+(a[1]-.5)*height);b=(left+i*advance+b[0]*height,cy+(b[1]-.5)*height)
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx=-dy/length*stroke/2;ny=dx/length*stroke/2
    pts=[App.Vector(a[0]+nx,a[1]+ny,z),App.Vector(b[0]+nx,b[1]+ny,z),App.Vector(b[0]-nx,b[1]-ny,z),App.Vector(a[0]-nx,a[1]-ny,z)]
    seg.append(Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(App.Vector(0,0,depth)))
    for x,y in [a,b]:seg.append(Part.makeCylinder(stroke/2,depth,App.Vector(x,y,z)))
 return seg[0].multiFuse(seg[1:]).removeSplitter()
for code in ['F1','F2','F3','F4']:
 top=13.9 if code=='F2' else 14.2
 mark=glyphs(code,1.5,.40,.11,-20.30,top-.32,.60)
 parts[code]=parts[code].cut(mark).removeSplitter()
for code in ['R1','R2']:
 mark=glyphs(code,4.0,.65,-4,-3.9,1.4-.32,.60)
 parts[code]=parts[code].cut(mark).removeSplitter()
# S1/S2/S3 are identified by one/two/three recessed dots on the inner crossbar bottom.
for n in [1,2,3]:
 marks=[Part.makeCylinder(.30,.35,App.Vector(40.85,cy-4.0+i*.85,5.60)) for i in range(n)]
 parts['S'+str(n)]=parts['S'+str(n)].cut(Part.makeCompound(marks)).removeSplitter()
trial=App.newDocument('myMicrobyte_v08_trials');trial.Label='v0.8 验证套件 / F1-F4·R1-R2·S1-S3'
meta={
 'F1':dict(kind='front',style='flat',face_z=14.2,bezel_z=14.2,hole=6.6,hole_A=6.8,button_exposure=1.4,glass_recess=.7,variable='baseline'),
 'F2':dict(kind='front',style='flat',face_z=13.9,bezel_z=13.9,hole=6.6,hole_A=6.8,button_exposure=1.7,glass_recess=.4,variable='front surface -0.3 mm'),
 'F3':dict(kind='front',style='raised',face_z=14.2,bezel_z=15.4,hole=6.6,hole_A=6.8,button_exposure=1.4,glass_recess=1.9,variable='screen surround +1.2 mm'),
 'F4':dict(kind='front',style='flat',face_z=14.2,bezel_z=14.2,hole=6.4,hole_A=6.6,button_exposure=1.4,glass_recess=.7,variable='button holes -0.2 mm'),
 'R1':dict(kind='rear',guide_width=1.70,total_guide_clearance=.40,variable='baseline'),
 'R2':dict(kind='rear',guide_width=1.55,total_guide_clearance=.25,variable='guide width -0.15 mm'),
 'S1':dict(kind='slider',socket=1.65,dots=1,variable='baseline'),
 'S2':dict(kind='slider',socket=1.50,dots=2,variable='socket -0.15 mm'),
 'S3':dict(kind='slider',socket=1.85,dots=3,variable='socket +0.20 mm'),
 'L1':dict(kind='lid',variable='identical open frame'), 'L2':dict(kind='lid',variable='identical spare open frame'),
}
report={'revision':'v0.8 controlled trials','parts':meta,'collisions':[],'meshes':[],'front_marks':'recessed F1-F4 beneath screen, 0.32 mm','rear_marks':'recessed R1/R2 inside battery frame, 0.32 mm'}
def check(a,b,tag):
 if not a.BoundBox.intersect(b.BoundBox):return
 v=a.common(b).Volume
 if v>.001:report['collisions'].append({'tag':tag,'volume_mm3':v})
# All front/rear combinations, and front reference clearance. Elastic speaker contact already audited.
for fc in ['F1','F2','F3','F4']:
 for rc in ['R1','R2']:check(parts[fc],parts[rc],fc+'/'+rc)
 for name,s in refshapes.items():check(parts[fc],s,fc+'/'+name)
 for dx,dy in [(0,0),(.2,.2),(.2,-.2),(-.2,.2),(-.2,-.2)]:
  s=refs['LCD_ToleranceEnvelope'].copy();s.translate(App.Vector(dx,dy,.2));check(parts[fc],s,fc+'/LCD tolerance')
# New rear is a local change to the guide; verify electronics and all sliders along travel.
for name,s in refshapes.items():
 if name!='Speaker_1510':check(parts['R2'],s,'R2/'+name)
fixed_switch=refshapes['Ref_SW3'].common(Part.makeBox(10,14,5,App.Vector(29.5,-12,6)))
for sc in ['S1','S2','S3']:
 for k in range(19):
  dy=-.55+k*.2;s=parts[sc].copy();s.translate(App.Vector(0,dy,0))
  for rc in ['R1','R2']:check(s,parts[rc],sc+'/'+rc+'/'+str(round(dy,2)))
  check(s,fixed_switch,sc+'/fixed switch/'+str(round(dy,2)))
for code in sorted(parts):
 sh=parts[code];assert sh.isValid() and len(sh.Solids)==1,code
 o=trial.addObject('Part::Feature',code);o.Label=code+' / '+meta[code]['variable'];o.Shape=sh
 posed=sh.copy()
 # Flat front faces and lid top face down. Raised front is printed inside down to keep its visible face off supports.
 if code in ['F1','F2','F4','L1','L2']:posed.rotate(App.Vector(),App.Vector(1,0,0),180)
 elif code.startswith('S'):posed.rotate(App.Vector(),App.Vector(0,1,0),-90)
 m=MeshPart.meshFromShape(Shape=posed,LinearDeflection=.025,AngularDeflection=.10,Relative=False)
 bb=m.BoundBox;m.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
 p=OUT/(code+'_print.stl');m.write(str(p));err=abs(m.Volume-sh.Volume)/sh.Volume
 assert m.isSolid() and not m.hasNonManifolds() and not m.hasSelfIntersections() and err<.001,code
 report['meshes'].append(dict(id=code,volume_mm3=sh.Volume,relative_error=err,bounds=[m.BoundBox.XLength,m.BoundBox.YLength,m.BoundBox.ZLength],sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
trial.recompute();trial.saveAs(str(OUT/'myMicrobyte_v08_trials.FCStd'))
(REP/'trial_geometry_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));(OUT/'configurations.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
assert not report['collisions'],'trial geometry collision'
