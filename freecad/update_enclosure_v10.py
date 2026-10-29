"""FreeCAD v0.10: GBA-inspired captive flange slider and integral shell guide.
Regenerate with FreeCAD's bundled Python. Millimetres; source PCB XY preserved.
Parameters are documented in the native sheet; edit VALUES here and regenerate.
"""
from pathlib import Path
import sys, json
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, MeshPart
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/v10'; REPORT=ROOT/'reports/v10'
OUT.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
VALUES=dict(BoardRearZ=9.0,BoardT=1.60005,BoardPocketT=2.15,Floor=1.4,FrontUnderZ=12.8,Face=1.4,
 OuterW=85.,OuterH=45.,OuterR=5.5,Wall=2.,RearRound=1.8,FrontRound=1.8,SeamGap=.1,
 BatteryW=50.,BatteryH=28.,BatteryT=3.,BatteryCx=-4.,BatteryCy=-3.9,BatteryFrameW=52.,BatteryFrameH=30.,
 SpeakerCx=30.4,SpeakerCy=-1.5,ChamberCx=30.4,ChamberCy=-2.65,ChamberW=13.2,ChamberH=20.1,ChamberWall=.8,ChamberWallTop=6.0,ChamberLidUnder=6.0,ChamberLidTop=6.8,AcousticSealT=0,SpeakerClipOpening=9.7,SpeakerClipT=.5,WindowW=29.72,WindowH=29.72,ScreenCx=.110,ScreenCy=.123,
 LCDClearW=32.52,LCDClearH=34.72,LCDPocketCeiling=14.55,LCDRailBottom=12.05,ButtonFaceZ=14.2,TFSlotW=14.2,TFSlotH=3.8,ButtonHole=6.6,
 InsertPilotD=2.8,InsertDepth=2.15,RearSeatT=1.1,SliderTravel=3.6,SliderLower=-.55,SliderUpper=3.05)
