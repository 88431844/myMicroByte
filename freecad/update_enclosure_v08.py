"""FreeCAD v0.8: dry-fit speaker clips and snap/hook lid; no glue or gasket.
Regenerate with FreeCAD's bundled Python. Millimetres; source PCB XY preserved.
Parameters are documented in the native sheet; edit VALUES here and regenerate.
"""
from pathlib import Path
import sys, json
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, MeshPart
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/v08'; REPORT=ROOT/'reports/v08'
OUT.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
VALUES=dict(BoardRearZ=9.0,BoardT=1.60005,BoardPocketT=2.15,Floor=1.4,FrontUnderZ=12.8,Face=1.4,
 OuterW=85.,OuterH=45.,OuterR=5.5,Wall=2.,RearRound=1.8,FrontRound=1.8,SeamGap=.1,
 BatteryW=50.,BatteryH=28.,BatteryT=3.,BatteryCx=-4.,BatteryCy=-3.9,BatteryFrameW=52.,BatteryFrameH=30.,
 SpeakerCx=30.4,SpeakerCy=-1.5,ChamberCx=30.4,ChamberCy=-2.65,ChamberW=13.2,ChamberH=20.1,ChamberWall=.8,ChamberWallTop=6.0,ChamberLidUnder=6.0,ChamberLidTop=6.8,AcousticSealT=0,SpeakerClipOpening=9.7,SpeakerClipT=.5,WindowW=29.72,WindowH=29.72,ScreenCx=.110,ScreenCy=.123,
 LCDClearW=32.72,LCDClearH=34.92,LCDPocketCeiling=13.3,LCDRailBottom=12.05,ButtonFaceZ=14.2,TFSlotW=14.2,TFSlotH=3.8,ButtonHole=6.6,
 InsertPilotD=2.8,InsertDepth=2.15,RearSeatT=1.1,SliderTravel=3.6,SliderLower=-.55,SliderUpper=3.05)
v=VALUES; BR=v['BoardRearZ']; PF=BR+v['BoardT']; TOP=v['FrontUnderZ']+v['Face']; FLOOR=v['Floor']
SEAM=BR+.8; FB=SEAM+v['SeamGap']; BOSSBOTTOM=BR+v['BoardPocketT']
old=App.openDocument(str(ROOT/'output/v03/myMicrobyte_enclosure_v03.FCStd'))
doc=App.newDocument('myMicrobyte_v08');doc.Label='myMicrobyte v0.8 / 两种前盖·玻璃避压·防脱拨帽·通气音腔'
p=doc.addObject('Spreadsheet::Sheet','Parameters');p.Label='尺寸记录 / 修改生成脚本 VALUES 后重建'
for i,(a,value) in enumerate(v.items(),1):p.set('A'+str(i),a);p.set('B'+str(i),str(value));p.setAlias('B'+str(i),a)
p.setColumnWidth('A',240)
construction=doc.addObject('App::DocumentObjectGroup','Construction');construction.Label='构造特征 / 原生布尔树'
refs=doc.addObject('App::DocumentObjectGroup','PCBReference');refs.Label='PCB、LCD 与选型占位'
keep=doc.addObject('App::DocumentObjectGroup','ConnectorKeepouts');keep.Label='检查包络（隐藏）'
hardware=doc.addObject('App::DocumentObjectGroup','Hardware_v08');hardware.Label='M2 螺丝与热熔螺母'
# No gasket or glue parts in v0.8.
def feat(n,s,label=None,group=construction):
 o=doc.addObject('Part::Feature',n);o.Shape=s;o.Label=label or n
 if group:group.addObject(o)
 return o
def shape(o):return o.Shape if hasattr(o,'Shape') else o
def fuse(n,objs):
 o=doc.addObject('Part::MultiFuse',n);o.Shapes=objs;o.Refine=True;construction.addObject(o);doc.recompute();return o
def cut(n,a,b):
 o=doc.addObject('Part::Cut',n);o.Base=a;o.Tool=b;o.Refine=True;construction.addObject(o);doc.recompute();return o
def box(n,w,h,d,x,y,z):
 o=doc.addObject('Part::Box',n);o.Length=w;o.Width=h;o.Height=d;o.Placement.Base=App.Vector(x,y,z);construction.addObject(o);doc.recompute();return o
