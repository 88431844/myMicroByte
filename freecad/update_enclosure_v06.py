"""FreeCAD v0.6: removable speaker back chamber based on the v0.5 fit revision.
Regenerate with FreeCAD's bundled Python. Millimetres; source PCB XY preserved.
Parameters are documented in the native sheet; edit VALUES here and regenerate.
"""
from pathlib import Path
import sys, json
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, MeshPart
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/v06'; REPORT=ROOT/'reports/v06'
OUT.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
VALUES=dict(BoardRearZ=9.0,BoardT=1.60005,BoardPocketT=2.15,Floor=1.4,FrontUnderZ=12.8,Face=1.6,
 OuterW=85.,OuterH=45.,OuterR=5.5,Wall=2.,RearRound=1.8,FrontRound=1.8,SeamGap=.1,
 BatteryW=50.,BatteryH=28.,BatteryT=3.,BatteryCx=-4.,BatteryCy=-3.9,BatteryFrameW=52.,BatteryFrameH=30.,
 SpeakerCx=30.4,SpeakerCy=-1.5,ChamberCx=30.4,ChamberCy=-2.65,ChamberW=13.2,ChamberH=20.1,ChamberWall=1.0,ChamberWallTop=5.9,ChamberLidUnder=6.2,ChamberLidTop=7.0,AcousticSealT=.3,WindowW=29.72,WindowH=29.72,ScreenCx=.110,ScreenCy=.123,
 LCDClearW=32.72,LCDClearH=34.92,LCDPocketCeiling=13.3,LCDRailBottom=12.05,ButtonFaceZ=14.0,TFSlotW=14.2,TFSlotH=3.8,ButtonHole=7.4,
 InsertPilotD=2.8,InsertDepth=2.15,RearSeatT=1.1,SliderTravel=3.6,SliderLower=-.55,SliderUpper=3.05)