v=VALUES; BR=v['BoardRearZ']; PF=BR+v['BoardT']; TOP=v['FrontUnderZ']+v['Face']; FLOOR=v['Floor']
SEAM=BR+.8; FB=SEAM+v['SeamGap']; BOSSBOTTOM=BR+v['BoardPocketT']
old=App.openDocument(str(ROOT/'output/v03/myMicrobyte_enclosure_v03.FCStd'))
doc=App.newDocument('myMicrobyte_v10');doc.Label='myMicrobyte v0.10 / 凸框小窗口·整圈限位·GBA式整体导轨拨帽·胶贴椭圆喇叭座'
p=doc.addObject('Spreadsheet::Sheet','Parameters');p.Label='尺寸记录 / 修改生成脚本 VALUES 后重建'
for i,(a,value) in enumerate(v.items(),1):p.set('A'+str(i),a);p.set('B'+str(i),str(value));p.setAlias('B'+str(i),a)
p.setColumnWidth('A',240)
construction=doc.addObject('App::DocumentObjectGroup','Construction');construction.Label='构造特征 / 原生布尔树'
refs=doc.addObject('App::DocumentObjectGroup','PCBReference');refs.Label='PCB、LCD 与选型占位'
keep=doc.addObject('App::DocumentObjectGroup','ConnectorKeepouts');keep.Label='检查包络（隐藏）'
hardware=doc.addObject('App::DocumentObjectGroup','Hardware_v10');hardware.Label='M2 螺丝与热熔螺母'
# Speaker supplied adhesive is a reference envelope, not a printable part.
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
SX=v['SpeakerCx'];SY=v['SpeakerCy'];SZ=FLOOR+.4+.2
speaker=feat('Speaker_1510',capsule(10,15,SZ,3.5,SX,SY),'1510 喇叭 / 15×10×3.5·自带胶暂按0.2 mm',refs)
spmax=feat('Speaker_ToleranceEnvelope',capsule(10.2,15.2,SZ,4.0,SX,SY),'喇叭最大包络 / 含胶厚增加0.2 mm',keep)
tab=feat('Speaker_TabEnvelope',Part.makeBox(3,2.5,1,App.Vector(SX-1.5,SY-10,SZ)),'喇叭端部凸耳包络',keep)
# Rounded exterior blanks; the upper and lower perimeter rounds improve grip.
rearblank=rounded('RearBlank',85,45,5.5,0,SEAM)
rearouter=edge_round('RearGripRound',rearblank,0,v['RearRound'])
rearvoid=rounded('RearCavity',81,41,3.5,FLOOR,SEAM+2)
rearbase=cut('RearWallsAndFloor',rearouter,rearvoid)
# Restore the smooth rear exterior: no feet and no recessed sound channel.
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
# The speaker's own annular adhesive rests on the uninterrupted hard seat.
spseat=feat('SpeakerContinuousSeat',capsule(10.8,16.6,FLOOR-.1,.5,SX,SY).cut(capsule(8,13,FLOOR-.2,.8,SX,SY)))
adhesive=feat('Speaker_Adhesive',capsule(10,15,1.8,.2,SX,SY).cut(capsule(8,13,1.75,.35,SX,SY)),'喇叭自带环形双面胶 / 暂按0.2 mm',refs)
# A low oval perimeter locates the hard speaker case; it does not clamp the driver.
oval=feat('SpeakerOvalLocator',capsule(12.4,17.4,FLOOR-.1,2.9,SX,SY).cut(capsule(10.6,15.6,FLOOR-.2,3.2,SX,SY)))
notches=fuse('SpeakerTerminalAndWireNotches',[box('SpeakerTerminalNotch',3.6,4.2,3.5,SX-1.8,SY-10.5,1.75),box('SpeakerWireNotch',3.2,3.3,2.0,SX-1.6,SY+6.5,2.5)])
oval=cut('SpeakerOvalWithLeadReliefs',oval,notches)
CX=v['ChamberCx'];CY=v['ChamberCy'];CW=v['ChamberW'];CH=v['ChamberH'];WT=v['ChamberWall']
chouter=rounded('ChamberOuterWall',CW,CH,1.8,FLOOR-.1,6.0-(FLOOR-.1),CX,CY)
chvoid=rounded('ChamberWallVoid',CW-2*WT,CH-2*WT,1.8-WT,FLOOR-.2,6.3-FLOOR,CX,CY)
chwall=cut('ChamberWallRing',chouter,chvoid)
leadslot=box('AcousticWireExit',3.6,2.4,3.7,CX-1.8,CY-CH/2-.2,2.5)
chwall=cut('ChamberWallWithWireExit',chwall,leadslot)
rearbase=fuse('RearWithFramesAndOpenChamber',[rearbase,bframe,spseat,oval,chwall])
# No speaker side springs, detachable lid, fixed hook or lid latches in this revision.
def xz_prism(points,y,width):
 ps=[App.Vector(x,y,z) for x,z in points]
 return Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(App.Vector(0,width,0))
# Grille retains 1 mm webs and stays inside the unobstructed front plenum.
grilles=[]
for i,dy in enumerate([-4.4,-2.2,0,2.2,4.4]):
 g=Part.makeBox(7.6,1.3,FLOOR+.3,App.Vector(SX-3.8+(.2 if i%2 else -.2),SY+dy-.65,-.1)).common(capsule(8,13,-.15,FLOOR+.5,SX,SY))
 grilles.append(feat('SpeakerGrille'+str(i),g))