def cyl(n,r,h,x,y,z):
 o=doc.addObject('Part::Cylinder',n);o.Radius=r;o.Height=h;o.Placement.Base=App.Vector(x,y,z);construction.addObject(o);doc.recompute();return o
def rr(w,h,r,z,d,cx=0,cy=0):
 s=Part.makeBox(w-2*r,h,d,App.Vector(cx-w/2+r,cy-h/2,z)).fuse(Part.makeBox(w,h-2*r,d,App.Vector(cx-w/2,cy-h/2+r,z)))
 for sx in [-1,1]:
  for sy in [-1,1]:s=s.fuse(Part.makeCylinder(r,d,App.Vector(cx+sx*(w/2-r),cy+sy*(h/2-r),z)))
 return s.removeSplitter()
def rounded(n,w,h,r,z,d,cx=0,cy=0):return feat(n,rr(w,h,r,z,d,cx,cy))
def edge_round(n,base,z,r):
 s=shape(base);edges=[e for e in s.Edges if abs(e.BoundBox.ZMin-z)<1e-6 and abs(e.BoundBox.ZMax-z)<1e-6]
 result=s.makeFillet(r,edges);assert result.isValid(),n
 return feat(n,result)
def capsule(w,l,z,h,cx,cy):
 s=Part.makeBox(w,l-w,h,App.Vector(cx-w/2,cy-(l-w)/2,z))
 return s.fuse(Part.makeCylinder(w/2,h,App.Vector(cx,cy-(l-w)/2,z))).fuse(Part.makeCylinder(w/2,h,App.Vector(cx,cy+(l-w)/2,z))).removeSplitter()
def xz_wire(cx,y,cz,w,h):
 ps=[App.Vector(cx-w/2,y,cz-h/2),App.Vector(cx+w/2,y,cz-h/2),App.Vector(cx+w/2,y,cz+h/2),App.Vector(cx-w/2,y,cz+h/2)]
 return Part.makePolygon(ps+[ps[0]])
def port(n,cx,cz,w,h,side):
 yi=side*19.6;ym=side*21.5;yo=side*23.3
 throat=Part.Face(xz_wire(cx,yi,cz,w,h)).extrude(App.Vector(0,ym-yi,0))
 lead=Part.makeLoft([xz_wire(cx,ym,cz,w,h),xz_wire(cx,yo,cz,w+3.6,h+3.6)],True,True)
 return feat(n,throat.fuse(lead).removeSplitter())
# Copy only retained reference solids, avoiding previous shell and keycap histories.
for src in old.PCBReference.Group:
 if src.Name in ['Battery_Assumed','Speaker_1510']:continue
 s=src.Shape.copy();s.translate(App.Vector(0,0,BR-13));feat(src.Name,s,src.Label,refs)
for src in old.ConnectorKeepouts.Group:
 if src.Name.startswith('Speaker_'):continue
 s=src.Shape.copy();s.translate(App.Vector(0,0,BR-13));feat(src.Name,s,src.Label,keep)