v=VALUES; BR=v['BoardRearZ']; PF=BR+v['BoardT']; TOP=v['FrontUnderZ']+v['Face']; FLOOR=v['Floor']
SEAM=BR+.8; FB=SEAM+v['SeamGap']; BOSSBOTTOM=BR+v['BoardPocketT']
old=App.openDocument(str(ROOT/'output/v03/myMicrobyte_enclosure_v03.FCStd'))
doc=App.newDocument('myMicrobyte_v06');doc.Label='myMicrobyte v0.6 / 可拆喇叭音腔·连续密封圈·扩大出声孔'
p=doc.addObject('Spreadsheet::Sheet','Parameters');p.Label='尺寸记录 / 修改生成脚本 VALUES 后重建'
for i,(a,value) in enumerate(v.items(),1):p.set('A'+str(i),a);p.set('B'+str(i),str(value));p.setAlias('B'+str(i),a)
p.setColumnWidth('A',240)
construction=doc.addObject('App::DocumentObjectGroup','Construction');construction.Label='构造特征 / 原生布尔树'
refs=doc.addObject('App::DocumentObjectGroup','PCBReference');refs.Label='PCB、LCD 与选型占位'
keep=doc.addObject('App::DocumentObjectGroup','ConnectorKeepouts');keep.Label='检查包络（隐藏）'
hardware=doc.addObject('App::DocumentObjectGroup','Hardware_v06');hardware.Label='M2 螺丝与热熔螺母'
seals=doc.addObject('App::DocumentObjectGroup','AcousticSeals');seals.Label='声学密封胶圈 / 非打印件'
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
# Battery is a selection placeholder, not an already purchased pack.
battery=feat('Battery_Assumed',Part.makeBox(50,28,3,App.Vector(-29,-17.9,FLOOR+.3)),'3 mm 电池选型占位 / 50×28×3',refs)
batterymax=feat('Battery_ToleranceEnvelope',Part.makeBox(51,29,3.3,App.Vector(-29.5,-18.4,FLOOR+.3)),'成品电池检查包络 51×29×3.3',keep)
SX=v['SpeakerCx'];SY=v['SpeakerCy'];SZ=FLOOR+.4+.3
speaker=feat('Speaker_1510',capsule(10,15,SZ,3.5,SX,SY),'1510 喇叭 / 15×10×3.5',refs)
spmax=feat('Speaker_ToleranceEnvelope',capsule(10.2,15.2,SZ,3.9,SX,SY),'喇叭尺寸与胶层最坏包络',keep)
tab=feat('Speaker_TabEnvelope',Part.makeBox(3,2.5,1,App.Vector(SX-1.5,SY-10,SZ)),'喇叭端部凸耳包络',keep)
# Rounded exterior blanks; the upper and lower perimeter rounds improve grip.
rearblank=rounded('RearBlank',85,45,5.5,0,SEAM)
rearouter=edge_round('RearGripRound',rearblank,0,v['RearRound'])
rearvoid=rounded('RearCavity',81,41,3.5,FLOOR,SEAM+2)
rearbase=cut('RearWallsAndFloor',rearouter,rearvoid)
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
# Continuous front baffle seal separates the grille plenum from the rear cavity.
# The speaker tab notch no longer cuts through the sealing seat.
spseat=feat('SpeakerContinuousSeat',capsule(10.8,16.2,FLOOR-.1,.5,SX,SY).cut(capsule(8,13,FLOOR-.2,.8,SX,SY)))
frontseal=feat('SpeakerFrontSeal',capsule(10,15,FLOOR+.4,.3,SX,SY).cut(capsule(8,13,FLOOR+.35,.4,SX,SY)),'喇叭前密封胶圈 / 装配厚0.3 mm·非打印件',seals)
CX=v['ChamberCx'];CY=v['ChamberCy'];CW=v['ChamberW'];CH=v['ChamberH']
chouter=rounded('ChamberOuterWall',CW,CH,1.8,FLOOR-.1,v['ChamberWallTop']-(FLOOR-.1),CX,CY)
chvoid=rounded('ChamberWallVoid',CW-2,CH-2,.8,FLOOR-.2,v['ChamberWallTop']-FLOOR+.5,CX,CY)
chwall=cut('ChamberWallRing',chouter,chvoid)
# Two fine wires exit through this top-open notch. Fill around the wires with
# removable soft sealant; the notch is NOT a tuned acoustic port.
leadslot=box('AcousticWireExit',2.2,2.4,2.0,CX-1.1,CY-CH/2-.2,4.8)
chwall=cut('ChamberWallWithWireExit',chwall,leadslot)
# 0.3 mm compressed seal/tape ring also fixes the lid for the first trial.
cs=rr(CW,CH,1.8,5.9,.3,CX,CY).cut(rr(CW-2,CH-2,.8,5.85,.4,CX,CY)).cut(leadslot.Shape).removeSplitter()
capseal=feat('ChamberLidSeal',cs,'腔盖密封胶圈 / 装配厚0.3 mm·非打印件',seals)
# Flat outer side prints on the bed. Two small underside tabs locate the lid
# without intruding into the speaker or requiring a snap-fit in thin PLA.
capplate=rounded('ChamberLidPlate',CW,CH,1.8,6.2,.8,CX,CY)
caplocators=[box('ChamberLidLocator'+str(i),1.2,1.2,.85,x,CY-CH/2+1.6,5.4) for i,x in enumerate([CX-CW/2+1.3,CX+CW/2-2.5])]
lid=fuse('AcousticLid_v06',[capplate]+caplocators);lid.Label='可拆喇叭音腔盖 / 0.8 mm·背面定位凸台'
construction.removeObject(lid)
rearbase=fuse('RearWithFramesAndChamber',[rearbase,bframe,spseat,chwall])
# Grille retains 1 mm webs and stays inside the unobstructed front plenum.
grilles=[]
for i,dy in enumerate([-4.4,-2.2,0,2.2,4.4]):
 g=Part.makeBox(7,1.2,FLOOR+.3,App.Vector(SX-3.5,SY+dy-.6,-.1)).common(capsule(8,13,-.15,FLOOR+.5,SX,SY))
 grilles.append(feat('SpeakerGrille'+str(i),g))