# Four-sided locating frame around the whole glass. It locates, never clamps.
lcx=.110;lcy=-1.427;rz=12.05
lcdpocket=rounded('LCDGlassPocket',v['LCDClearW'],v['LCDClearH'],.20,FB-.2,v['LCDPocketCeiling']-(FB-.2),lcx,lcy)
frontbase=cut('FrontLCDClearance',frontbase,lcdpocket)
locator=rounded('LCDLocatorOuter',v['LCDClearW']+2.4,v['LCDClearH']+2.4,1.4,rz,v['LCDPocketCeiling']-rz+.03,lcx,lcy)
locator=cut('LCDFullPerimeterLocator',locator,rounded('LCDLocatorInner',v['LCDClearW'],v['LCDClearH'],.20,rz-.1,3.0,lcx,lcy))
# Shallow relief at the lower edge for the display flex. Frame remains connected above it.
locator=cut('LCDLocatorFlexRelief',locator,box('LCDFlexExit',12,3.0,.65,lcx-6,lcy-v['LCDClearH']/2-1.5,rz-.05))
frontbase=fuse('FrontWithPerimeterLCDLocator',[frontbase,locator])
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
window=rounded('LCDWindow',29.72,29.72,.20,PF-.1,9,.110,.123)
def xywire(cx,cy,z,w,h):
 ps=[App.Vector(cx-w/2,cy-h/2,z),App.Vector(cx+w/2,cy-h/2,z),App.Vector(cx+w/2,cy+h/2,z),App.Vector(cx-w/2,cy+h/2,z)]
 return Part.makePolygon(ps+[ps[0]])
winlead=feat('LCDWindowBevel',Part.makeLoft([xywire(.110,.123,15.15,29.72,29.72),xywire(.110,.123,15.45,30.32,30.32)],True,True))
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
# GBA-inspired one-piece flange/fork. The rear is an open loading cradle;
# the FRONT has an integral roof. No separate keeper or elastic latch is needed.
cz=BR-1.15;cy=-6.3186;mid=cy+(v['SliderLower']+v['SliderUpper'])/2
# Local side collar adds only 0.55 mm to the shell, retaining >=1.0 mm outer
# wall beside the guide instead of thinning the existing 2 mm wall to 0.45 mm.
collar=rr(20.0,7.35,1.0,0,2.65)
# rr XY -> YZ; local Z extrusion becomes X. Then locate in switch region.
collar.rotate(App.Vector(),App.Vector(1,1,1),120)
collar.translate(App.Vector(40.4,mid,7.975))
rearadd=feat('RearGuideCollar',collar.common(Part.makeBox(8,24,9.8,App.Vector(39,mid-12,0))))
frontadd=feat('FrontGuideCollar',collar.common(Part.makeBox(8,24,5,App.Vector(39,mid-12,9.9))))
innerguide=box('RearLowerInnerGuide',1.6,19.6,2.65,39.0,mid-9.8,4.4)
rearbase=fuse('RearWithRigidGuideCollar',[rearbase,rearadd,innerguide])
frontbase=fuse('FrontWithGuideCollar',[frontbase,frontadd])
flangeshape=Part.makeBox(1.6,14.0,4.2,App.Vector(40.25,cy-7,5.55))
flange=feat('SliderWideFlange',flangeshape.makeFillet(.15,flangeshape.Edges))
neck=box('SliderThickNeck',1.85,4.2,3.0,41.65,cy-2.1,6.35)
thumbshape=Part.makeBox(1.7,7.8,3.8,App.Vector(43.2,cy-3.9,cz-1.9))
thumb=feat('SliderRoundedThumb',thumbshape.makeFillet(.40,thumbshape.Edges))
grips=[]
for dy in [-2.8,-1.4,0,1.4,2.8]:
 gs=Part.makeBox(.65,.65,2.8,App.Vector(44.70,cy+dy-.325,cz-1.4))
 grips.append(feat('SliderGripRib',gs.makeFillet(.20,gs.Edges)))
# Through-Z fork avoids stressing the soldered switch during top-down assembly.
# Behind the fork a 1.60 mm solid root remains through the 3 mm-high neck.
socket=box('SliderOpenFork',1.85,1.8,6,40.05,cy-.9,4.9)
slider=cut('PowerSlider_v10',fuse('SliderWithGrip',[flange,neck,thumb]+grips),socket)
slider.Label='GBA式拨帽 / 14 mm宽挡边·1.6 mm叉根·1.8 mm叉口·纹路朝上打印'
construction.removeObject(slider)
tracks=fuse('SliderOpenTracks',[
 box('SliderInnerOpenTrack',2.0,18.0,8,40.05,mid-9.0,5.35),
 box('SliderOuterOpenTrack',6,7.8,8,42.05,mid-3.9,6.15)])