# User reports about 1 mm adhesive; glass itself is 1.9 mm thick.
doc.LCD_Assumed_5mm.Shape=Part.makeBox(31.52,33.72,1.9,App.Vector(-15.65,-18.287,PF+1.0))
doc.LCD_Assumed_5mm.Label='LCD 31.52×33.72×1.9 / 下方约1.0 mm胶层'
doc.LCD_ToleranceEnvelope.Shape=Part.makeBox(31.72,33.92,3.4,App.Vector(-15.75,-18.387,PF))
feat('LCD_AdhesiveEnvelope',Part.makeBox(30.5,32.7,1.0,App.Vector(.110-15.25,-1.427-16.35,PF)),'约1 mm胶层占位；实际涂胶形状未知',refs)
# Battery is a selection placeholder, not an already purchased pack.
battery=feat('Battery_Assumed',Part.makeBox(50,28,3,App.Vector(-29,-17.9,FLOOR+.3)),'3 mm 电池选型占位 / 50×28×3',refs)
batterymax=feat('Battery_ToleranceEnvelope',Part.makeBox(51,29,3.3,App.Vector(-29.5,-18.4,FLOOR+.3)),'成品电池检查包络 51×29×3.3',keep)
SX=v['SpeakerCx'];SY=v['SpeakerCy'];SZ=FLOOR+.4
speaker=feat('Speaker_1510',capsule(10,15,SZ,3.5,SX,SY),'1510 喇叭 / 15×10×3.5',refs)
spmax=feat('Speaker_ToleranceEnvelope',capsule(10.2,15.2,SZ,3.8,SX,SY),'喇叭尺寸最大包络 / 无胶层',keep)
tab=feat('Speaker_TabEnvelope',Part.makeBox(3,2.5,1,App.Vector(SX-1.5,SY-10,SZ)),'喇叭端部凸耳包络',keep)
# Rounded exterior blanks; the upper and lower perimeter rounds improve grip.
rearblank=rounded('RearBlank',85,45,5.5,0,SEAM)
rearouter=edge_round('RearGripRound',rearblank,0,v['RearRound'])
rearvoid=rounded('RearCavity',81,41,3.5,FLOOR,SEAM+2)
rearbase=cut('RearWallsAndFloor',rearouter,rearvoid)
# Four integrated 0.9 mm feet leave a desk air gap. Outer face needs support when printed feet-down.
feet=[]
for i,(fx,fy) in enumerate([(-32,-16),(-32,16),(32,-16),(32,16)]):
 ft=rr(6,4,1.8,-.9,1.05,fx,fy)
 es=[e for e in ft.Edges if abs(e.BoundBox.ZMin+.9)<1e-6 and abs(e.BoundBox.ZMax+.9)<1e-6]
 feet.append(feat('DeskFoot'+str(i),ft.makeFillet(.35,es)))
rearbase=fuse('RearWithDeskFeet',[rearbase]+feet)
frontblank=rounded('FrontBlank',85,45,5.5,FB,TOP-FB)
frontouter=edge_round('FrontGripRound',frontblank,TOP,v['FrontRound'])
frontvoid=rounded('FrontCavity',81,41,3.5,FB-.1,v['FrontUnderZ']-FB+.1)
frontbase=cut('FrontWallsAndFace',frontouter,frontvoid)
# 2.15 mm support pocket accommodates board thickness, warp and insert installation. Seam datum independent of board thickness.
holes=[(37.46,17.46),(37.46,-17.46),(-37.46,17.46),(-37.46,-17.46)]
rearposts=[cyl('RearPost'+str(i),3.4,BR-FLOOR,x,y,FLOOR) for i,(x,y) in enumerate(holes)]
frontposts=[cyl('FrontPost'+str(i),3.4,v['FrontUnderZ']-BOSSBOTTOM+.05,x,y,BOSSBOTTOM) for i,(x,y) in enumerate(holes)]
tongue=cut('Tongue',rounded('TongueOuter',82.4,42.4,4.2,SEAM-.05,1.2),rounded('TongueInner',81,41,3.5,SEAM-.1,1.4))
receiver=rounded('TongueReceiver',83.0,43.0,4.5,FB-.05,1.45)
frontbase=cut('FrontReceiver',frontbase,receiver)
tongue=cut('TongueBossClearance',tongue,fuse('TongueBossReliefs',[cyl('BossTongueRelief'+str(i),3.7,2,x,y,SEAM) for i,(x,y) in enumerate(holes)]))
rearbase=fuse('RearWithPostsAndTongue',[rearbase,tongue]+rearposts)
frontbase=fuse('FrontWithInsertBosses',[frontbase]+frontposts)
# Shallow rectangular adhesive frame, separate from both connector plug envelopes.
bframe=cut('BatteryFrame',box('BatteryFrameOuter',54.4,32.4,1.7,-31.2,-20.1,FLOOR-.1),box('BatteryFrameInner',52,30,2.2,-30,-18.9,FLOOR-.2))
bframe=cut('BatteryCableExit',bframe,box('BatteryCableRelief',8,5,2.5,16,9,FLOOR+.1))
# Continuous printed seat; bare speaker rim rests on it. No soft gasket.
spseat=feat('SpeakerContinuousSeat',capsule(10.8,16.6,FLOOR-.1,.5,SX,SY).cut(capsule(8,13,FLOOR-.2,.8,SX,SY)))
CX=v['ChamberCx'];CY=v['ChamberCy'];CW=v['ChamberW'];CH=v['ChamberH'];WT=v['ChamberWall']
chouter=rounded('ChamberOuterWall',CW,CH,1.8,FLOOR-.1,6.0-(FLOOR-.1),CX,CY)
chvoid=rounded('ChamberWallVoid',CW-2*WT,CH-2*WT,1.8-WT,FLOOR-.2,6.3-FLOOR,CX,CY)
chwall=cut('ChamberWallRing',chouter,chvoid)
leadslot=box('AcousticWireExit',3.2,2.4,1.8,CX-1.6,CY-CH/2-.2,4.5)
chwall=cut('ChamberWallWithWireExit',chwall,leadslot)
# Local .2 mm relief leaves .6 mm wall behind each moving spring.
springreliefs=fuse('SpeakerSpringWallReliefs',[box('SpeakerSpringWallReliefL',.25,3,4.25,SX-6.0,SY-1.5,1.95),box('SpeakerSpringWallReliefR',.25,3,4.25,SX+5.75,SY-1.5,1.95)])
chwall=cut('ChamberWallWithSpringRelief',chwall,springreliefs)
# Profiles extruded along Y: inclined cantilevers contact the rigid speaker sides.
def xz_prism(points,y,width):
 ps=[App.Vector(x,y,z) for x,z in points]
 return Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(App.Vector(0,width,0))
