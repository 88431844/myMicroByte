"""Update the native v0.1 design for the supplied LCD and 1510 speaker.

Run using FreeCAD's bundled Python, or from its Python console. All additions
are editable native Part primitives/booleans tied to the Parameters sheet.
"""
import sys, json, math
from pathlib import Path
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, MeshPart

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/v02'; REPORT=ROOT/'reports/v02'
OUT.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
doc=App.openDocument(str(ROOT/'output/myMicrobyte_enclosure_v01.FCStd'))
doc.Label='myMicrobyte v0.2 — LCD 1.9 mm / 1510 / battery frame'
p=doc.Parameters
def parameter(alias,value,note):
    # Preserve the existing sheet and its aliases.
    for row in range(1,150):
        if p.getAlias('B'+str(row))==alias:
            p.set('B'+str(row),str(value));p.set('A'+str(row),note);return
    for row in range(1,150):
        if 'B'+str(row) not in p.getNonEmptyCells():
            p.set('A'+str(row),note);p.set('B'+str(row),str(value));p.setAlias('B'+str(row),alias);return

for alias,value,note in [
 ('BatteryW',56,'电池最大成品轮廓 X（含保护板）'),
 ('BatteryH',36,'电池最大成品轮廓 Y（含保护板）'),
 ('BatteryT',6,'推荐电池最大成品厚度'),
 ('BatteryCx',-4,'电池中心 X'),('BatteryCy',0,'电池中心 Y'),
 ('BatteryAdhesive',0.3,'电池底部胶层预留'),
 ('BatteryGap',0.5,'电池框单边装配余量'),
 ('FrameWall',1.2,'电池/喇叭定位框壁厚'),('BatteryFrameH',2.4,'电池框高度'),
 ('LCDThickness',1.9,'LCD 标称厚度（图1）'),('LCDAdhesive',0.1,'LCD 胶层'),
 ('LCDTolerance',0.1,'LCD 厚度正公差'),('LCDAssemblyExtra',0.1,'LCD 安装叠高额外预留'),
 ('GlassGap',0.4,'窗口内圈距最坏玻璃面的间隙'),
 ('SpeakerCx',33,'喇叭中心 X（TF 侧的侧边区域）'),('SpeakerCy',4.5,'喇叭中心 Y'),
 ('SpeakerW',10,'喇叭短边 X'),('SpeakerL',15,'喇叭长边 Y'),('SpeakerT',3.5,'1510 喇叭厚度'),
 ('SpeakerXYTol',0.2,'喇叭平面尺寸正公差'),('SpeakerZTol',0.3,'喇叭厚度正公差'),
 ('SpeakerGap',0.4,'喇叭座单边间隙'),('SpeakerSeatH',0.4,'喇叭座支承环高度'),
 ('SpeakerTape',0.3,'喇叭边缘泡棉胶层预留'),('SpeakerFrameH',3.2,'喇叭定位框高度'),
 ('ConnectorDepth',5.5,'端子及插头保守垂直包络（未实测）'),
 ('BatteryTopGap',0.7,'电池到端子包络最小预留')]:
    parameter(alias,value,note)

def setprop(o,key,value):
    if isinstance(value,str):o.setExpression(key,value)
    elif key.startswith('Placement.Base.'):
        v=o.Placement.Base;setattr(v,key[-1],value);o.Placement.Base=v
    else:setattr(o,key,value)