# LCD pocket leaves 0.70 mm nominal glass clearance; rim stays 1.1 mm thick.
lcdpocket=rounded('LCDGlassPocket',v['LCDClearW'],v['LCDClearH'],.35,FB-.2,v['LCDPocketCeiling']-(FB-.2),.110,-1.427)
frontbase=cut('FrontLCDClearance',frontbase,lcdpocket)
# Short rails hang 0.75 mm below the main underside; overlap the glass side only.
rails=[];lcx=.110;lcy=-1.427;hw=v['LCDClearW']/2;hh=v['LCDClearH']/2;rz=v['LCDRailBottom']
for ix in [-1,1]:
 for iy in [-1,1]:
  xx=lcx+ix*hw;yy=lcy+iy*hh
  rails.append(box('LCDRailX',6,1,v['FrontUnderZ']-rz+.08,xx-5 if ix>0 else xx-1,yy if iy>0 else yy-1,rz))
  rails.append(box('LCDRailY',1,5,v['FrontUnderZ']-rz+.08,xx if ix>0 else xx-1,yy-5 if iy>0 else yy,rz))
frontbase=fuse('FrontWithShortLCDLocator',[frontbase]+rails)
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
window=box('LCDWindow',v['WindowW'],v['WindowH'],7,.110-v['WindowW']/2,.123-v['WindowH']/2,PF-.1)
# 0.7 mm bevel keeps the aperture clear toward the outside.
def xywire(cx,cy,z,w,h):
 ps=[App.Vector(cx-w/2,cy-h/2,z),App.Vector(cx+w/2,cy-h/2,z),App.Vector(cx+w/2,cy+h/2,z),App.Vector(cx-w/2,cy+h/2,z)]
 return Part.makePolygon(ps+[ps[0]])
winlead=feat('LCDWindowBevel',Part.makeLoft([xywire(.110,.123,TOP-.5,29.72,29.72),xywire(.110,.123,TOP+.1,30.92,30.92)],True,True))
frontcut += [window,winlead]
buttons={'UP':(-28.707,6.543),'DOWN':(-28.707,-4.760),'LEFT':(-34.168,.955),'RIGHT':(-23.119,.828),'START':(23.998,-15.174),'SELECT':(-23.246,-15.174),'MENU':(23.998,14.798),'A':(34.285,.955),'B':(25.903,-2.728)}
# Recess both control fields by 0.4 mm. Through-clearance exposes the original
# switch body; no thin roof or fragile floating centre island remains.
for side in [-1,1]:
 frontcut.append(rounded('ButtonFieldRecess',22.0,39.4,3.0,v['ButtonFaceZ'],2,side*29.5,0))
for n,(x,y) in buttons.items():
 frontcut.append(rounded('SwitchThrough_'+n,7.4,7.4,.55,PF-.2,6,x,y))
# Deliberate connected D-pad opening: the four cuts intersect the central aperture.
frontcut.append(rounded('DpadCentreOpening',7.2,7.2,.6,PF-.2,6,-28.707,.89))
# Rear charge indicator only. Front RUN hole removed after confirmed poor transmission.
rearcut.append(cyl('ChargeLEDLightHole',1.,BR+.3,38.476,2.225,-.1))
rearcut += grilles
# Slider installs vertically from the OPEN rear split face, after PCB placement.
# The socket is through-Z and clears the PCB edge; front cover becomes the retainer.
cz=BR-1.15;cy=-6.3186;mid=cy+(v['SliderLower']+v['SliderUpper'])/2
flange=box('SliderInnerFlange',1.1,6.8,3.8,40.35,cy-3.4,cz-2.2)
neck=box('SliderNeck',1.8,3.2,2.2,41.4,cy-1.6,cz-1.1)
thumbshape=Part.makeBox(1.5,6.8,3.4,App.Vector(43.0,cy-3.4,cz-1.7))
thumb=feat('SliderRoundedThumb',thumbshape.makeFillet(.35,thumbshape.Edges))
grips=[]
for dy in [-2.4,-1.2,0,1.2,2.4]:
 gs=Part.makeBox(.65,.60,2.6,App.Vector(44.30,cy+dy-.3,cz-1.3))
 grips.append(feat('SliderGripRib',gs.makeFillet(.18,gs.Edges)))