def yz_prism(points,x,width):
 ps=[App.Vector(x,y,z) for y,z in points]
 return Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(App.Vector(width,0,0))
spclips=[]
rightprofile=[(SX+5.25,1.55),(SX+5.75,1.55),(SX+5.35,5.4),(SX+5.35,5.8),(SX+5.20,5.8),(SX+4.85,5.4)]
for side in [-1,1]:
 pts=rightprofile if side==1 else [(2*SX-x,z) for x,z in reversed(rightprofile)]
 beam=xz_prism(pts,SY-.9,1.8)
 foot=Part.makeBox(.85,2.2,.6,App.Vector(SX+5.15 if side==1 else SX-6.0,SY-1.1,FLOOR-.1))
 spclips.append(feat('SpeakerSideSpring'+('R' if side==1 else 'L'),beam.fuse(foot).removeSplitter(),'喇叭侧壁弹片 / 仅接触硬边框'))
# Lid contacts the wall directly; underside keys locate it, not a gasket ring.
capplate=rounded('ChamberLidPlate',CW,CH-.4,1.6,6.0,.8,CX,CY)
caplocators=[box('ChamberLidLocator'+str(i),1.0,1.0,.95,x,CY-CH/2+1.7,5.1) for i,x in enumerate([CX-CW/2+1.5,CX+CW/2-2.5])]
lidblank=fuse('ChamberLidBlank',[capplate]+caplocators)
vent=rounded('LidLargeVent',9.0,14.4,.65,4.9,2.3,CX,CY)
wirelid=box('LidCableRelief',3.2,2.2,2.0,CX-1.6,CY-CH/2-.2,5.0)
lid=cut('AcousticLid_v08',lidblank,fuse('LidVentAndCable',[vent,wirelid]));lid.Label='通气音腔盖 / 大开窗·免胶挂扣'
construction.removeObject(lid)
# North fixed hook sits left of the battery connector. The opposite two latches
# flex toward -Y. Hook engagement is .15 mm; about .25 mm deflection clears it.
fixedhook=fuse('ChamberFixedHook',[box('HookBackRiser',3,.9,1.75,26.0,7.3,5.8),box('HookTopLip',3,1.6,.6,26.0,6.6,6.95)])
frontlatches=[]
for i,x in enumerate([26.8,32.0]):
 foot=box('LidLatchFoot'+str(i),2.2,1.4,.7,x,-13.7,1.3)
 stem=box('LidLatchStem'+str(i),2.2,.6,5.55,x,-13.7,1.45)
 ramp=feat('LidLatchHook'+str(i),yz_prism([(-13.7,6.95),(-12.35,6.95),(-13.1,7.55),(-13.7,7.55)],x,2.2))
 frontlatches.append(fuse('LidLatch'+str(i),[foot,stem,ramp]))
