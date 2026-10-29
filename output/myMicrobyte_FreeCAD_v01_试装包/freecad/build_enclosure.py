"""Build a native FreeCAD boolean feature tree. Run with FreeCAD bundled Python."""
import sys, json, math
from pathlib import Path
sys.path.insert(0, '/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, Import, MeshPart

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
doc = App.newDocument('myMicrobyte_Enclosure_v01')
p = doc.addObject('Spreadsheet::Sheet','Parameters')
p.Label = '尺寸参数（mm） / Parameters'
values = [
 ('BoardW',80,'PCB 宽'),('BoardH',40,'PCB 高'),('BoardT',1.60005,'PCB 厚'),
 ('EdgeGap',0.5,'PCB 单边间隙'),('Wall',2,'侧壁厚'),('Floor',2,'后壳底厚'),
 ('OuterR',5.5,'外轮廓圆角'),('BoardRearZ',15,'PCB 元件面高度'),
 ('SeamGap',0.2,'两壳分缝'),('FrontUnderZ',22.9,'前面板内侧高度'),
 ('Face',1.6,'前面板厚'),('BossR',3,'螺柱半径'),('RearHoleR',1.15,'后壳 M2 通孔半径'),
 ('PilotR',0.85,'前壳 M2 自攻预孔半径'),('ButtonR',2.7,'按钮半径'),
 ('ButtonGap',0.25,'按钮径向间隙'),('FlangeR',3.4,'按键防脱凸缘半径'),
 ('FlangeBottomZ',22.25,'按键凸缘底'),('FlangeT',0.6,'按键凸缘厚'),
 ('StemBottomZ',21.95,'按键推杆底（待实物校准）'),('StemR',1.25,'推杆半径'),
 ('ButtonTopZ',25.1,'按键顶'),('WindowW',28.52,'显示窗口宽'),('WindowH',28.52,'显示窗口高'),
 ('ScreenCx',0.110,'显示中心 X'),('ScreenCy',0.123,'显示中心 Y'),
 ('BatteryW',50,'电池占位宽：假定'),('BatteryH',30,'电池占位高：假定'),('BatteryT',6,'电池占位厚：假定')]
for i,(alias,v,note) in enumerate(values,1):
 p.set('A%d'%i,note);p.set('B%d'%i,str(v));p.setAlias('B%d'%i,alias)
p.setColumnWidth('A',265);p.setColumnWidth('B',110)
def expr(o,k,v):
 if isinstance(v,str):o.setExpression(k,v)
 else:setattr(o,k,v)
def box(name,w,h,d,x,y,z):
 o=doc.addObject('Part::Box',name)
 for k,v in [('Length',w),('Width',h),('Height',d),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:
  if isinstance(v,str):o.setExpression(k,v)
  elif k.startswith('Placement'):
   base=o.Placement.Base;setattr(base,k[-1],v);o.Placement.Base=base
  else:setattr(o,k,v)
 return o
def cyl(name,r,h,x,y,z):
 o=doc.addObject('Part::Cylinder',name)
 for k,v in [('Radius',r),('Height',h),('Placement.Base.x',x),('Placement.Base.y',y),('Placement.Base.z',z)]:
  if isinstance(v,str):o.setExpression(k,v)
  elif k.startswith('Placement'):
   base=o.Placement.Base;setattr(base,k[-1],v);o.Placement.Base=base
  else:setattr(o,k,v)
 return o
def fuse(name,objects):
 o=doc.addObject('Part::MultiFuse',name);o.Shapes=objects;o.Refine=True;return o
def cut(name,base,tool):
 o=doc.addObject('Part::Cut',name);o.Base=base;o.Tool=tool;o.Refine=True;return o
def rounded(name,w,h,r,z,d):
 parts=[box(name+'X',f'({w})-2*({r})',h,d,f'-({w})/2+({r})',f'-({h})/2',z),
        box(name+'Y',w,f'({h})-2*({r})',d,f'-({w})/2',f'-({h})/2+({r})',z)]
 for sx in [-1,1]:
  for sy in [-1,1]:parts.append(cyl(name+'Corner',r,d,f'{sx}*(({w})/2-({r}))',f'{sy}*(({h})/2-({r}))',z))
 return fuse(name,parts)
W='Parameters.BoardW+2*(Parameters.EdgeGap+Parameters.Wall)'
H='Parameters.BoardH+2*(Parameters.EdgeGap+Parameters.Wall)'
IW='Parameters.BoardW+2*Parameters.EdgeGap';IH='Parameters.BoardH+2*Parameters.EdgeGap'
R='Parameters.OuterR';IR='Parameters.OuterR-Parameters.Wall'
PZ='Parameters.BoardRearZ+Parameters.BoardT'
rearouter=rounded('RearOuter',W,H,R,0,'Parameters.BoardRearZ')
rearvoid=rounded('RearCavity',IW,IH,IR,'Parameters.Floor','Parameters.BoardRearZ')
rearbase=cut('RearWallsAndFloor',rearouter,rearvoid)
holes=[(37.46,17.46),(37.46,-17.46),(-37.46,17.46),(-37.46,-17.46)]
rearposts=[cyl('RearPost','Parameters.BossR','Parameters.BoardRearZ-Parameters.Floor',x,y,'Parameters.Floor') for x,y in holes]
rearbase=fuse('RearWithPosts',[rearbase]+rearposts)
# Tongue surrounds the PCB, with a receiving recess in the front shell.
tongueouter=rounded('TongueOuter',f'({IW})+1.6',f'({IH})+1.6',f'({IR})+0.8','Parameters.BoardRearZ',1.3)
tongueinner=rounded('TongueVoid',IW,IH,IR,'Parameters.BoardRearZ-0.05',1.4)
tongue=cut('Tongue',tongueouter,tongueinner)
rearbase=fuse('RearWithTongue',[rearbase,tongue])
frontbottom='Parameters.BoardRearZ+Parameters.SeamGap'
fronttop='Parameters.FrontUnderZ+Parameters.Face'
frontouter=rounded('FrontOuter',W,H,R,frontbottom,f'({fronttop})-({frontbottom})')
frontvoid=rounded('FrontCavity',IW,IH,IR,f'({frontbottom})-0.1',f'Parameters.FrontUnderZ-({frontbottom})+0.1')
frontbase=cut('FrontWallsAndFace',frontouter,frontvoid)
receiver=rounded('TongueReceiver',f'({IW})+2.0',f'({IH})+2.0',f'({IR})+1.0',f'({frontbottom})-0.05',1.5)
frontbase=cut('FrontTongueClearance',frontbase,receiver)
frontposts=[cyl('FrontPost','Parameters.BossR',f'Parameters.FrontUnderZ-({PZ})',x,y,PZ) for x,y in holes]
frontbase=fuse('FrontWithPosts',[frontbase]+frontposts)
rearholes=[cyl('RearScrew','Parameters.RearHoleR','Parameters.BoardRearZ+3',x,y,-1) for x,y in holes]
rearholes += [cyl('ScrewHeadRecess',2.2,0.9,x,y,-0.1) for x,y in holes]
frontholes=[cyl('FrontPilot','Parameters.PilotR',f'Parameters.FrontUnderZ-({PZ})+0.15',x,y,f'({PZ})-0.1') for x,y in holes]
# Connector apertures. Coordinates use X = 40 - PCB X; Y = PCB Y - 20.
ports=[box('USBAccess',12.4,7,6.5,-6.4,-25,'Parameters.BoardRearZ-4.5'),
       box('TFAccess',17.4,7,5.5,-3.85,18.5,'Parameters.BoardRearZ-4'),
       box('PowerSliderAccess',7,10.2,6,39.5,-10.5,'Parameters.BoardRearZ-4.8')]
porttool=fuse('ConnectorOpenings',ports)
rearholes.append(porttool);frontholes.append(porttool)
screenhole=box('ScreenWindow','Parameters.WindowW','Parameters.WindowH',4,
 'Parameters.ScreenCx-Parameters.WindowW/2','Parameters.ScreenCy-Parameters.WindowH/2','Parameters.FrontUnderZ-0.1')
frontholes.append(screenhole)
buttons=[('UP',68.707,26.543),('DOWN',68.707,15.240),('LEFT',74.168,20.955),('RIGHT',63.119,20.828),
 ('START',16.002,4.826),('SELECT',63.246,4.826),('MENU',16.002,34.798),('A',5.715,20.955),('B',14.097,17.272)]
caps=[]
for name,bx,by in buttons:
 x,y=40-bx,by-20
 frontholes.append(cyl(name+'Guide','Parameters.ButtonR+Parameters.ButtonGap',4,x,y,'Parameters.FrontUnderZ-0.05'))
 stem=cyl(name+'Stem','Parameters.StemR','Parameters.FlangeBottomZ-Parameters.StemBottomZ',x,y,'Parameters.StemBottomZ')
 flange=cyl(name+'Flange','Parameters.FlangeR','Parameters.FlangeT',x,y,'Parameters.FlangeBottomZ')
 shaft=cyl(name+'Finger','Parameters.ButtonR','Parameters.ButtonTopZ-Parameters.FlangeBottomZ-Parameters.FlangeT',x,y,'Parameters.FlangeBottomZ+Parameters.FlangeT')
 cap=fuse('Cap_'+name,[stem,flange,shaft]);cap.Label='按键帽 '+name;caps.append(cap)
# A conservative speaker grille; no holder before the real speaker is known.
for x in [27,30,33,36]:
 rearholes.append(box('SpeakerSlot',1.2,9,3,x-0.6,-4.5,-0.5))
rear=cut('RearShell',rearbase,fuse('RearCutters',rearholes));rear.Label='后壳 / Rear shell'
front=cut('FrontShell',frontbase,fuse('FrontCutters',frontholes));front.Label='前壳 / Front shell'
doc.recompute()

# Retain believable component models; many LCEDA bindings are in inches at mm scale.
refdoc=App.newDocument('PCBImport');Import.insert(str(ROOT/'reference/pcb-current.step'),refdoc.Name)
root=next(o for o in refdoc.Objects if not o.InList)
refgroup=doc.addObject('App::DocumentObjectGroup','PCBReference');refgroup.Label='PCB 参考（已剔除异常绑定模型）'
transform=App.Placement(App.Vector(40,-20,16.60005),App.Rotation(App.Vector(0,1,0),180))
retained=[];rejected=[];pcbshapes=[]
for o in root.Group:
 if not hasattr(o,'Shape') or o.Shape.isNull():continue
 s=o.Shape.copy();b=s.BoundBox
 designator=o.Label.split('~')[0]
 if (b.XLength>40 or b.YLength>40 or b.ZLength>12) and not designator.startswith('Board'):
  rejected.append(designator);continue
 s.Placement=transform.multiply(s.Placement)
 f=doc.addObject('Part::Feature','Ref_'+designator.replace('-','_'));f.Label=designator;f.Shape=s;f.setExpression('Placement.Base.z',f'Parameters.BoardRearZ+Parameters.BoardT+({s.Placement.Base.z-16.60005})');refgroup.addObject(f)
 pcbshapes.append((designator,s));retained.append(designator)
App.closeDocument(refdoc.Name)
App.setActiveDocument(doc.Name)
def reference_box(name,w,h,t,x,y,z):
 f=box(name,w,h,t,x,y,z);refgroup.addObject(f);return f
screen=reference_box('LCD_Assumed_5mm',31.52,33.72,5,-15.65,-18.287,PZ)
screen.Label='屏幕占位：高度假定 5 mm'
battery=reference_box('Battery_Assumed','Parameters.BatteryW','Parameters.BatteryH','Parameters.BatteryT',
 '-Parameters.BatteryW/2','-Parameters.BatteryH/2','Parameters.Floor+1')
battery.Label='电池占位：假定 50×30×6 mm'
usb=reference_box('USB_Envelope',9.4,7.2,3.6,-4.7,-21.2,'Parameters.BoardRearZ-3.6')
usb.Label='USB 保守占位（绑定模型异常）'
doc.recompute()

printables=[rear,front]+caps
if App.GuiUp:
 for o in doc.Objects:
  if hasattr(o,'ViewObject'):o.ViewObject.Visibility=False
 for o in printables:o.ViewObject.Visibility=True
 for o in refgroup.Group:o.ViewObject.Visibility=True
 for o in [rear,front]:o.ViewObject.ShapeColor=(0.16,0.23,0.31)
 front.ViewObject.Transparency=15
 for o in caps:o.ViewObject.ShapeColor=(0.95,0.45,0.16)
 for o in refgroup.Group:
  o.ViewObject.ShapeColor=(0.18,0.58,0.30)
 screen.ViewObject.ShapeColor=(0.08,0.12,0.15)
 battery.ViewObject.ShapeColor=(0.6,0.6,0.65);battery.ViewObject.Transparency=70
 usb.ViewObject.ShapeColor=(0.7,0.7,0.75)
doc.recompute()
report={'units':'mm','status':'prototype; actual battery, LCD height, speaker and connector cable fit pending',
 'retained_step_components':retained,'excluded_abnormally_scaled_models':rejected,'parts':[], 'intersections':[]}
for o in printables:
 s=o.Shape;report['parts'].append({'name':o.Name,'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume})
 assert s.isValid() and len(s.Solids)==1 and s.Volume>0,(o.Name,s.isValid(),len(s.Solids))
for shell in [rear,front]:
 for name,s in pcbshapes:
  v=shell.Shape.common(s).Volume
  if v>0.01:report['intersections'].append({'shell':shell.Name,'pcb_component':name,'volume_mm3':v})
report['shell_overlap_mm3']=rear.Shape.common(front.Shape).Volume
report['screen_shell_overlap_mm3']=sum(o.Shape.common(screen.Shape).Volume for o in [rear,front])
report['battery_shell_overlap_mm3']=sum(o.Shape.common(battery.Shape).Volume for o in [rear,front])
report['usb_shell_overlap_mm3']=sum(o.Shape.common(usb.Shape).Volume for o in [rear,front])
report['cap_switch_overlap_mm3']=sum(c.Shape.common(s).Volume for c in caps for name,s in pcbshapes if name in [v[0] for v in buttons])
report['cap_shell_overlap_mm3']=sum(c.Shape.common(o.Shape).Volume for c in caps for o in [rear,front])
# The position-specific battery clearance is derived by verify_motion_and_make_coupons.py.
doc.saveAs(str(OUT/'myMicrobyte_enclosure_v01.FCStd'))
Part.export(printables,str(OUT/'myMicrobyte_enclosure_v01.step'))
for o in [rear,front]:
 s=o.Shape.copy()
 if o==front:s.rotate(App.Vector(),App.Vector(1,0,0),180)
 b=s.BoundBox;s.translate(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
 MeshPart.meshFromShape(Shape=s,LinearDeflection=0.08,AngularDeflection=0.15,Relative=False).write(str(OUT/(o.Name+'_print.stl')))
# Separate cap STLs, face down; supports are needed underneath the retaining flange.
for o in caps:
 s=o.Shape.copy();s.rotate(App.Vector(),App.Vector(1,0,0),180);b=s.BoundBox;s.translate(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
 MeshPart.meshFromShape(Shape=s,LinearDeflection=0.04,AngularDeflection=0.1,Relative=False).write(str(OUT/(o.Name+'_print.stl')))
(ROOT/'reports'/'fit_check.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps(report,indent=2,ensure_ascii=False))
