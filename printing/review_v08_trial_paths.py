from pathlib import Path
import json,zipfile,re,math,hashlib,xml.etree.ElementTree as E
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'printing/A1_black_PLA_v08_trials';R=ROOT/'reports/v08_trials';p=OUT/'myMicrobyte_v08_trials_black.gcode.3mf'
with zipfile.ZipFile(p) as archive:
 g=archive.read('Metadata/plate_1.gcode');s=json.loads(archive.read('Metadata/project_settings.config'));si=E.fromstring(archive.read('Metadata/slice_info.config'));plates=si.findall('plate');assert len(plates)==1
 plate=plates[0];meta={m.get('key'):m.get('value') for m in plate.findall('metadata')};objs=plate.findall('object');names=[o.get('name') for o in objs];expect={c+'_print.stl' for c in ['F1','F2','F3','F4','R1','R2','S1','S2','S3','L1','L2']}
 assert set(names)==expect and len(names)==11 and all(o.get('skipped')=='false' for o in objs)
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
# Nominal extrusion-width plots expose whether support fuses to the slide-keeper slots.
regions=[('R1 keeper base',224,228,71,86,6.2),('R1 keeper top',224,228,71,86,10.92),('R2 keeper base',127,131,71,86,6.2),('R2 keeper top',127,131,71,86,10.92),('R1 acoustic',207,223,69,94,6.28),('R2 acoustic',110,126,69,94,6.28)]
fig,axs=plt.subplots(2,3,figsize=(15,10),layout='constrained')
for ax,(label,x0,x1,y0,y1,z0) in zip(axs.flat,regions):
 available=sorted(set(zl for zl,ft,ww,pts in paths if any(x0<a<x1 and y0<b<y1 for a,b in pts)));zz=min(available,key=lambda t:abs(t-z0))
 for zl,ft,ww,pts in paths:
  if abs(zl-zz)>.001:continue
  if max(a for a,b in pts)<x0 or min(a for a,b in pts)>x1 or max(b for a,b in pts)<y0 or min(b for a,b in pts)>y1:continue
  color='#d94a45' if 'Support' in ft else '#1c596b'
  for (a,b),(c,d) in zip(pts,pts[1:]):
   ll=math.hypot(c-a,d-b)
   if ll<1e-7:continue
   dx=-(d-b)/ll*ww/2;dy=(c-a)/ll*ww/2
   ax.add_patch(Polygon([(a+dx,b+dy),(c+dx,d+dy),(c-dx,d-dy),(a-dx,b-dy)],color=color,linewidth=0))
 ax.set(xlim=(x0,x1),ylim=(y0,y1),aspect='equal',title=f'{label} / Z{zz:.2f} mm');ax.grid(alpha=.2)
fig.suptitle('Actual extrusion width review — red = removable support');fig.savefig(R/'keeper_acoustic_toolpaths.png',dpi=170)
fig,axs=plt.subplots(2,3,figsize=(15,7),layout='constrained')
marks=[('F1',184.61,217.9,.2,3,1.6),('F2',184.61,160.9,.2,3,1.6),('F3',87.61,177.3,4.84,3,1.6),('F4',87.61,160.9,.2,3,1.6),('R1',180.5,79.7,2.28,6,3.5),('R2',83.5,79.7,2.28,6,3.5)]
for ax,(name,cx,cy,target,hw,hh) in zip(axs.flat,marks):
 x0,x1,y0,y1=cx-hw,cx+hw,cy-hh,cy+hh
 available=sorted(set(zl for zl,ft,ww,pts in paths if any(x0<a<x1 and y0<b<y1 for a,b in pts)))
 zz=min(available,key=lambda q:abs(q-target))
 for zl,ft,ww,pts in paths:
  if abs(zl-zz)>.001:continue
  if max(a for a,b in pts)<x0 or min(a for a,b in pts)>x1 or max(b for a,b in pts)<y0 or min(b for a,b in pts)>y1:continue
  for (a,b),(c,d) in zip(pts,pts[1:]):
   ll=math.hypot(c-a,d-b)
   if ll<1e-7:continue
   dx=-(d-b)/ll*ww/2;dy=(c-a)/ll*ww/2
   ax.add_patch(Polygon([(a+dx,b+dy),(c+dx,d+dy),(c-dx,d-dy),(a-dx,b-dy)],color='#1c596b',linewidth=0))
 ax.set(xlim=(x0,x1),ylim=(y0,y1),aspect='equal',title=f'{name} / actual layer Z{zz:.2f}')
 if name in ['F1','F2','F4']:ax.invert_yaxis()
fig.suptitle('Recessed part IDs retained in actual toolpaths');fig.savefig(R/'engraved_ids_toolpaths.png',dpi=170)

report={'status':'sliced_one_plate','file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'printer':s['printer_model'],'count':len(names),'names':names,'estimated_seconds':int(meta['prediction']),'estimated_grams':float(meta['weight']),'bed_bbox_xy':bbox['bbox_all'],'layer_height':s['layer_height'],'filaments':filaments,'all_object_tool_indices':{n:list(t) for n,t in actual.items()},'job_sent':False}
(R/'print_project_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