rearbase=fuse('RearWithFramesAndChamber',[rearbase,bframe,spseat,chwall,fixedhook]+frontlatches)
# Grille retains 1 mm webs and stays inside the unobstructed front plenum.
grilles=[]
for i,dy in enumerate([-4.4,-2.2,0,2.2,4.4]):
 g=Part.makeBox(7.6,1.3,FLOOR+.3,App.Vector(SX-3.8+(.2 if i%2 else -.2),SY+dy-.65,-.1)).common(capsule(8,13,-.15,FLOOR+.5,SX,SY))
 grilles.append(feat('SpeakerGrille'+str(i),g))
# Full glass opening: only lateral guides, with no lip above the bonded glass.
lcx=.110;lcy=-1.427;rz=12.05
lcdpocket=rounded('LCDGlassThroughClearance',v['LCDClearW'],v['LCDClearH'],.20,FB-.2,8,lcx,lcy)
frontbase=cut('FrontLCDClearance',frontbase,lcdpocket)
rails=[];hw=v['LCDClearW']/2;hh=v['LCDClearH']/2
for ix in [-1,1]:
 for iy in [-1,1]:
  xx=lcx+ix*hw;yy=lcy+iy*hh
  rails.append(box('LCDRailX',6,1,v['FrontUnderZ']-rz+.08,xx-5 if ix>0 else xx-1,yy if iy>0 else yy-1,rz))
  rails.append(box('LCDRailY',1,5,v['FrontUnderZ']-rz+.08,xx if ix>0 else xx-1,yy-5 if iy>0 else yy,rz))
frontbase=fuse('FrontWithSideOnlyLCDLocator',[frontbase]+rails)
# A front-cover brow masks the PCB edge behind the TF connector. Clearance below
# it is deliberately retained for the card: do not make the lip touch the board plane.
tflip=box('TFFrontBrow',16.4,2.15,3.8,4.8511-8.2,20.35,9.25)
frontbase=fuse('FrontWithTFBrow',[frontbase,tflip])
# Openings and four machine screw paths.
rearcut=[box('TFBrowRearClearance',17.0,3.2,2.0,4.8511-8.5,20.05,8.95),box('BatteryPlugPostRelief',6.6,3.6,6.1,32.128,12.152,BR-5.8)];frontcut=[];inserts=[];screws=[]
for i,(x,y) in enumerate(holes):
 rearcut += [cyl('RearScrewThrough'+str(i),1.15,BR+2,x,y,-.1),cyl('RearDeepHeadBore'+str(i),2.3,BR-v['RearSeatT']+.1,x,y,-.1)]
 frontcut += [cyl('InsertPilot'+str(i),1.4,v['InsertDepth']+.02,x,y,BOSSBOTTOM-.01),cyl('ScrewTipRelief'+str(i),1.15,v['InsertDepth'],x,y,BOSSBOTTOM-.01),feat('InsertLeadIn'+str(i),Part.makeCone(1.55,1.4,.3,App.Vector(x,y,BOSSBOTTOM-.01)))]
 inserts.append(feat('Hardware_Insert'+str(i+1),Part.makeCylinder(1.5,2,App.Vector(x,y,BOSSBOTTOM)).cut(Part.makeCylinder(.8,2.2,App.Vector(x,y,BOSSBOTTOM-.1))),'M2×2×3 热熔螺母',hardware))
 seat=BR-v['RearSeatT'];screws.append(feat('Hardware_Screw'+str(i+1),Part.makeCylinder(1,5,App.Vector(x,y,seat)).fuse(Part.makeCylinder(2,.8,App.Vector(x,y,seat-.8))),'M2×5 螺丝',hardware))