rearcut.append(tracks)
rearcut.append(box('RearTongueUnderFrontCollarRelief',3.2,20.4,1.8,40.25,mid-10.2,9.8))
# Integral roof descends with the front and leaves 0.20 mm nominal top play.
# The side collar and existing front wall support its entire length.
roof=box('FrontIntegralSliderRoof',2.70,18.6,1.70,40.35,mid-9.3,9.95)
frontbase=fuse('FrontWithIntegralSliderRoof',[frontbase,roof])
frontcut.append(box('FrontSliderBelowRoofClearance',6,18.2,1.20,40.05,mid-9.1,8.75))
rear=cut('RearShell_v10',rearbase,fuse('RearCutters',rearcut));rear.Label='后盖 v0.10 / 平整背面·椭圆胶贴喇叭座·敞口滑槽·整体加厚导轨'
front=cut('FrontShellFlat_v10',frontbase,fuse('FrontCutters',frontcut));front.Label='前盖下部构造 / 不单独打印'
# Keep the preferred F3 outside profile while covering the inactive glass border.
ringouter=rounded('RaisedBezelOuter',37.0,39.2,1.8,TOP-.05,1.25,.110,-1.427)
ringouter=edge_round('RaisedBezelTopRound',ringouter,TOP+1.2,.45)
ring=cut('RaisedBezelUndersideGlassRelief',ringouter,lcdpocket)
ring=cut('RaisedBezelDisplayAperture',ring,fuse('RaisedBezelWindowCutters',[window,winlead]))
raised=fuse('FrontShell_v10',[front,ring]);raised.Label='前盖 v0.10 / F3凸框与按键孔·小显示窗·整圈玻璃限位'
construction.removeObject(raised);construction.removeObject(rear)
# Flat construction remains hidden; only the completed raised front is printable.
doc.recompute()

printables=[raised,rear,slider]
report={'revision':'0.10','units':'mm','status':'review only, no print authorization for this revision','parts':[],'collisions':[],
 'front':{'basis':'F3 from v08 trials','button_holes_mm':[6.6,6.8],'button_surface_z':14.2,'bezel_top_z':15.4,'button_exposure_nominal_mm':1.4,'display_window_mm':[29.72,29.72],'active_display_mm':[27.72,27.72],'glass_mm':[31.52,33.72,1.9],'adhesive_nominal_mm':1.0,'locator_inner_mm':[32.52,34.72],'locator_side_gap_nominal_mm':.5,'glass_top_z':PF+2.9,'over_glass_ceiling_z':14.55,'nominal_glass_roof_gap_mm':14.55-(PF+2.9),'flex_relief_mm':[12,3,.65],'print_orientation':'outside/front face UP'},
 'slider':{'retention':'GBA-inspired wide flange between rear cradle and integral front roof','flange_mm':[1.6,14,4.2],'neck_mm':[1.85,4.2,3.0],'fork_root_mm':1.6,'fork_width_mm':1.8,'roof_thickness_mm':1.7,'guide_side_clearance_per_side_mm':.2,'top_bottom_clearance_per_side_mm':.2,'local_outer_wall_min_mm':1.0,'inner_guide_top_z':7.05,'inner_guide_to_switch_body_gap_mm':.2587,'travel_mm':[-.55,3.05],'printed_parts_count':3},
 'speaker':{'attachment':'speaker supplied annular double-sided adhesive','adhesive_assumed_mm':.2,'oval_inner_mm':[10.6,15.6],'oval_top_z':4.2,'outer_rect_top_z':6,'open_back':True,'no_lid_no_latches_no_side_springs':True},
 'rear':{'smooth_exterior':True,'feet_removed':True,'outer_sound_relief_removed':True,'battery_frame_mm':[52,30],'recommended_pack_max_mm':[51,29,3.3]},
 'limitations':['Geometry does not prove no pressure under finger/screw loads. Glass clearance is based on 1 mm adhesive; physical pressure test still needed.','A four-sided locator limits lateral drift but must not clamp the glass. Existing adhesive holds the display to PCB.','The rectangular surrounding wall is open at the back, not a sealed/tuned chamber. Oval seat and adhesive separate the front outlet from rear leakage; gain is unmeasured.','Restoring the smooth rear sacrifices the 0.9 mm desk gap: a flat table may block the rear grille again.','Slider should be installed with rear flat on the desk; it becomes positively captive only after front closure. The front roof is integral. No clip flex is required.','Existing flex cable is not fully modeled; lower frame relief requires physical routing check.']}
