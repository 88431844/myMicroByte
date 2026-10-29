"""Export actual FreeCAD triangulations for the interactive assembly preview."""
from pathlib import Path
import sys,json,base64,array
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, MeshPart
ROOT=Path(__file__).resolve().parents[1]
doc=App.openDocument(str(ROOT/'output/v03/myMicrobyte_enclosure_v03.FCStd'))
shells=[doc.RearShell_v03,doc.FrontShell_v03]
caps=[o for o in doc.Objects if o.Name.startswith('Button_')]
objects=shells+caps+[doc.PowerSlider_v03]+list(doc.PCBReference.Group)+list(doc.Hardware_v03.Group)
data=[]
for o in objects:
    if o.Shape.isNull():continue
    points,faces=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=.2,AngularDeflection=.65,Relative=False).Topology
    pos=array.array('h',[round(v*100) for pt in points for v in (pt.x,pt.y,pt.z)])
    idx=array.array('I',[v for face in faces for v in face])
    typ='rear' if o==shells[0] else 'front' if o==shells[1] else 'cap' if o in caps else 'slider' if o==doc.PowerSlider_v03 else 'insert' if o.Name.startswith('Hardware_Insert') else 'screw' if o.Name.startswith('Hardware_Screw') else 'battery' if o.Name=='Battery_Assumed' else 'speaker' if o.Name=='Speaker_1510' else 'lcd' if o.Name.startswith('LCD') else 'pcb' if o.Name=='Ref_Board' else 'component'
    color='#26292e' if typ in ['front','rear','cap','slider'] else '#ba944b' if typ=='insert' else '#aeb2bb' if typ in ['screw','battery'] else '#0d2832' if typ=='lcd' else '#247141' if typ=='pcb' else '#747c82' if o.Name in ['USB_Envelope','Ref_CARD1'] else '#454b50' if typ=='speaker' else '#42494a'
    data.append({'name':o.Name,'label':o.Label,'type':typ,'color':color,'p':base64.b64encode(pos.tobytes()).decode(),'i':base64.b64encode(idx.tobytes()).decode()})
out=ROOT/'reports/v03/preview_meshes.json';out.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
print('Objects:',len(data),'JSON bytes:',out.stat().st_size)