socket=box('SliderOpenSocket',1.25,1.95,6,40.2,cy-.975,cz-2.8)
slider=cut('PowerSlider_v06',fuse('SliderWithGrip',[flange,neck,thumb]+grips),socket)
slider.Label='电源拨帽 v0.6 / 顶部装入·3.6 mm机械行程·指纹朝上打印'
construction.removeObject(slider)
tracks=fuse('SliderOpenTracks',[box('SliderInnerOpenTrack',1.75,10.4,8,40.10,mid-5.2,cz-2.5),box('SliderOuterOpenTrack',5,6.8,7,41.70,mid-3.4,cz-1.4)])
rearcut.append(tracks)
# Only remove the tongue/receiver return below the retaining face; keep the front
# side wall intact above Z9.85 as the upper slide stop.
frontcut.append(box('SliderFrontReturnClearance',2.0,11.0,1.0,40.1,mid-5.5,8.85))
rear=cut('RearShell_v06',rearbase,fuse('RearCutters',rearcut));rear.Label='后盖 v0.6 / 一体音腔围壁·52×30电池框'
front=cut('FrontShell_v06',frontbase,fuse('FrontCutters',frontcut));front.Label='前盖 v0.6 / 下沉按键·短屏幕框·TF遮板唇边'
construction.removeObject(rear);construction.removeObject(front)
doc.recompute()
printables=[rear,front,slider,lid]
report={'revision':'0.6','units':'mm','shell_size_mm':[85,45,TOP],'board_rear_z_mm':BR,'board_thickness_CAD_mm':v['BoardT'],'board_pocket_mm':v['BoardPocketT'],'seam_gap_mm':v['SeamGap'],'rear_depth_reduction_mm':13-BR,'battery_nominal_placeholder_mm':[50,28,3],'battery_checked_finished_envelope_mm':[51,29,3.3],'battery_frame_clear_mm':[52,30],'lcd_window_mm':[29.72,29.72],'lcd_active_mm':[27.72,27.72],'lcd_glass_recess_mm':TOP-(PF+2),'button_nominal_protrusion_mm':PF+5-v['ButtonFaceZ'],'button_face_z_mm':v['ButtonFaceZ'],'lcd_locator_height_mm':v['FrontUnderZ']-rz,'slider_mechanical_travel_mm':3.6,'slider_socket_play_mm':.65,'minimum_insert_blind_roof_mm':v['ButtonFaceZ']-(BOSSBOTTOM-.01+v['InsertDepth']+.02),'tf_throat_mm':[14.2,3.8],'usb_throat_mm':[10.4,4.6],'exterior_edge_round_mm':[1.8,1.8],'front_run_hole':False,'speaker_center_mm':[SX,SY],'chamber_outer_xy_mm':[CW,CH],'chamber_lid_thickness_mm':.8,'chamber_wall_thickness_mm':1.,'acoustic_seal_compressed_thickness_mm':.3,'parts':[],'collisions':[],'clearances_mm':{},'assumptions':['Acoustic layout only: no measured SPL benefit. Rear vent details and speaker fs/Vas/Qts are unavailable. Compare the removable lid on/off using the same signal and volume.','Both perimeter seals and the wire exit must be airtight. Gaskets and soft wire sealant are non-printed consumables.','Battery model not chosen; prioritize thin rear. Select finished pack within checked envelope including protection and wrap.','Connector and plug depth remains conservative 5.5 mm, not physically measured.','MSK slider mechanical travel3.6 mm; socket play about0.65 mm for the supplied1.3 mm actuator, leaving up to2.95 mm actuator motion. Electrical end positions still require physical trial. Guide play is not a measured printer calibration.','Speaker tab shape is a conservative allowance from image; cable bending and plug strain relief require physical trial.','Board pocket2.15 mm is a non-clamping trial clearance; actual solder, warp and proud inserts are not in the source STEP. Do not force the joint with screws.','TF brow retains at least0.35 mm above checked card path; a small part of the lower PCB edge remains visible to preserve insertion clearance.','M2×2×3 insert interference with 2.8 mm pilot is intentional. Heat insertion fit requires trial.']}
def collision(a,b,tag='fit'):
 sa=shape(a);sb=shape(b)
 if not sa.BoundBox.intersect(sb.BoundBox):return
 vol=sa.common(sb).Volume
 if vol>.001:report['collisions'].append({'a':a.Name if hasattr(a,'Name') else 'swept_volume','b':b.Name,'tag':tag,'volume_mm3':vol})