usb=port('USBThroatAndChamfer',-.00165,BR-1.8,10.4,4.6,-1)
tf=port('TFThroatAndChamfer',4.8511,BR-.8,v['TFSlotW'],v['TFSlotH'],1)
rearcut += [usb,tf];frontcut += [usb]
# Chamfer the brow's upper card edge by 0.35 mm; the remaining PCB edge is masked.
tfbrowbevel=feat('TFBrowEntryBevel',Part.makeLoft([xz_wire(4.8511,21.65,7.55,14.2,3.4),xz_wire(4.8511,22.65,7.55,15.6,4.1)],True,True))
frontcut.append(tfbrowbevel)
# Window follows the glass outline, including its inactive black border.
window=rounded('LCDWindow',32.72,34.92,.20,PF-.1,9,.110,-1.427)
def xywire(cx,cy,z,w,h):
 ps=[App.Vector(cx-w/2,cy-h/2,z),App.Vector(cx+w/2,cy-h/2,z),App.Vector(cx+w/2,cy+h/2,z),App.Vector(cx-w/2,cy+h/2,z)]
 return Part.makePolygon(ps+[ps[0]])
winlead=feat('LCDWindowBevel',Part.makeLoft([xywire(.110,-1.427,TOP-.35,32.72,34.92),xywire(.110,-1.427,TOP+.05,33.52,35.72)],True,True))
frontcut += [window,winlead]
buttons={'UP':(-28.707,6.543),'DOWN':(-28.707,-4.760),'LEFT':(-34.168,.955),'RIGHT':(-23.119,.828),'START':(23.998,-15.174),'SELECT':(-23.246,-15.174),'MENU':(23.998,14.798),'A':(34.285,.955),'B':(25.903,-2.728)}
# Narrow 6.6 mm throats (A is 6.8 mm for the source's rotated 6.23 mm body).
# Small cosmetic lead-in only; the whole button field remains a continuous flat skin.
for n,(x,y) in buttons.items():
 w=6.8 if n=='A' else v['ButtonHole']
 frontcut.append(rounded('SwitchThrough_'+n,w,w,.35,PF-.2,7,x,y))
# The diagonal D-pad positions overlap. Remove the unsupported centre, keeping a
# connected opening instead of adding an unattached fragile island.
frontcut.append(rounded('DpadCentreOpening',5.7,5.7,.4,PF-.2,7,-28.707,.89))
# Rear charge indicator only. Front RUN hole removed after confirmed poor transmission.
rearcut.append(cyl('ChargeLEDLightHole',1.,BR+.3,38.476,2.225,-.1))
rearcut += grilles
# Slider installs vertically from the OPEN rear split face, after PCB placement.
# The socket is through-Z and clears the PCB edge; front cover becomes the retainer.
cz=BR-1.15;cy=-6.3186;mid=cy+(v['SliderLower']+v['SliderUpper'])/2
flange=box('SliderInnerFlange',1.3,10.4,4.0,40.2,cy-5.2,cz-2.2)
neck=box('SliderNeck',1.8,3.2,2.2,41.4,cy-1.6,cz-1.1)
thumbshape=Part.makeBox(1.5,6.8,3.4,App.Vector(43.0,cy-3.4,cz-1.7))
thumb=feat('SliderRoundedThumb',thumbshape.makeFillet(.35,thumbshape.Edges))
grips=[]
for dy in [-2.4,-1.2,0,1.2,2.4]:
 gs=Part.makeBox(.65,.60,2.6,App.Vector(44.30,cy+dy-.3,cz-1.3))
 grips.append(feat('SliderGripRib',gs.makeFillet(.18,gs.Edges)))
socket=box('SliderOpenSocket',1.55,1.65,6,40.05,cy-.825,cz-2.8)
slider=cut('PowerSlider_v08',fuse('SliderWithGrip',[flange,neck,thumb]+grips),socket)
slider.Label='电源拨帽 v0.8 / 顶部装入·3.6 mm机械行程·指纹朝上打印'
construction.removeObject(slider)
tracks=fuse('SliderOpenTracks',[box('SliderInnerOpenTrack',1.70,14.4,8,40.05,mid-7.2,cz-2.35),box('SliderOuterOpenTrack',5,7.2,7,41.70,mid-3.6,cz-1.25)])
rearcut.append(tracks)
# Only remove the tongue/receiver return below the retaining face; keep the front
# side wall intact above Z9.85 as the upper slide stop.
frontcut.append(box('SliderFrontReturnClearance',2.25,15.0,1.0,40.05,mid-7.5,8.85))
# Two long, narrow flexible keeper tabs retain at least one flange end throughout travel.
sliderclips=[]
for i,yc in enumerate([mid-4.9,mid+4.9]):
 rearcut.append(box('SliderKeeperRelief'+str(i),1.1,1.7,6.3,41.55,yc-.85,4.4))
 stem=Part.makeBox(.6,1.1,5.65,App.Vector(41.8,yc-.55,4.25))
 ramp=xz_prism([(41.3,9.80),(42.4,9.80),(42.4,10.45),(41.8,10.45),(41.3,10.0)],yc-.55,1.1)
 sliderclips.append(feat('SliderKeeper'+str(i),stem.fuse(ramp).removeSplitter(),'拨帽防脱弹片 / 装入时轻向外让位'))
 frontcut.append(box('FrontKeeperPocket'+str(i),2.4,2.0,1.4,40.9,yc-1,9.65))
