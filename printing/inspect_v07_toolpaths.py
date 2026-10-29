from pathlib import Path
import re, math, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
ROOT=Path(__file__).resolve().parents[1]
g=ROOT/'printing/A1_black_green_blue_PLA_v07/gui_plate_1.gcode'
x=y=z=layer=0.; w=.42; feature=''; segments=[]
for line in g.read_text().splitlines():
 if line.startswith('; Z_HEIGHT:'): layer=float(line.split(':')[1])
 if line.startswith('; LINE_WIDTH:'): w=float(line.split(':')[1])
 if line.startswith('; FEATURE:'): feature=line.split(':',1)[1].strip()
 raw=line.split(';')[0].strip();cmd=raw.split(' ')[0]
 if cmd not in ('G0','G1','G2','G3'): continue
 a={k:float(v) for k,v in re.findall(r'([XYZEIJ])([-+]?\d*\.?\d+)',raw)}
 nx=a.get('X',x);ny=a.get('Y',y);nz=a.get('Z',z)
 pts=[(x,y),(nx,ny)]
 if cmd in ('G2','G3') and ('I' in a or 'J' in a):
  cx=x+a.get('I',0);cy=y+a.get('J',0);r=math.hypot(x-cx,y-cy)
  t0=math.atan2(y-cy,x-cx);t1=math.atan2(ny-cy,nx-cx);dt=(t1-t0)%(2*math.pi)
  if cmd=='G2':dt=dt-2*math.pi
  n=max(2,int(abs(dt)*r/.08));pts=[(cx+r*math.cos(t0+dt*i/n),cy+r*math.sin(t0+dt*i/n)) for i in range(n+1)]
 if a.get('E',0)>0 and ('X' in a or 'Y' in a) and 161 < (x+nx)/2 <181 and 91 <(y+ny)/2<119:
  segments.append((layer,feature,w,pts))
 x,y,z=nx,ny,nz
layers=sorted(set(p[0] for p in segments));targets=[min(layers,key=lambda x:abs(x-z)) for z in [2.1,3.5,5.4,7.2]]
fig,axs=plt.subplots(1,4,figsize=(16,6),layout='constrained')
for ax,t in zip(axs,targets):
 for zz,ft,ww,pts in segments:
  if zz!=t:continue
  c='#d13a42' if 'Support' in ft else '#1f6177'
  for (a,b),(c1,d) in zip(pts,pts[1:]):
   ll=math.hypot(c1-a,d-b)
   if ll<1e-6:continue
   dx=-(d-b)/ll*ww/2;dy=(c1-a)/ll*ww/2
   ax.add_patch(Polygon([(a+dx,b+dy),(c1+dx,d+dy),(c1-dx,d-dy),(a-dx,b-dy)],color=c,linewidth=0))
 ax.set(xlim=(162.5,179.5),ylim=(92,117),aspect='equal',title=f'Z = {t:.2f} mm',xlabel='Plate X / mm')
 ax.grid(alpha=.18)
axs[0].set_ylabel('Plate Y / mm')
fig.suptitle('v0.7 acoustic chamber: actual extrusion widths (red = support)')
fig.savefig(ROOT/'reports/v07/acoustic_sliced_layers.png',dpi=180)
report={'sampled_layers_mm':targets,'acoustic_support_segments_above_floor':sum(1 for z,f,w,p in segments if z>1.8 and 'Support' in f),'note':'Toolpath widths shown at nominal extrusion width, not a print accuracy guarantee.'}
(ROOT/'reports/v07/acoustic_toolpath_check.json').write_text(json.dumps(report,indent=2));print(report)