for o in printables:
 s=o.Shape;report['parts'].append({'name':o.Name,'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume})
collision(rear,front)
collision(lid,rear);collision(lid,front);collision(lid,slider)
allrefs=list(refs.Group)+list(keep.Group)+list(seals.Group)
for sh in [rear,front,lid]:
 for r in allrefs:collision(sh,r)
for movable in [batterymax,spmax,tab]:
 for r in allrefs:
  if r.Name.startswith(('Battery_','Speaker_')):continue
  collision(movable,r,'electronics layout')
collision(batterymax,spmax)
for r in [rear,front,lid]+allrefs:collision(slider,r,'slider rest')
# Continuous sweep: vertex-translated start/end and swept boundary faces. Curved
# grip surfaces stay outside the enclosure; exact planar guide envelope is checked.
def linear_sweep(s,delta):
 e=s.copy();e.translate(delta);out=s.fuse(e)
 for f in s.Faces:
  try:
   if abs(f.normalAt(0,0).dot(delta))>1e-5:out=out.fuse(f.extrude(delta))
  except Exception:pass
 return out
# Conservative slider envelope contains filleted thumb/ribs, with exact socket.
ss=Part.makeBox(1.1,6.8,3.8,App.Vector(40.35,cy-3.4,cz-2.2)).fuse(Part.makeBox(1.8,3.2,2.2,App.Vector(41.4,cy-1.6,cz-1.1))).fuse(Part.makeBox(1.95,6.8,3.4,App.Vector(43.,cy-3.4,cz-1.7))).cut(socket.Shape)
ss.translate(App.Vector(0,v['SliderLower'],0))
sweep=linear_sweep(ss,App.Vector(0,v['SliderTravel'],0))
for r in [rear,front,lid]+allrefs:
 if r.Name=='Ref_SW3':continue
 collision(sweep,r,'slider full mechanical envelope')
# Fixed switch body is checked separately from its moving white actuator.
switchbody=doc.Ref_SW3.Shape.common(Part.makeBox(10,14,5,App.Vector(29.5,-12,6)))
if sweep.common(switchbody).Volume>.001:report['collisions'].append({'tag':'slider vs fixed switch body'})
# Entire drop-in path from above, with PCB already seated and front cover removed.
install_envelope=ss.copy();install_envelope.translate(App.Vector(0,-v['SliderLower'],0))
insertion=linear_sweep(install_envelope,App.Vector(0,0,12))
for r in [rear,lid]+allrefs:
 if r.Name=='Ref_SW3':continue
 collision(insertion,r,'vertical slider installation')
if insertion.common(switchbody).Volume>.001:report['collisions'].append({'tag':'slider installation vs fixed switch body'})
report['slider_retention_mm']={'flange_height':3.8,'outer_slot_height':FB-(cz-1.4),'minimum_vertical_capture':3.8-(FB-(cz-1.4))}
report['slider_installation']='vertical +Z to seated position; front removed; open socket captures actuator'
# Full card approach beyond connector edge, and worst-case PCB thickness.
tfapproach=Part.makeBox(11.4,11,1.4,App.Vector(4.8511-5.7,19.9,BR-1.5))
for sh in [rear,front,lid]:collision(tfapproach,sh,'TF insertion path')
for sc in screws:
 for r in allrefs:collision(sc,r,'screw path')
for n,a,b in [('battery_ESP32',batterymax,doc.Ref_U1),('battery_USB',batterymax,doc.USB_Envelope),('battery_speaker_plug',batterymax,doc.SPEAKER_PlugEnvelope),('speaker_battery_connector',spmax,doc.BAT_ConnectorEnvelope),('glass_front',doc.LCD_ToleranceEnvelope,front)]:report['clearances_mm'][n]=a.Shape.distToShape(b.Shape)[0]
report['switch_front_clearances_mm']={n:front.Shape.distToShape(doc.getObject('Ref_'+n).Shape)[0] for n in buttons}
# New chamber assembly is completed BEFORE the PCB is put in the rear shell.
lidpath=linear_sweep(lid.Shape,App.Vector(0,0,12))
for r in [rear,batterymax,spmax,tab,frontseal,capseal]:collision(lidpath,r,'lid vertical installation before PCB')
speakerpath=linear_sweep(spmax.Shape.fuse(tab.Shape),App.Vector(0,0,12))
for r in [rear,batterymax,frontseal]:collision(speakerpath,r,'speaker insertion before chamber lid')
# Back-cavity volume with installed solid speaker, seat, gaskets and lid tabs.
# The driver internal cavities are unknown, so this is an external-envelope estimate.
backair=rr(CW-2,CH-2,.8,FLOOR,6.2-FLOOR,CX,CY)
for s0 in [speaker.Shape,tab.Shape,spseat.Shape,frontseal.Shape,lid.Shape,capsule(8,13,FLOOR,.7,SX,SY)]:backair=backair.cut(s0)
report['rear_air_volume_estimate_cm3']=backair.Volume/1000
report['grille_open_area_mm2']=sum(g.Shape.Volume/(FLOOR+.3) for g in grilles)
report['acoustic_lid_attachment']='0.3 mm compressed double-sided sealing ring, two underside locating tabs; removable for A/B trial'
report['wire_exit']='2.2 mm wide top-open notch; seal around two wires with removable soft sealant; not a port'
for n,obj in [('lid_to_switch',doc.Ref_SW3),('chamber_to_battery_frame',bframe),('chamber_to_battery_connector',doc.BAT_ConnectorEnvelope),('lid_to_speaker_max',spmax),('chamber_to_charge_light_path',doc.ChargeLEDLightHole)]:
 s0=lid.Shape if n.startswith('lid_') else chwall.Shape.fuse(lid.Shape)
 report['clearances_mm'][n]=s0.distToShape(obj.Shape)[0]
report['acoustic_assembly_order']=['front seal on continuous seat','speaker face toward rear grille','wires through notch','lid seal and lid','seal around wires','PCB','power slider','front shell','screws']
(REPORT/'fit_check_v06.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
doc.saveAs(str(OUT/'myMicrobyte_enclosure_v06.FCStd'))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
assert all(x['valid'] and x['solids']==1 for x in report['parts']),'invalid print solid'
assert not report['collisions'],'collisions; inspect report'
Part.export(printables,str(OUT/'myMicrobyte_enclosure_v06.step'))
for o,name in [(rear,'RearShell'),(front,'FrontShell'),(slider,'PowerSlider'),(lid,'AcousticLid')]:
 s=o.Shape.copy()
 if o in [front,lid]:s.rotate(App.Vector(),App.Vector(1,0,0),180)
 elif o==slider:s.rotate(App.Vector(),App.Vector(0,1,0),-90) # textured +X face now points UP
 b=s.BoundBox;s.translate(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
 m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.035,AngularDeflection=.1,Relative=False)
 assert m.isSolid(),name
 mb=m.BoundBox;m.translate(-mb.XMin,-mb.YMin,-mb.ZMin)
 m.write(str(OUT/(name+'_print.stl')))
print('v0.6 exports complete',flush=True)