def collision(a,b,tag):
 sa=shape(a);sb=shape(b)
 if not sa.BoundBox.intersect(sb.BoundBox):return
 vol=sa.common(sb).Volume
 if vol>.001:report['collisions'].append({'tag':tag,'volume_mm3':round(vol,7)})
for o in printables:
 report['parts'].append({'name':o.Name,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'volume_mm3':o.Shape.Volume})
allrefs=list(refs.Group)+list(keep.Group)
for sh in printables:
 for r in allrefs:collision(sh,r,sh.Name+'/'+r.Name)
for i,a in enumerate(printables):
 for b in printables[i+1:]:collision(a,b,a.Name+'/'+b.Name)
# Full tolerance envelope including lateral assembly offset and adhesive/PCB stack increase.
gaps=[]
for dx,dy in [(0,0),(.2,.2),(.2,-.2),(-.2,.2),(-.2,-.2)]:
 sh=doc.LCD_ToleranceEnvelope.Shape.copy();sh.translate(App.Vector(dx,dy,.2))
 collision(sh,raised,'LCD enlarged/shifted tolerance');gaps.append(sh.distToShape(raised.Shape)[0])
report['front']['worst_checked_glass_gap_mm']=min(gaps)
report['front']['nominal_glass_min_distance_mm']=doc.LCD_Assumed_5mm.Shape.distToShape(raised.Shape)[0]
for n in buttons:
 sh=doc.getObject('Ref_'+n).Shape.copy();sh.translate(App.Vector(0,0,.4));collision(sh,raised,'Elevated solder '+n)
# Slider geometry, working travel and assembly paths. Switch end stops are
# electrical-component properties; the 3.6 mm shell travel is a design allowance.
switchbody=doc.Ref_SW3.Shape.common(Part.makeBox(10,14,5,App.Vector(29.5,-12,6)))
actuator=doc.Ref_SW3.Shape.common(Part.makeBox(4,4,3,App.Vector(39.5,cy-2,6.5)))
staticrefs=[r for r in allrefs if r.Name!='Ref_SW3']
retention=[];lateral_retention=[];down_retention=[];endstops=[]
for k in range(37):
 dy=-.55+.1*k;sh=slider.Shape.copy();sh.translate(App.Vector(0,dy,0))
 for r in [rear,raised]+staticrefs:collision(sh,r,'slider motion '+str(round(dy,2))+'/'+r.Name)
 collision(sh,switchbody,'slider vs fixed switch')
 act=actuator.copy();act.translate(App.Vector(0,dy,0));collision(sh,act,'slider vs moving actuator')
 for dx in [-.15,0,.15]:
  for dz in [-.15,0,.15]:
   pos=sh.copy();pos.translate(App.Vector(dx,0,dz))
   for r in [rear,raised]+staticrefs:collision(pos,r,'slider running tolerance/'+r.Name)
   collision(pos,switchbody,'slider running tolerance/switchbody')
  probe=sh.copy();probe.translate(App.Vector(dx,0,.50));retention.append(probe.common(raised.Shape).Volume)
  probe=sh.copy();probe.translate(App.Vector(dx,0,-.50));down_retention.append(probe.common(rear.Shape).Volume)
 for dx in [-.6,.6]:
  probe=sh.copy();probe.translate(App.Vector(dx,0,0));lateral_retention.append(probe.common(rear.Shape).Volume)
