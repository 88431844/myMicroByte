"""Orthographic rendering of the actual FreeCAD solids, without GPU dependencies."""
from pathlib import Path
import sys
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
V02='--v02' in sys.argv
V03='--v03' in sys.argv
V04='--v06' in sys.argv
REPORT = ROOT/'reports/v06' if V04 else ROOT/'reports/v03' if V03 else ROOT/'reports/v02' if V02 else ROOT/'reports'
REPORT.mkdir(parents=True,exist_ok=True)
doc = App.openDocument(str(ROOT/('output/v06/myMicrobyte_enclosure_v06.FCStd' if V04 else 'output/v03/myMicrobyte_enclosure_v03.FCStd' if V03 else 'output/v02/myMicrobyte_enclosure_v02.FCStd' if V02 else 'output/myMicrobyte_enclosure_v01.FCStd')))
black = np.array([43., 45., 48.])
shells = [doc.RearShell_v06, doc.FrontShell_v06] if V04 else [doc.RearShell_v03, doc.FrontShell_v03] if V03 else [doc.RearShell_v02, doc.FrontShell_v02] if V02 else [doc.RearShell, doc.FrontShell]
caps = [] if V04 else [o for o in doc.Objects if o.Name.startswith('Button_' if V03 else 'Cap_')]
cam = np.array([0.42, -0.68, 0.76]); cam /= np.linalg.norm(cam)
right = np.cross([0., 0., 1.], cam); right /= np.linalg.norm(right)
up = np.cross(cam, right)
basis = np.stack([right, up, cam], axis=1)
light = np.array([-0.3, -0.5, 1.]); light /= np.linalg.norm(light)

def material(o):
    if o in shells or o in caps or o.Name in ('PowerSlider_v03','PowerSlider_v06','AcousticLid_v06'): return black
    if o.Name in ('SpeakerFrontSeal','ChamberLidSeal'):return np.array([140.,190.,170.])
    if o.Name.startswith('Hardware_Insert'): return np.array([185.,149.,75.])
    if o.Name.startswith('Hardware_Screw'): return np.array([170.,176.,182.])
    if o.Name.startswith('LCD'): return np.array([13., 40., 50.])
    if o.Name.startswith('Battery'): return np.array([155., 159., 168.])
    if o.Name.startswith('Speaker_'): return np.array([95., 99., 107.])
    if o.Name in ('USB_Envelope', 'Ref_CARD1'): return np.array([153., 157., 162.])
    if o.Name in ['Ref_UP','Ref_DOWN','Ref_LEFT','Ref_RIGHT','Ref_START','Ref_SELECT','Ref_MENU','Ref_A','Ref_B']: return np.array([29., 31., 32.])
    if o.Name == 'Ref_Board': return np.array([38., 105., 64.])
    return np.array([55., 72., 66.])

