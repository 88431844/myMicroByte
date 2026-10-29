from pathlib import Path
import json,zipfile,re,math,hashlib,xml.etree.ElementTree as E
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'printing/A1_black_PLA_v10';R=ROOT/'reports/v10';p=OUT/'myMicrobyte_v10_black.gcode.3mf'
with zipfile.ZipFile(p) as archive:
 g=archive.read('Metadata/plate_1.gcode');s=json.loads(archive.read('Metadata/project_settings.config'));si=E.fromstring(archive.read('Metadata/slice_info.config'));plates=si.findall('plate');assert len(plates)==1
 plate=plates[0];meta={m.get('key'):m.get('value') for m in plate.findall('metadata')};objs=plate.findall('object');names=[o.get('name') for o in objs];expect={c+'_print.stl' for c in ['FrontShell','RearShell','PowerSlider']}
 assert set(names)==expect and len(names)==3 and all(o.get('skipped')=='false' for o in objs)
 assert meta['outside']=='false' and meta['nozzle_diameters']=='0.4'
 assert s['printer_model']=='Bambu Lab A1' and s['layer_height']=='0.16' and s['support_on_build_plate_only']=='1'
 filaments=[dict(f.attrib) for f in plate.findall('filament')];assert len(filaments)==1 and filaments[0]['type']=='PLA' and filaments[0]['color']=='#171717'
 assert hashlib.md5(g).hexdigest()==archive.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
 bbox=json.loads(archive.read('Metadata/plate_1.json'));assert min(bbox['bbox_all'])>0 and max(bbox['bbox_all'])<256
 for a in bbox['bbox_objects']:
  for b in bbox['bbox_objects']:
   if a['id']>=b['id']:continue
   aa,bb=a['bbox'],b['bbox'];assert aa[2]<bb[0] or aa[0]>bb[2] or aa[3]<bb[1] or aa[1]>bb[3],(a['name'],b['name'])
 (OUT/'plate_1.gcode').write_bytes(g)
 for name in ['plate_1.png','top_1.png']:(R/name).write_bytes(archive.read('Metadata/'+name))
 text=g.decode();idmap={int(o.get('identify_id')):o.get('name') for o in objs}
active=None;tool=0;feature='';actual={n:set() for n in names};paths=[];x=y=z=0.;layer=0;w=.42
for line in text.splitlines():
 if line.startswith('; start printing object'):active=idmap[int(line.rsplit(':',1)[1])]
 elif line.startswith('; stop printing object'):active=None
 elif line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
 elif line.startswith('; Z_HEIGHT:'):layer=float(line.split(':',1)[1])
 elif line.startswith('; LINE_WIDTH:'):w=float(line.split(':',1)[1])
 elif re.fullmatch(r'T\d+',line) and int(line[1:])<255:tool=int(line[1:])
 raw=line.split(';')[0].strip();cmd=raw.split(' ')[0]
 if cmd not in ['G0','G1','G2','G3']:continue
 v={k:float(a) for k,a in re.findall(r'([XYZEIJ])([-+]?\d*\.?\d+)',raw)};nx,ny,nz=v.get('X',x),v.get('Y',y),v.get('Z',z)
 if v.get('E',0)>0 and ('X' in v or 'Y' in v):
  if active and feature in ['Outer wall','Inner wall','Top surface','Bottom surface']:actual[active].add(tool)
  pts=[(x,y),(nx,ny)]
  if cmd in ['G2','G3'] and ('I' in v or 'J' in v):
   cx,cy=x+v.get('I',0),y+v.get('J',0);rad=math.hypot(x-cx,y-cy);t0=math.atan2(y-cy,x-cx);dt=(math.atan2(ny-cy,nx-cx)-t0)%(2*math.pi)
   if cmd=='G2':dt-=2*math.pi
   n=max(2,int(abs(dt)*rad/.10));pts=[(cx+rad*math.cos(t0+dt*i/n),cy+rad*math.sin(t0+dt*i/n)) for i in range(n+1)]
  paths.append((layer,feature,w,pts))
 x,y,z=nx,ny,nz
assert actual=={n:{0} for n in names},actual
report={'status':'sliced_one_plate','file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'printer':s['printer_model'],'count':len(names),'names':names,'estimated_seconds':int(meta['prediction']),'estimated_grams':float(meta['weight']),'bed_bbox_xy':bbox['bbox_all'],'layer_height':s['layer_height'],'filaments':filaments,'all_object_tool_indices':{n:list(t) for n,t in actual.items()},'job_sent':False}
(R/'print_project_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