for dy in [-.85,3.35]:
 probe=slider.Shape.copy();probe.translate(App.Vector(0,dy,0));endstops.append(probe.common(rear.Shape).Volume)
report['slider'].update(minimum_top_stop_overlap_at_0_5mm_lift_mm3=min(retention),minimum_bottom_stop_overlap_at_0_5mm_drop_mm3=min(down_retention),minimum_lateral_stop_overlap_at_0_6mm_mm3=min(lateral_retention),minimum_end_stop_overlap_at_0_3mm_overtravel_mm3=min(endstops),minimum_nominal_PCB_edge_gap_mm=slider.Shape.distToShape(doc.Ref_Board.Shape)[0])
# No part flex is required for top-down loading with rear flat and front absent.
for k in range(49):
 dz=k*.25;sh=slider.Shape.copy();sh.translate(App.Vector(0,0,dz))
 for r in [rear]+allrefs:collision(sh,r,'slider drop-in '+str(dz)+'/'+r.Name)
# Speaker installed before PCB, with its own adhesive. Check enlarged body and tab.
spbody=spmax.Shape.fuse(tab.Shape)
for k in range(33):
 sh=spbody.copy();sh.translate(App.Vector(0,0,k*.5))
 collision(sh,rear,'speaker drop-in');collision(sh,batterymax,'speaker drop-in/battery')
# Front placement onto seated assembly; excludes its intended insert engagement.
for k in range(33):
 sh=raised.Shape.copy();sh.translate(App.Vector(0,0,k*.5))
 for r in [rear,slider]+allrefs:collision(sh,r,'front drop-in '+str(k*.5)+'/'+r.Name)
tfapproach=Part.makeBox(11.4,11,1.4,App.Vector(4.8511-5.7,19.9,BR-1.5))
for sh in [rear,raised]:collision(tfapproach,sh,'TF insertion')
report['speaker']['grille_open_area_mm2']=sum(g.Shape.Volume/(FLOOR+.3) for g in grilles)
report['speaker']['max_body_to_outer_wall_mm']=spmax.Shape.distToShape(chwall.Shape)[0]
(REPORT/'fit_check_v10.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
doc.saveAs(str(OUT/'myMicrobyte_enclosure_v10.FCStd'))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
assert all(p['valid'] and p['solids']==1 for p in report['parts']),'invalid solids'
assert not report['collisions'],'collisions in report'
assert min(retention+down_retention+lateral_retention+endstops)>.001,'slider geometric retention failure'
Part.export(printables,str(OUT/'myMicrobyte_enclosure_v10.step'))
meshes=[]
for o,name in [(raised,'FrontShell'),(rear,'RearShell'),(slider,'PowerSlider')]:
 sh=o.Shape.copy()
 if o==slider:sh.rotate(App.Vector(),App.Vector(0,1,0),-90)
 # Front stays face UP, rear exterior face down; slider inner flange on bed, grip UP.
 b=sh.BoundBox;sh.translate(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
 m=MeshPart.meshFromShape(Shape=sh,LinearDeflection=.025,AngularDeflection=.10,Relative=False)
 err=abs(m.Volume-o.Shape.Volume)/o.Shape.Volume
 assert m.isSolid() and not m.hasNonManifolds() and not m.hasSelfIntersections() and err<.001,name
 m.write(str(OUT/(name+'_print.stl')))
 meshes.append({'name':name,'closed':True,'self_intersections':False,'volume_error_fraction':err,'bounds_mm':[m.BoundBox.XLength,m.BoundBox.YLength,m.BoundBox.ZLength]})
(REPORT/'export_validation_v10.json').write_text(json.dumps({'parts':meshes},indent=2))
print('v10 validated and exported',flush=True)
