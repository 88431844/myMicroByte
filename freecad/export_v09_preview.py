from pathlib import Path
import sys,json,base64,array,gzip
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App,Part,MeshPart
ROOT=Path(__file__).resolve().parents[1]
doc=App.openDocument(str(ROOT/'output/v09/myMicrobyte_enclosure_v09.FCStd'));doc.recompute()
objects=[doc.RearShell_v09,doc.FrontShell_v09,doc.PowerSlider_v09,doc.SliderKeeper_v09]+list(doc.PCBReference.Group)+list(doc.Hardware_v09.Group)
active=doc.addObject('Part::Feature','LCD_ActiveArea');active.Label='27.72×27.72 mm显示区（示意面）';active.Shape=Part.makeBox(27.72,27.72,.012,App.Vector(.110-13.86,.123-13.86,13.50005));objects.append(active)
data=[]
for o in objects:
 if o.Shape.isNull():continue
 points,faces=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=.12,AngularDeflection=.4,Relative=False).Topology
 pos=array.array('h',[round(v*100) for pt in points for v in (pt.x,pt.y,pt.z)]);idx=array.array('I',[v for face in faces for v in face])
 typ='rear' if o==doc.RearShell_v09 else 'front' if o==doc.FrontShell_v09 else 'slider' if o==doc.PowerSlider_v09 else 'keeper' if o==doc.SliderKeeper_v09 else 'insert' if o.Name.startswith('Hardware_Insert') else 'screw' if o.Name.startswith('Hardware_Screw') else 'battery' if o.Name=='Battery_Assumed' else 'speaker' if o.Name.startswith('Speaker_') else 'lcd' if o.Name.startswith('LCD') else 'pcb' if o.Name=='Ref_Board' else 'component'
 color='#202329' if typ in ['front','rear','slider','keeper'] else '#ba944b' if typ=='insert' else '#aeb2bb' if typ in ['screw','battery'] else '#132c37' if o==active else '#070b0f' if typ=='lcd' else '#247141' if typ=='pcb' else '#9ccabd' if o.Name=='Speaker_Adhesive' else '#747c82' if o.Name in ['USB_Envelope','Ref_CARD1'] else '#454b50' if typ=='speaker' else '#42494a'
 data.append({'name':o.Name,'label':o.Label,'type':typ,'color':color,'variant':'raised' if typ=='front' else None,'p':base64.b64encode(pos.tobytes()).decode(),'i':base64.b64encode(idx.tobytes()).decode()})
out=ROOT/'reports/v09/preview_meshes.json';out.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
out.with_suffix('.b64').write_text(base64.b64encode(gzip.compress(out.read_bytes())).decode())
print('Preview export',len(data),'objects',out.stat().st_size,'bytes')