# Recess around grille leads toward the rounded right edge; feet provide the main desk gap.
rearcut.append(rounded('OuterSoundRelief',14.0,16.5,1.4,-.2,.65,SX,SY))
rearcut.append(box('OuterSoundEdgeChannel',14.0,10.0,.65,SX,-6.5,-.2))
rearcutters=fuse('RearCutters',rearcut)
rearrigid=cut('RearRigidWithoutSpeakerSprings',rearbase,rearcutters)
rear=fuse('RearShell_v08',[rearrigid]+spclips+sliderclips);rear.Label='后盖 v0.8 / 无胶音腔·侧弹片·卡扣·52×30电池框'
front=cut('FrontShellFlat_v08',frontbase,fuse('FrontCutters',frontcut));front.Label='B 平面前盖 / 屏幕框与按键区同高'
# A raised, rounded protective bezel. Its opening stays outside the entire glass.
ringouter=rounded('RaisedBezelOuter',37.0,39.2,1.8,TOP-.05,1.25,.110,-1.427)
ringouter=edge_round('RaisedBezelTopRound',ringouter,TOP+1.2,.45)
ringhole=rounded('RaisedBezelGlassClearance',32.72,34.92,.2,TOP-.1,1.5,.110,-1.427)
ring=cut('RaisedBezelRing',ringouter,ringhole)
raised=fuse('FrontShellRaised_v08',[front,ring]);raised.Label='A 凸框前盖 / 屏幕框高于按键区1.2 mm'
construction.removeObject(raised)
construction.removeObject(rear);construction.removeObject(front)
doc.recompute()
printables=[rear,front,raised,slider,lid]

report={'revision':'0.8','units':'mm','parts':[],'collisions':[],'front_options':{'A_raised':{'button_surface_z':TOP,'bezel_surface_z':TOP+1.2,'glass_top_z':PF+2.9,'switch_top_z_nominal':PF+5},'B_flat':{'button_surface_z':TOP,'bezel_surface_z':TOP,'glass_top_z':PF+2.9,'switch_top_z_nominal':PF+5}},'button_holes_mm':{'regular':6.6,'A_rotated':6.8,'dpad_centre':5.7},'glass_opening_mm':[32.72,34.92],'adhesive_assumed_mm':1.0,'glass_total_checked_height_above_pcb_mm':3.4,'desk_gap_mm':.9,'slider_inner_flange_length_mm':10.4,'slider_inner_flange_old_mm':6.8,'slider_socket_width_mm':1.65,'slider_motion_mm':[-.55,3.05],'acoustic_lid':'large open window, optional removable frame','printing':'review only; do not send until user approves this revision'}
def collision(a,b,tag='fit'):
 sa=shape(a);sb=shape(b)
 if not sa.BoundBox.intersect(sb.BoundBox):return
 vol=sa.common(sb).Volume
 if vol>.001:report['collisions'].append({'a':a.Name if hasattr(a,'Name') else 'swept','b':b.Name if hasattr(b,'Name') else 'shape','tag':tag,'volume_mm3':vol})
for o in printables:
 report['parts'].append({'name':o.Name,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'volume_mm3':o.Shape.Volume})
allrefs=list(refs.Group)+list(keep.Group)
for sh in [rear,front,raised,lid]:
 for r in allrefs:
  collision(rearrigid if sh==rear and r.Name in ['Speaker_1510','Speaker_ToleranceEnvelope'] else sh,r)
