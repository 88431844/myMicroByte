"""Trial-fit revision: thin battery bay, shallow LCD, keyed caps and captive slider.
Run with /Applications/FreeCAD.app/Contents/Resources/bin/python.
Dimensions are millimetres; original PCB XY datums are preserved.
"""
from pathlib import Path
import sys, json, math
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, MeshPart

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/v03'; REPORT=ROOT/'reports/v03'
OUT.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
doc=App.openDocument(str(ROOT/'output/v02/myMicrobyte_enclosure_v02.FCStd'))
doc.Label='myMicrobyte v0.3 — 5 mm battery / keyed dome caps / M2 inserts'
p=doc.Parameters
def param(alias,value,note):
    row=next((i for i in range(1,220) if p.getAlias('B'+str(i))==alias),None)
    if row is None: row=next(i for i in range(1,220) if 'B'+str(i) not in p.getNonEmptyCells())
    p.set('A'+str(row),note);p.set('B'+str(row),str(value));p.setAlias('B'+str(row),alias)
for a,v,n in [
 ('BoardRearZ',13.0,'PCB 背面高度；5 mm 电池方案'),('Floor',1.6,'后壳底厚'),
 ('BatteryT',5,'电池成品最大厚度'),('FrontUnderZ',20.50005,'按键区域面板内侧'),
 ('BatteryW',50,'503550 电芯标称长度，成品需包含保护板'),('BatteryH',35,'503550 电芯标称宽度'),
 ('BatteryFrameClearW',57,'保留原电池框内长'),('BatteryFrameClearH',37,'保留原电池框内宽'),
 ('Face',1.4,'按键区域面板厚'),('BossR',3.4,'螺柱半径'),
 ('FlangeBottomZ',19.95005,'帽防脱耳底'),('FlangeT',0.5,'帽防脱耳厚'),
 ('ButtonTopZ',23.70005,'弧面帽最高点'),('StemBottomZ',19.82015,'A 帽触头高度'),
 ('LCDRecess',1.6,'玻璃至窗口边缘深度'),('LowRoofT',1.0,'屏幕低面板厚'),
 ('RoofFlatHalfW',17.0,'下沉屏幕区域半宽'),('RoofRampOuterX',19.0,'斜面过渡外侧 X'),
 ('EarW',1.6,'帽定位耳宽'),('EarLength',9.2,'双定位耳总长'),
 ('EarGap',0.25,'定位耳单边滑动间隙'),('DomeRise',0.8,'弧面帽球冠高度'),
 ('InsertOD',3,'用户热熔螺母外径'),('InsertL',2,'用户热熔螺母长度'),
 ('InsertPilotD',2.8,'热熔预孔直径'),('InsertPocketDepth',2.15,'热熔预孔深度'),
 ('ScrewL',5,'用户 M2×5 机牙螺丝'),('ScrewHeadD',4,'螺丝头外径'),
 ('RearSeatT',1.4,'沉孔底至 PCB 的承力厚度'),('HeadBoreD',4.6,'后盖深沉孔直径'),
 ('TFSlotW',11.6,'TF 11 mm 卡宽＋0.6 mm'),('TFSlotH',1.9,'TF 卡通道高度'),
 ('PortChamfer',0.8,'接口外扩倒角深度'),
 ('SliderTravel',2.3,'拨帽可用行程；扣除叉槽空程后容纳约1.5 mm开关行程'),
 ('SliderSocketW',1.8,'白色拨杆 1.3 mm＋装配余量'),
 ('SliderSocketH',1.5,'白色拨杆 1.1 mm＋装配余量'),
 ('SliderCy',-5.1686,'拨帽行程中心 Y'),('SliderCzOffset',-1.15,'拨帽中心相对 PCB 背面'),
]:param(a,v,n)

def num(k):return float(getattr(p,k))
def setprop(o,k,v):
    if isinstance(v,str):o.setExpression(k,v)
    elif k.startswith('Placement.Base.'):
        b=o.Placement.Base;setattr(b,k[-1],v);o.Placement.Base=b
    else:setattr(o,k,v)