def box(name,w,h,d,x,y,z):
    o=doc.addObject('Part::Box',name)
    for k,v in [('Length',w),('Width',h),('Height',d),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:setprop(o,k,v)
    return o
def cyl(name,r,h,x,y,z):
    o=doc.addObject('Part::Cylinder',name)
    for k,v in [('Radius',r),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:setprop(o,k,v)
    return o
def fuse(name,parts):
    o=doc.addObject('Part::MultiFuse',name);o.Shapes=parts;o.Refine=True;return o
def cut(name,a,b):
    o=doc.addObject('Part::Cut',name);o.Base=a;o.Tool=b;o.Refine=True;return o
def capsule(name,w,l,z,h,cx='Parameters.SpeakerCx',cy='Parameters.SpeakerCy'):
    mid=box(name+'Middle',w,f'({l})-({w})',h,f'({cx})-({w})/2',f'({cy})-(({l})-({w}))/2',z)
    ends=[cyl(name+'End',f'({w})/2',h,cx,f'({cy})+{sign}*(({l})-({w}))/2',z) for sign in [-1,1]]
    return fuse(name,[mid]+ends)

# Bring the display to the user-confirmed PCB-to-glass stack height.
lcd=doc.LCD_Assumed_5mm
lcd.setExpression('Height','Parameters.LCDThickness+Parameters.LCDAdhesive')
lcd.Label='LCD 31.52×33.72；1.9 mm + 0.1 mm 胶层'
lcd.addProperty('App::PropertyString','SourceNote').SourceNote='用户图1；1.9±0.1 mm，PCB 上胶粘安装，0.1 mm 胶层'
bezelZ='Parameters.BoardRearZ+Parameters.BoardT+Parameters.LCDThickness+Parameters.LCDAdhesive+Parameters.LCDTolerance+Parameters.LCDAssemblyExtra+Parameters.GlassGap'
bezelouter=box('ScreenTunnelOuter','Parameters.WindowW+4','Parameters.WindowH+4',f'Parameters.FrontUnderZ-({bezelZ})+0.1',
 'Parameters.ScreenCx-Parameters.WindowW/2-2','Parameters.ScreenCy-Parameters.WindowH/2-2',bezelZ)
bezelinner=box('ScreenTunnelVoid','Parameters.WindowW','Parameters.WindowH',f'Parameters.FrontUnderZ-({bezelZ})+0.4',
 'Parameters.ScreenCx-Parameters.WindowW/2','Parameters.ScreenCy-Parameters.WindowH/2',f'({bezelZ})-0.1')
bezel=cut('ScreenTunnel',bezelouter,bezelinner)
front=fuse('FrontShell_v02',[doc.FrontShell,bezel]);front.Label='前壳 v0.2 / 低屏幕窗口内圈'

# Remove the generic v0.1 grille. Its cutters are editable leaves in the tree.
oldcutters=doc.RearCutters
oldcutters.Shapes=[o for o in oldcutters.Shapes if not o.Name.startswith('SpeakerSlot')]
rearbase=doc.RearShell

# Open-top battery rectangle, with a flat uninterrupted adhesive floor.
battery=doc.Battery_Assumed
battery.setExpression('Placement.Base.x','Parameters.BatteryCx-Parameters.BatteryW/2')
battery.setExpression('Placement.Base.y','Parameters.BatteryCy-Parameters.BatteryH/2')
battery.setExpression('Placement.Base.z','Parameters.Floor+Parameters.BatteryAdhesive')
battery.Label='电池选型包络：成品不超过 56×36×6 mm'
bw='Parameters.BatteryW+2*Parameters.BatteryGap';bh='Parameters.BatteryH+2*Parameters.BatteryGap'
fo=box('BatteryFrameOuter',f'({bw})+2*Parameters.FrameWall',f'({bh})+2*Parameters.FrameWall','Parameters.BatteryFrameH+0.1',
 f'Parameters.BatteryCx-({bw})/2-Parameters.FrameWall',f'Parameters.BatteryCy-({bh})/2-Parameters.FrameWall','Parameters.Floor-0.1')
fi=box('BatteryFrameVoid',bw,bh,'Parameters.BatteryFrameH+0.4',f'Parameters.BatteryCx-({bw})/2',f'Parameters.BatteryCy-({bh})/2','Parameters.Floor-0.2')
frame=cut('BatteryFrame',fo,fi);frame.Label='电池矩形胶粘定位框；内净空 57×37'

# Capsule holder: long axis Y, front/diaphragm faces the rear grille (-Z).
sw='Parameters.SpeakerW+2*Parameters.SpeakerGap';sl='Parameters.SpeakerL+2*Parameters.SpeakerGap'
so=capsule('SpeakerFrameOuter',f'({sw})+2*Parameters.FrameWall',f'({sl})+2*Parameters.FrameWall','Parameters.Floor-0.1','Parameters.SpeakerFrameH+0.1')
si=capsule('SpeakerFrameVoid',sw,sl,'Parameters.Floor-0.2','Parameters.SpeakerFrameH+0.5')
speakerwall=cut('SpeakerFrameWalls',so,si)
seatOuter=capsule('SpeakerSeatOuter',sw,sl,'Parameters.Floor-0.1','Parameters.SpeakerSeatH+0.1')
seatInner=capsule('SpeakerSeatVoid',8,13,'Parameters.Floor-0.2','Parameters.SpeakerSeatH+0.5')
seat=cut('SpeakerSeat',seatOuter,seatInner);seat.Label='喇叭支承环；仅边缘泡棉粘贴，避开振膜'
lead=box('SpeakerLeadNotch',4,5,4,'Parameters.SpeakerCx-2','Parameters.SpeakerCy+Parameters.SpeakerL/2-0.8','Parameters.Floor+0.7')
tabrelief=box('SpeakerTabRelief',3.5,4.6,4,'Parameters.SpeakerCx-1.75','Parameters.SpeakerCy-Parameters.SpeakerL/2-3','Parameters.Floor+0.3')
speakerframe=cut('SpeakerFrame',fuse('SpeakerFrameAndSeat',[speakerwall,seat]),fuse('SpeakerEndReliefs',[lead,tabrelief]))
speakerframe.Label='1510 喇叭座；出线朝 TF/喇叭端子方向'
grille=[]
for dy in [-4.8,-2.4,0,2.4,4.8]:
    # All slots lie inside the 8×13 diaphragm opening.
    grille.append(box('SpeakerGrilleSlot',6,1.0,'Parameters.Floor+0.4','Parameters.SpeakerCx-3',f'Parameters.SpeakerCy+({dy})-0.5',-0.1))
rearwithframes=fuse('RearWithBatteryAndSpeakerFrames',[rearbase,frame,speakerframe])
reargrille=cut('RearWith1510Grille',rearwithframes,fuse('SpeakerGrilleCutters',grille))

# Connector body/plug envelopes derived in XY from the PCB footprint, with a
# deliberately conservative 5.5 mm depth; the bad STEP bindings stay excluded.
keepouts=doc.addObject('App::DocumentObjectGroup','ConnectorKeepouts')
keepouts.Label='端子/插头保守占位：XY 来自封装，厚度尚未实测'
connectors=[]
for name,w,h,x,y in [
 ('BAT_ConnectorEnvelope',7.6,4.5,31.628,7.952),
 ('BAT_PlugEnvelope',6.0,3.0,32.428,12.452),
 ('SPEAKER_ConnectorEnvelope',4.5,7.6,-12.439,11.633),
 ('SPEAKER_PlugEnvelope',3.0,6.0,-7.939,12.433)]:
    o=box(name,w,h,'Parameters.ConnectorDepth',x,y,'Parameters.BoardRearZ-Parameters.ConnectorDepth')
    o.Label=name+'（保守包络）';keepouts.addObject(o);connectors.append(o)
# A shallow local relief above the BAT insertion corridor keeps the existing
# corner post clear; leave the screw bore and its local ligament intact.
relief=box('BAT_PostServiceRelief',6.6,3.4,'Parameters.ConnectorDepth+0.2',32.128,12.252,'Parameters.BoardRearZ-Parameters.ConnectorDepth-0.1')
rear=cut('RearShell_v02',reargrille,relief);rear.Label='后壳 v0.2 / 电池矩形框 + 1510 喇叭座'

speaker=capsule('Speaker_1510','Parameters.SpeakerW','Parameters.SpeakerL',
 'Parameters.Floor+Parameters.SpeakerSeatH+Parameters.SpeakerTape','Parameters.SpeakerT')
speaker.Label='1510 喇叭 15×10×3.5 mm；朝后发声'
doc.PCBReference.addObject(speaker)
speakermax=capsule('Speaker_ToleranceEnvelope','Parameters.SpeakerW+Parameters.SpeakerXYTol','Parameters.SpeakerL+Parameters.SpeakerXYTol',
 'Parameters.Floor+Parameters.SpeakerSeatH+Parameters.SpeakerTape','Parameters.SpeakerT+Parameters.SpeakerZTol+0.1')
speakermax.Label='喇叭最坏外形包络（含尺寸公差及额外胶厚）';keepouts.addObject(speakermax)
tabmax=box('Speaker_TabEnvelope',3.0,2.5,1.0,'Parameters.SpeakerCx-1.5','Parameters.SpeakerCy-Parameters.SpeakerL/2-2.5',
 'Parameters.Floor+Parameters.SpeakerSeatH+Parameters.SpeakerTape')
tabmax.Label='图2未注尺寸凸耳：3×2.5×1 保守预留，需试装';keepouts.addObject(tabmax)
lcdmax=box('LCD_ToleranceEnvelope',31.72,33.92,'Parameters.LCDThickness+Parameters.LCDAdhesive+Parameters.LCDTolerance+Parameters.LCDAssemblyExtra',
 -15.75,-18.387,'Parameters.BoardRearZ+Parameters.BoardT')
lcdmax.Label='LCD 正公差与胶层安装包络';keepouts.addObject(lcdmax)
doc.recompute()

# Native fit and motion validation, kept alongside this revision's exports.
caps=[o for o in doc.Objects if o.Name.startswith('Cap_')]
prints=[rear,front]+caps
report={'revision':'0.2','units':'mm','fit_scope':'Retained STEP geometry, supplied LCD/speaker dimensions, conservative connector envelopes. Invalid STEP bindings, actual plug mouldings and battery wires remain unverified.',
 'battery_recommended_finished_envelope_mm':[56,36,6],
 'battery_frame_clear_mm':[57,37], 'speaker_nominal_mm':[15,10,3.5],
 'lcd_nominal_stack_mm':2.0,'lcd_checked_stack_mm':2.2,
 'parts':[], 'collisions':[], 'minimum_clearances_mm':{},'cap_sweep_mm':0.8}
for o in prints:
    s=o.Shape
    assert s.isValid() and len(s.Solids)==1 and s.Volume>0,o.Name
    report['parts'].append({'name':o.Name,'valid':True,'solids':len(s.Solids),'volume_mm3':s.Volume})
refs=list(doc.PCBReference.Group)+list(keepouts.Group)
def collide(a,b):
    if not a.Shape.BoundBox.intersect(b.Shape.BoundBox):return
    v=a.Shape.common(b.Shape).Volume
    if v>0.001:report['collisions'].append({'a':a.Name,'b':b.Name,'volume_mm3':v})
collide(rear,front)
for a in [rear,front]:
    for b in refs:collide(a,b)
for a in [battery,speakermax,tabmax]:
    for b in refs:
        if b==a or b in [battery,speaker,speakermax,tabmax,lcd,lcdmax]:continue
        collide(a,b)
collide(battery,speakermax)
collide(battery,tabmax)
for cap in caps:
    stem=doc.getObject(cap.Name[4:]+'Stem');x,y=stem.Placement.Base.x,stem.Placement.Base.y
    n=lambda k:float(getattr(p,k))
    shapes=[]
    for radius,z,h in [(n('StemR'),n('StemBottomZ'),n('FlangeBottomZ')-n('StemBottomZ')),
      (n('FlangeR'),n('FlangeBottomZ'),n('FlangeT')),
      (n('ButtonR'),n('FlangeBottomZ')+n('FlangeT'),n('ButtonTopZ')-n('FlangeBottomZ')-n('FlangeT'))]:
        shapes.append(Part.makeCylinder(radius,h+0.8,App.Vector(x,y,z-0.8)))
    sweep=shapes[0].multiFuse(shapes[1:]).removeSplitter()
    for o in [rear,front]+refs+[c for c in caps if c!=cap]:
        if o.Label==cap.Name[4:]:continue
        if sweep.BoundBox.intersect(o.Shape.BoundBox):
            v=sweep.common(o.Shape).Volume
            if v>0.001:report['collisions'].append({'cap_sweep':cap.Name,'obstacle':o.Name,'volume_mm3':v})
clear=report['minimum_clearances_mm']
for name,a,b in [('battery_to_ESP32',battery,doc.Ref_U1),('battery_to_USB',battery,doc.USB_Envelope),
 ('battery_to_speaker_connector',battery,connectors[2]),('battery_to_speaker_plug',battery,connectors[3]),
 ('battery_frame_to_speaker_frame',frame,speakerframe),('glass_to_window_tunnel',lcdmax,bezel),
 ('speaker_to_BAT_connector',speakermax,connectors[0])]:
    clear[name]=a.Shape.distToShape(b.Shape)[0]
report['battery_thickness_upper_bound_at_this_footprint_mm']=float(p.BoardRearZ)-float(p.ConnectorDepth)-float(p.Floor)-float(p.BatteryAdhesive)-float(p.BatteryTopGap)
report['speaker_wire_route_estimate_mm']=math.dist((33,12),(30,14))+math.dist((30,14),(-4.939,15.433))+3
report['speaker_wire_route_scope']='Plan-view estimate plus 3 mm end allowance; 50±3 mm wire must be checked physically for plug/crimp and bends.'
(REPORT/'fit_check_v02.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
assert not report['collisions'],report['collisions']

if App.GuiUp:
    for o in doc.Objects:
        if o.ViewObject:o.ViewObject.Visibility=False
    for o in prints+list(doc.PCBReference.Group):o.ViewObject.Visibility=True
    for o in [rear,front]+caps:o.ViewObject.ShapeColor=(0.13,0.135,0.14)
    front.ViewObject.Transparency=0
    lcd.ViewObject.ShapeColor=(0.025,0.075,0.095)
    battery.ViewObject.ShapeColor=(0.65,0.67,0.71);battery.ViewObject.Transparency=0
    speaker.ViewObject.ShapeColor=(0.35,0.36,0.38)
    for o in doc.PCBReference.Group:
        if o.Name.startswith('Ref_'):o.ViewObject.ShapeColor=(0.15,0.42,0.25)
    doc.PCBReference.ViewObject.Visibility=True
doc.recompute()
doc.saveAs(str(OUT/'myMicrobyte_enclosure_v02.FCStd'))
Part.export(prints,str(OUT/'myMicrobyte_enclosure_v02.step'))
for o in prints:
    shape=o.Shape.copy()
    if o!=rear:shape.rotate(App.Vector(),App.Vector(1,0,0),180)
    b=shape.BoundBox;shape.translate(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
    m=MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.06,AngularDeflection=0.12,Relative=False)
    assert m.isSolid(),o.Name
    name='RearShell' if o==rear else 'FrontShell' if o==front else o.Name
    m.write(str(OUT/(name+'_print.stl')))
print(json.dumps(report,indent=2,ensure_ascii=False))