def render(exploded=False,inside=False,empty=False):
    items = shells + caps + (list(doc.PCBReference.Group) if exploded or V04 else [doc.LCD_Assumed_5mm, doc.USB_Envelope])
    if V04:items += [doc.PowerSlider_v06,doc.AcousticLid_v06]+list(doc.AcousticSeals.Group) + (list(doc.Hardware_v06.Group) if exploded else [])
    if V03:items += [doc.PowerSlider_v03] + (list(doc.Hardware_v03.Group) if exploded else [])
    if inside: items=[shells[0]]+([] if empty else [doc.Battery_Assumed,doc.Speaker_1510])
    meshes=[]
    for o in items:
        pts, faces = o.Shape.tessellate(0.08)
        points = np.array([[p.x,p.y,p.z] for p in pts])
        if exploded:
            dz = 51 if o == shells[1] else 42 if o in caps else 0 if o == shells[0] or o.Name in ('PowerSlider_v03','PowerSlider_v06') else 51 if o.Name.startswith('Hardware_Insert') else -20 if o.Name.startswith('Hardware_Screw') else 20 if o.Name=='AcousticLid_v06' else 14 if o.Name=='ChamberLidSeal' else 8 if o.Name=='Speaker_1510' else 4 if o.Name=='SpeakerFrontSeal' else 4 if o==doc.Battery_Assumed else 30
            points[:,2] += dz
        meshes.append((points,np.asarray(faces),material(o)))
    W,H=1800,1450 if exploded else 1120
    projected = np.concatenate([p@basis for p,f,c in meshes])
    lo,hi=projected[:,:2].min(0),projected[:,:2].max(0)
    scale=min((W-300)/(hi[0]-lo[0]), (H-280)/(hi[1]-lo[1]))
    center=(lo+hi)/2
    depth=np.full((H,W),-np.inf)
    rgb=np.zeros((H,W,3),dtype=np.uint8);rgb[:]=[243,245,247]
    def screen(p):
        q=p@basis
        q[:,0]=(q[:,0]-center[0])*scale+W/2
        q[:,1]=H/2+30-(q[:,1]-center[1])*scale
        return q
    # Ground silhouette, softened; the object image itself uses a depth buffer.
    shadow=Image.new('L',(W,H));sd=ImageDraw.Draw(shadow)
    for p,f,c in meshes:
        pp=p.copy();pp[:,0]+=pp[:,2]*0.2;pp[:,1]+=pp[:,2]*0.15;pp[:,2]=0
        q=screen(pp)
        for face in f: sd.polygon([tuple(t) for t in q[face,:2]],fill=30)
    sh=np.array(shadow.filter(ImageFilter.GaussianBlur(18)))
    rgb=np.maximum(0,rgb.astype(int)-sh[:,:,None]).astype('uint8')
    for points, faces, color in meshes:
        proj=screen(points)
        for face in faces:
            p=points[face];n=np.cross(p[1]-p[0],p[2]-p[0]);norm=np.linalg.norm(n)
            if norm<1e-10:continue
            n/=norm
            if np.dot(n,cam)<=0:continue
            tri=proj[face];xmin=max(0,int(np.floor(tri[:,0].min())));xmax=min(W-1,int(np.ceil(tri[:,0].max())))
            ymin=max(0,int(np.floor(tri[:,1].min())));ymax=min(H-1,int(np.ceil(tri[:,1].max())))
            if xmax<xmin or ymax<ymin:continue
            x,y=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
            a,b,c=tri
            denom=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(denom)<1e-10:continue
            w0=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/denom
            w1=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/denom
            w2=1-w0-w1;z=w0*a[2]+w1*b[2]+w2*c[2]
            target=depth[ymin:ymax+1,xmin:xmax+1]
            mask=(w0>=-1e-7)&(w1>=-1e-7)&(w2>=-1e-7)&(z>target)
            half=(light+cam);half/=np.linalg.norm(half)
            shade=.48+.64*max(0,np.dot(n,light))
            spec=25*max(0,np.dot(n,half))**35
            rgb[ymin:ymax+1,xmin:xmax+1][mask]=np.clip(color*shade+spec,0,255)
            target[mask]=z[mask]
    im=Image.fromarray(rgb);draw=ImageDraw.Draw(im)
    font='/System/Library/Fonts/Supplemental/Arial.ttf'
    draw.text((70,40),'myMicrobyte / BLACK PLA',font=ImageFont.truetype(font,34),fill=(36,43,51))
    subtitle='REAR SHELL / ADHESIVE FRAME + 1510 SPEAKER SEAT' if inside and empty else 'REAR SHELL / BATTERY + SPEAKER (PCB REMOVED)' if inside else 'EXPLODED ASSEMBLY' if exploded else 'ASSEMBLED / 85 x 45 x 24.5 mm'
    if V03 and not inside and not exploded:subtitle='ASSEMBLED / 85 x 45 x 21.9 mm / KEYED DOME CAPS'
    if V04 and not inside and not exploded:subtitle='ASSEMBLED / 85 x 45 x 14.4 mm / EXPOSED SILENT SWITCHES'
    draw.text((70,92),subtitle,font=ImageFont.truetype(font,20),fill=(100,108,116))
    footer='Prototype v0.2 | LCD stack 2.0 mm | Speaker 15 x 10 x 3.5 mm | Battery selection envelope 56 x 36 x 6 mm' if V02 else 'Prototype v0.1 | Actual CAD geometry | LCD and battery envelopes are provisional'
    if V03:footer='Prototype v0.3 | LCD recess 1.6 mm | Battery 503550 | M2 x 5 screws / M2 x 2 x 3 inserts'
    if V04:footer='Prototype v0.6 | Rounded edges R1.8 | Battery placeholder 50 x 28 x 3 mm | Actual CAD geometry'
    draw.text((70,H-65),footer,font=ImageFont.truetype(font,20),fill=(100,108,116))
    name='rear_frame.png' if inside and empty else 'rear_layout.png' if inside else 'blackPLA_exploded.png' if exploded else 'blackPLA_assembly.png'
    im.save(REPORT/name)
    print(name, 'rendered',len(items),'objects')

render(False)
render(True)
if V02 or V03 or V04:
    render(inside=True)
    render(inside=True,empty=True)