for ff in [front,raised]:
 collision(ff,rear);collision(ff,lid);collision(ff,slider)
collision(lid,rear);collision(lid,slider)
for r in allrefs:collision(slider,r,'slider rest')
# Exact slider at sampled travel poses. White switch actuator is a moving part and excluded;
# the fixed metal switch case is checked independently.
switchbody=doc.Ref_SW3.Shape.common(Part.makeBox(10,14,5,App.Vector(29.5,-12,6)))
for iy in range(37):
 delta=-.55+iy*.1;ss=slider.Shape.copy();ss.translate(App.Vector(0,delta,0))
 for r in [rear,front,raised,lid]+[r for r in allrefs if r.Name!='Ref_SW3']:
  collision(ss,r,'slider travel '+str(round(delta,2)))
 collision(ss,feat('SwitchBodyCheck',switchbody),'slider vs fixed switch') if iy==0 else None
# Glass and switches displaced laterally, board/adhesive thickness grown. This cannot
# simulate shell deflection, so physical black-screen pressure test remains necessary.
report['glass_clearances_mm']={}
for ff in [front,raised]:
 gaps=[]
 for dx,dy in [(0,0),(.2,.2),(.2,-.2),(-.2,.2),(-.2,-.2)]:
  sh=doc.LCD_ToleranceEnvelope.Shape.copy();sh.translate(App.Vector(dx,dy,.2))
  collision(sh,ff,'LCD tolerance');gaps.append(sh.distToShape(ff.Shape)[0])
 report['glass_clearances_mm'][ff.Name]=min(gaps)
 for n in buttons:
  sh=doc.getObject('Ref_'+n).Shape.copy();sh.translate(App.Vector(0,0,.4));collision(sh,ff,'switch elevated solder')
# Card approach and actual source board fit retained.
tfapproach=Part.makeBox(11.4,11,1.4,App.Vector(4.8511-5.7,19.9,BR-1.5))
for sh in [rear,front,raised]:collision(tfapproach,sh,'TF insertion path')
report['grille_open_area_mm2']=sum(g.Shape.Volume/(FLOOR+.3) for g in grilles)
report['lid_open_area_mm2']=vent.Shape.Volume/2.3
report['assumptions']=['Glass 1.9 mm plus approximately 1.0 mm adhesive. User confirms ripples disappear with front removed. Full glass aperture removes vertical pressing lip; side clearance remains.','No quantified acoustic gain is claimed. Large vent relieves the small rear cavity; removable frame enables same-volume comparison.','Feet add 0.9 mm beyond back plane. Raised front and rear feet require a reviewed support/orientation strategy before printing.','Slider keeper tabs are geometric designs, not validated fatigue/force models. Nominal 0.3 mm outward flex during insertion; no glue.','6.6 mm holes use 6.0 mm switch assumption. Source A is rotated, so it uses 6.8 mm; actual tolerance needs trial.']
(REPORT/'fit_check_v08.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
doc.saveAs(str(OUT/'myMicrobyte_enclosure_v08.FCStd'))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
assert all(x['valid'] and x['solids']==1 for x in report['parts']),'invalid solids'
assert not report['collisions'],'collision check failed'
for ff,tag in [(front,'B_flat'),(raised,'A_raised')]:Part.export([rear,ff,slider,lid],str(OUT/('myMicrobyte_v08_'+tag+'.step')))
for o,name in [(rear,'RearShell'),(front,'FrontShell_B_flat'),(raised,'FrontShell_A_raised'),(slider,'PowerSlider'),(lid,'AcousticLid')]:
 sh=o.Shape.copy()
 if o in [front,raised,lid]:sh.rotate(App.Vector(),App.Vector(1,0,0),180)
 elif o==slider:sh.rotate(App.Vector(),App.Vector(0,1,0),-90)
 b=sh.BoundBox;sh.translate(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
 m=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.035,AngularDeflection=.1,Relative=False)
 assert m.isSolid(),name
 b=m.BoundBox;m.translate(-b.XMin,-b.YMin,-b.ZMin);m.write(str(OUT/(name+'_print.stl')))
print('v0.8 exports complete',flush=True)