def box(n,w,h,d,x,y,z):
    o=doc.addObject('Part::Box',n)
    for k,v in [('Length',w),('Width',h),('Height',d),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:setprop(o,k,v)
    return o
def cyl(n,r,h,x,y,z):
    o=doc.addObject('Part::Cylinder',n)
    for k,v in [('Radius',r),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:setprop(o,k,v)
    return o
def fuse(n,objects):
    o=doc.addObject('Part::MultiFuse',n);o.Shapes=objects;o.Refine=True;return o
def cut(n,a,b):
    o=doc.addObject('Part::Cut',n);o.Base=a;o.Tool=b;o.Refine=True;return o
def feature(n,s,label=None):
    o=doc.addObject('Part::Feature',n);o.Shape=s;o.Label=label or n;return o
def xz_prism(n,coords,y=-24,length=48):
    wire=Part.makePolygon([App.Vector(x,y,z) for x,z in coords]+[App.Vector(coords[0][0],y,coords[0][1])])
    return feature(n,Part.Face(wire).extrude(App.Vector(0,length,0)))
def rectwire_xz(cx,cy,cz,w,h):
    pts=[App.Vector(cx-w/2,cy,cz-h/2),App.Vector(cx+w/2,cy,cz-h/2),App.Vector(cx+w/2,cy,cz+h/2),App.Vector(cx-w/2,cy,cz+h/2)]
    return Part.makePolygon(pts+[pts[0]])
def port(n,cx,cz,w,h,side):
    # Narrow inner throat and a 45-degree outer lead-in.
    yi=side*19.9; ym=side*(22.5-num('PortChamfer')); yo=side*23.2
    throat=Part.Face(rectwire_xz(cx,yi,cz,w,h)).extrude(App.Vector(0,ym-yi,0))
    cham=Part.makeLoft([rectwire_xz(cx,ym,cz,w,h),rectwire_xz(cx,yo,cz,w+2*(abs(yo-ym)),h+2*(abs(yo-ym)))],True,True)
    return feature(n,throat.fuse(cham).removeSplitter())

# Keep the previous frame footprint as requested, allowing the chosen 503550
# pack its protection board/wrap allowance without making the case wider.
for o,extra in [(doc.BatteryFrameOuter,'2*Parameters.FrameWall'),(doc.BatteryFrameVoid,'0')]:
    o.setExpression('Length','Parameters.BatteryFrameClearW+'+extra)
    o.setExpression('Width','Parameters.BatteryFrameClearH+'+extra)
    o.setExpression('Placement.Base.x','Parameters.BatteryCx-Parameters.BatteryFrameClearW/2-('+extra+')/2')
    o.setExpression('Placement.Base.y','Parameters.BatteryCy-Parameters.BatteryFrameClearH/2-('+extra+')/2')
doc.recompute()
br=num('BoardRearZ'); bt=num('BoardT'); pf=br+bt; high=num('FrontUnderZ')+num('Face')
glass=pf+num('LCDThickness')+num('LCDAdhesive'); low=glass+num('LCDRecess')
holes=[(37.46,17.46),(37.46,-17.46),(-37.46,17.46),(-37.46,-17.46)]

# Preserve the useful v0.2 battery/speaker frame features, replacing port/screw cutters.
doc.RearCutters.Shapes=[]
# An empty MultiFuse is invalid. Keep a harmless cylinder fully inside the cavity.
dummy=cyl('V03HarmlessVoid',0.1,1,0,0,br-1)
doc.RearCutters.Shapes=[dummy,cyl('V03HarmlessVoid2',.1,1,1,0,br-1)]
doc.recompute()
rearbase=doc.RearShell_v02
rearholes=[]
for i,(x,y) in enumerate(holes,1):
    rearholes.append(cyl('V03ScrewThrough'+str(i),1.15,br+2,x,y,-.1))
    rearholes.append(cyl('V03DeepHeadBore'+str(i),'Parameters.HeadBoreD/2','Parameters.BoardRearZ-Parameters.RearSeatT+0.1',x,y,-.1))
usbport=port('V03USBThroatAndChamfer',-.00165,br-1.8,10.4,4.6,-1)
tfport=port('V03TFThroatAndChamfer',4.851,br-.8,num('TFSlotW'),num('TFSlotH'),1)
rearholes += [usbport,tfport]

# One continuous variable-height roof: shallow around the LCD and higher above switches.
outer=doc.FrontOuter
roof=xz_prism('V03RoofTopEnvelope',[(-44,12),(-44,high+1),(-num('RoofRampOuterX'),high+1),(-num('RoofRampOuterX'),high),(-num('RoofFlatHalfW'),low),(num('RoofFlatHalfW'),low),(num('RoofRampOuterX'),high),(num('RoofRampOuterX'),high+1),(44,high+1),(44,12)])
trim=doc.addObject('Part::Common','V03RoofOuter');trim.Base=outer;trim.Tool=roof;trim.Refine=True
cavitytop=xz_prism('V03CavityRoofEnvelope',[(-44,12),(-44,num('FrontUnderZ')),(-num('RoofRampOuterX'),num('FrontUnderZ')),(-num('RoofFlatHalfW'),low-num('LowRoofT')),(num('RoofFlatHalfW'),low-num('LowRoofT')),(num('RoofRampOuterX'),num('FrontUnderZ')),(44,num('FrontUnderZ')),(44,12)])
cavity=doc.addObject('Part::Common','V03FrontCavity');cavity.Base=doc.FrontCavity;cavity.Tool=cavitytop;cavity.Refine=True
frontbase=cut('V03RoofAndWalls',trim,cavity)
frontbase=cut('V03TongueReceiver',frontbase,doc.TongueReceiver)
frontbase=fuse('V03FrontWithInsertBosses',[frontbase]+[doc.getObject('FrontPost'+('' if i==0 else '%03d'%i)) for i in range(4)])
fronttools=[box('V03LCDWindow',num('WindowW'),num('WindowH'),12,num('ScreenCx')-num('WindowW')/2,num('ScreenCy')-num('WindowH')/2,16)]
inserts=[];screws=[]
for i,(x,y) in enumerate(holes,1):
    fronttools.append(cyl('V03InsertPilot'+str(i),'Parameters.InsertPilotD/2','Parameters.InsertPocketDepth+0.02',x,y,pf-.02))
    fronttools.append(cyl('V03ScrewTipRelief'+str(i),1.15,3.0,x,y,pf-.02))
    # Small lead-in removes the printed first-layer lip during heat insertion.
    cone=Part.makeCone(1.55,1.4,.3,App.Vector(x,y,pf-.01))
    fronttools.append(feature('V03InsertLeadIn'+str(i),cone))
    ins=Part.makeCylinder(1.5,2,App.Vector(x,y,pf)).cut(Part.makeCylinder(.8,2.2,App.Vector(x,y,pf-.1)))
    inserts.append(feature('Hardware_Insert'+str(i),ins,'M2×2×3 热熔螺母 '+str(i)))
    seat=br-num('RearSeatT')
    screw=Part.makeCylinder(1,5,App.Vector(x,y,seat)).fuse(Part.makeCylinder(2,.8,App.Vector(x,y,seat-.8)))
    screws.append(feature('Hardware_Screw'+str(i),screw,'M2×5 螺丝 '+str(i)))

# Flanges carry two opposed locating ears, sliding in short channels under the face.
caps=[];earwalls=[];earcuts=[]
names=['UP','DOWN','LEFT','RIGHT','START','SELECT','MENU','A','B']
for name in names:
    source=doc.getObject(name+'Stem');x=source.Placement.Base.x;y=source.Placement.Base.y
    contact=doc.getObject('Ref_'+name).Shape.BoundBox.ZMax+.03
    fb=num('FlangeBottomZ');ft=num('FlangeT');top=num('ButtonTopZ');rise=num('DomeRise');rad=num('ButtonR')
    stem=cyl('V03'+name+'Contact',1.2,fb-contact+.04,x,y,contact)
    fl=cyl('V03'+name+'Flange',3.4,ft,x,y,fb)
    ears=box('V03'+name+'Ears',num('EarW'),num('EarLength'),ft,x-num('EarW')/2,y-num('EarLength')/2,fb)
    shaft=cyl('V03'+name+'Shaft',rad,top-rise-(fb+ft)+.02,x,y,fb+ft-.01)
    sphereR=(rad*rad+rise*rise)/(2*rise)
    dome=Part.makeSphere(sphereR,App.Vector(x,y,top-sphereR)).common(Part.makeCylinder(rad,rise+.01,App.Vector(x,y,top-rise)))
    cap=fuse('Button_'+name,[stem,fl,ears,shaft,feature('V03'+name+'Dome',dome)]);cap.Label='弧面按键 / 双定位耳 '+name;caps.append(cap)
    fronttools.append(cyl('V03'+name+'Guide',rad+.25,5,x,y,num('FrontUnderZ')-.1))
    fronttools.append(cyl('V03'+name+'FlangeRelief',3.65,1.8,x,y,num('FrontUnderZ')-1.65))
    # Rails sit outside the 6 mm switch body, and the cap ears remain under the roof.
    for sign in [-1,1]:
        yy=y+sign*3.85
        rail=box('V03'+name+'EarRail',3.6,2.25,1.6,x-1.8,yy-1.125,num('FrontUnderZ')-1.5)
        slot=box('V03'+name+'EarChannel',num('EarW')+2*num('EarGap'),2.45,1.65,x-num('EarW')/2-num('EarGap'),yy-1.225,num('FrontUnderZ')-1.55)
        earwalls.append(rail);earcuts.append(slot)

frontbase=fuse('V03FrontWithButtonRails',[frontbase]+earwalls)
fronttools+=earcuts

# GB-style captured power slider. Rest shown at the lower end of travel.
cy=num('SliderCy')-num('SliderTravel')/2;cz=br+num('SliderCzOffset')
flange=box('V03SliderFlange',1.0,6.8,4.2,40.55,cy-3.4,cz-2.1)
neck=box('V03SliderNeck',1.3,3.6,2.2,41.5,cy-1.8,cz-1.1)
thumb=box('V03SliderThumb',1.3,6.4,3.4,42.75,cy-3.2,cz-1.7)
fork=box('V03SliderFork',2.0,3.6,2.0,39.7,cy-1.8,cz-1.0)
socket=box('V03SliderSocket',1.75,num('SliderSocketW'),num('SliderSocketH'),39.6,cy-num('SliderSocketW')/2,cz-num('SliderSocketH')/2)
sliderbase=fuse('V03SliderUncut',[flange,neck,thumb,fork])
grips=[]
for delta in [-1.8,0,1.8]:grips.append(box('V03SliderGrip',.35,.6,2.5,44.0,cy+delta-.3,cz-1.25))
slider=cut('PowerSlider_v03',fuse('V03SliderWithGrip',[sliderbase]+grips),socket)
slider.Label='电源拨帽 / 内叉槽＋壳体捕获导轨'
# A small amount of extra travel prevents the plastic end stops loading the tiny switch.
travel=num('SliderTravel');mid=num('SliderCy')
innerchannel=box('V03SliderInnerTrack',1.4,6.8+travel+.5,5.0,40.3,mid-(6.8+travel+.5)/2,cz-2.35)
outerchannel=box('V03SliderOuterTrack',5,3.6+travel+.5,2.7,41.65,mid-(3.6+travel+.5)/2,cz-1.35)
forkchannel=box('V03ForkAssemblyRelief',1.1,3.6+travel+.5,2.5,39.65,mid-(3.6+travel+.5)/2,cz-1.25)
slidecuts=fuse('V03SliderTrackCutters',[innerchannel,outerchannel,forkchannel])
rearholes.append(slidecuts);fronttools.append(slidecuts)
rear=cut('RearShell_v03',rearbase,fuse('V03RearCutters',rearholes));rear.Label='后壳 v0.3 / 薄电池仓＋M2×5 深沉孔'
front=cut('FrontShell_v03',frontbase,fuse('V03FrontCutters',fronttools));front.Label='前壳 v0.3 / 浅屏幕＋定位导槽＋M2热熔孔'
doc.Battery_Assumed.Label='503550 电池占位 50×35×5 mm'
hw=doc.addObject('App::DocumentObjectGroup','Hardware_v03');hw.Label='非打印件 / M2×5 与 M2×2×3';hw.Group=inserts+screws
doc.recompute()

prints=[rear,front]+caps+[slider]
report={'revision':'0.3','units':'mm','shell_size_mm':[85,45,high],'old_shell_thickness_mm':24.5,'battery_envelope_mm':[56,36,5],'lcd_glass_recess_mm':low-glass,'button_protrusion_mm':num('ButtonTopZ')-high,'screw':'M2x5 head D4 t0.8','insert':'M2 internal, L2, OD3, pitch0.4','insert_pilot_diameter_mm':num('InsertPilotD'),'insert_engagement_mm':5-num('RearSeatT')-bt,'tf_throat_mm':[num('TFSlotW'),num('TFSlotH')],'usb_throat_mm':[10.4,4.6],'slider_socket_mm':[num('SliderSocketW'),num('SliderSocketH')],'slider_travel_mm':travel,'parts':[],'collisions':[],'clearances':{},'assumptions':['Battery finished envelope includes protection PCB and wrapping; exact battery pending.','MSK12C02 actuator 1.3x1.1 and projection1.5 from user drawing; exact travel not dimensioned, 1.8 mm carriage travel used.','Existing switch STEP body is kept as conservative clearance reference; deforming actuators excluded from press sweep.','Heat-insert ribs intentionally interfere with pilot hole; press temperature and pilot fit require a trial.']}
def collision(a,b,tag='assembly'):
    sa=a.Shape if hasattr(a,'Shape') else a;sb=b.Shape if hasattr(b,'Shape') else b
    if not sa.BoundBox.intersect(sb.BoundBox):return
    volume=sa.common(sb).Volume
    if volume>.001:report['collisions'].append({'a':a.Name if hasattr(a,'Name') else 'sweep','b':b.Name,'tag':tag,'volume_mm3':volume})
for o in prints:
    s=o.Shape
    if s.isNull():
        print('NULL',o.Name,[(a.Name,str(a.State)) for a in doc.Objects if 'Invalid' in str(a.State)],flush=True)
        doc.saveAs(str(OUT/'debug_v03.FCStd'))
        raise ValueError('Null shape: '+o.Name)
    report['parts'].append({'name':o.Name,'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume})
refs=list(doc.PCBReference.Group)+list(doc.ConnectorKeepouts.Group)
collision(rear,front)
for shell in [rear,front]:
    for r in refs:collision(shell,r)
for cap in caps:
    for r in [rear,front]+refs+[c for c in caps if c!=cap]:collision(cap,r)
    # Continuous conservative sweep: extend each primitive through the full
    # travel; the dome is bounded by the finger cylinder at its full height.
    name=cap.Name.split('_',1)[1];stem=doc.getObject('V03'+name+'Contact');b=stem.Shape.BoundBox
    x=stem.Placement.Base.x;y=stem.Placement.Base.y;fb=num('FlangeBottomZ');ft=num('FlangeT')
    swept_parts=[Part.makeCylinder(1.2,fb+.04-b.ZMin+.6,App.Vector(x,y,b.ZMin-.6)),
      Part.makeCylinder(3.4,ft+.6,App.Vector(x,y,fb-.6)),
      Part.makeBox(num('EarW'),num('EarLength'),ft+.6,App.Vector(x-num('EarW')/2,y-num('EarLength')/2,fb-.6)),
      Part.makeCylinder(num('ButtonR'),num('ButtonTopZ')-(fb+ft)+.61,App.Vector(x,y,fb+ft-.61))]
    sweep=swept_parts[0].multiFuse(swept_parts[1:])
    for r in [rear,front]+refs+[c for c in caps if c!=cap]:
        if r.Name=='Ref_'+cap.Name.split('_',1)[1]:continue
        collision(sweep,r,'button continuous 0–0.6 mm conservative sweep')
for r in [rear,front]+refs:
    collision(slider,r,'slider rest')
slider_swept=[]
for o in [flange,neck,thumb,fork]+grips:
    b=o.Shape.BoundBox
    slider_swept.append(Part.makeBox(b.XLength,b.YLength+travel,b.ZLength,App.Vector(b.XMin,b.YMin,b.ZMin)))
slider_sweep=slider_swept[0].multiFuse(slider_swept[1:])
for r in [rear,front]+refs:
    if r.Name=='Ref_SW3':continue
    collision(slider_sweep,r,'slider continuous 0–2.3 mm conservative sweep')
for moving in [doc.Battery_Assumed,doc.Speaker_ToleranceEnvelope]:
    for r in refs:
        if r.Name in ['Battery_Assumed','Speaker_1510','Speaker_ToleranceEnvelope','Speaker_TabEnvelope']:continue
        collision(moving,r,'battery/speaker layout')
for screw in screws:
    for r in refs:collision(screw,r,'hardware')
for name,a,b in [('battery_ESP32',doc.Battery_Assumed,doc.Ref_U1),('battery_USB',doc.Battery_Assumed,doc.USB_Envelope),('battery_connector',doc.Battery_Assumed,doc.SPEAKER_ConnectorEnvelope),('battery_plug',doc.Battery_Assumed,doc.SPEAKER_PlugEnvelope)]:
    report['clearances'][name]=a.Shape.distToShape(b.Shape)[0]
doc.saveAs(str(OUT/'myMicrobyte_enclosure_v03.FCStd'))
report['battery_envelope_mm']=[50,35,5]
report['battery_frame_clear_mm']=[57,37]
report['button_continuous_travel_mm']=.6
report['assumptions'][0]='503550 chosen by user: nominal 50x35x5 mm. Seller finished dimensions including protection PCB and wrap are not supplied.'
report['assumptions'][1]='MSK12C02 actuator 1.3x1.1 and projection1.5 from user drawing. Exact stroke not dimensioned: 2.3 mm carriage travel minus 0.5 mm fork clearance accommodates up to1.8 mm actuator travel; verify both electrical end positions at trial fit.'
(REPORT/'fit_check_v03.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
assert all(x['valid'] and x['solids']==1 for x in report['parts']),'invalid print solid'
assert not report['collisions'],'CAD collision; inspect report before export'
Part.export(prints,str(OUT/'myMicrobyte_enclosure_v03.step'))
for o in prints:
    s=o.Shape.copy()
    if o==front:s.rotate(App.Vector(),App.Vector(1,0,0),180)
    elif o==slider:s.rotate(App.Vector(),App.Vector(0,1,0),90)
    # Caps print upright on a common flat flange/stem datum, with support below
    # ears as needed; curved finger surface remains upward and support-free.
    b=s.BoundBox;s.translate(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.035,AngularDeflection=.1,Relative=False)
    assert mesh.isSolid(),o.Name
    name='RearShell' if o==rear else 'FrontShell' if o==front else 'Cap_'+o.Name[7:] if o.Name.startswith('Button_') else 'PowerSlider'
    mesh.write(str(OUT/(name+'_print.stl')))
