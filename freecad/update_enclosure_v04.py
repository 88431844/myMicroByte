"""FreeCAD v0.4: thin shells following physical v0.3 fit feedback.
Regenerate with FreeCAD's bundled Python. Millimetres; source PCB XY preserved.
Parameters are documented in the native sheet; edit VALUES here and regenerate.
"""
from pathlib import Path
import sys, json
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, MeshPart
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/v04'; REPORT=ROOT/'reports/v04'
OUT.mkdir(parents=True,exist_ok=True); REPORT.mkdir(parents=True,exist_ok=True)
VALUES=dict(BoardRearZ=9.0,BoardT=1.60005,BoardPocketT=1.75,Floor=1.4,FrontUnderZ=13.0,Face=1.9,
 OuterW=85.,OuterH=45.,OuterR=5.5,Wall=2.,RearRound=1.8,FrontRound=1.8,SeamGap=.1,
 BatteryW=50.,BatteryH=25.,BatteryT=3.,BatteryCx=-4.,BatteryCy=-4.5,BatteryFrameW=52.,BatteryFrameH=27.,
 SpeakerCx=32.,SpeakerCy=-1.,WindowW=29.72,WindowH=29.72,ScreenCx=.110,ScreenCy=.123,
 LCDClearW=32.22,LCDClearH=34.42,TFSlotW=14.2,TFSlotH=3.8,ButtonHole=5.8,
 InsertPilotD=2.8,InsertDepth=2.15,RearSeatT=1.1,SliderTravel=2.3)
v=VALUES; BR=v['BoardRearZ']; PF=BR+v['BoardT']; TOP=v['FrontUnderZ']+v['Face']; FLOOR=v['Floor']
SEAM=BR+.8; FB=SEAM+v['SeamGap']; BOSSBOTTOM=BR+v['BoardPocketT']
old=App.openDocument(str(ROOT/'output/v03/myMicrobyte_enclosure_v03.FCStd'))
doc=App.newDocument('myMicrobyte_v04');doc.Label='myMicrobyte v0.4 / 薄壳·裸按键·LED孔'
p=doc.addObject('Spreadsheet::Sheet','Parameters');p.Label='尺寸记录 / 修改生成脚本 VALUES 后重建'
for i,(a,value) in enumerate(v.items(),1):p.set('A'+str(i),a);p.set('B'+str(i),str(value));p.setAlias('B'+str(i),a)
p.setColumnWidth('A',240)
construction=doc.addObject('App::DocumentObjectGroup','Construction');construction.Label='构造特征 / 原生布尔树'
refs=doc.addObject('App::DocumentObjectGroup','PCBReference');refs.Label='PCB、LCD 与选型占位'
keep=doc.addObject('App::DocumentObjectGroup','ConnectorKeepouts');keep.Label='检查包络（隐藏）'
hardware=doc.addObject('App::DocumentObjectGroup','Hardware_v04');hardware.Label='M2 螺丝与热熔螺母'
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
battery=feat('Battery_Assumed',Part.makeBox(50,25,3,App.Vector(-29,-17,FLOOR+.3)),'3 mm 电池选型占位 / 50×25×3',refs)
batterymax=feat('Battery_ToleranceEnvelope',Part.makeBox(51,26,3.3,App.Vector(-29.5,-17.5,FLOOR+.3)),'成品电池检查包络 51×26×3.3',keep)
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
# Board is held between supports with 1.75 mm clearance. Seam datum independent of board thickness.
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
bframe=cut('BatteryFrame',box('BatteryFrameOuter',54.4,29.4,1.9,-31.2,-19.2,FLOOR-.1),box('BatteryFrameInner',52,27,2.2,-30,-18,FLOOR-.2))
bframe=cut('BatteryCableExit',bframe,box('BatteryCableRelief',8,4,2.5,16,7,FLOOR+.1))
# Speaker seat contacts only the perimeter, diaphragm faces rear grille.
spwall=feat('SpeakerFrameWall',capsule(13.2,18.2,FLOOR-.1,3.1,SX,SY).cut(capsule(10.8,15.8,FLOOR-.2,3.4,SX,SY)))
spseat=feat('SpeakerSeat',capsule(10.8,15.8,FLOOR-.1,.5,SX,SY).cut(capsule(8,13,FLOOR-.2,.8,SX,SY)))
spframe=fuse('SpeakerFrameAndSeat',[spwall,spseat])
spreliefs=fuse('SpeakerReliefs',[box('SpeakerLeadNotch',4,5,5,SX-2,SY+6.7,FLOOR+.7),box('SpeakerTabNotch',3.5,4.6,5,SX-1.75,SY-10.5,FLOOR+.3)])
spframe=cut('SpeakerFrame',spframe,spreliefs)
rearbase=fuse('RearWithFrames',[rearbase,bframe,spframe])
# Four corner locating rails clear glass by 0.35 mm per side and leave FPC routing open.
rails=[];lcx=.110;lcy=-1.427;hw=v['LCDClearW']/2;hh=v['LCDClearH']/2;rz=PF+.35
for ix in [-1,1]:
 for iy in [-1,1]:
  xx=lcx+ix*hw;yy=lcy+iy*hh
  rails.append(box('LCDRailX',7,1,v['FrontUnderZ']-rz+.05,xx-6 if ix>0 else xx-1,yy if iy>0 else yy-1,rz))
  rails.append(box('LCDRailY',1,6,v['FrontUnderZ']-rz+.05,xx if ix>0 else xx-1,yy-6 if iy>0 else yy,rz))
frontbase=fuse('FrontWithLCDLocator',[frontbase]+rails)
# Openings and four machine screw paths.
rearcut=[box('BatteryPlugPostRelief',6.6,3.6,6.1,32.128,12.152,BR-5.8)];frontcut=[];inserts=[];screws=[]
for i,(x,y) in enumerate(holes):
 rearcut += [cyl('RearScrewThrough'+str(i),1.15,BR+2,x,y,-.1),cyl('RearDeepHeadBore'+str(i),2.3,BR-v['RearSeatT']+.1,x,y,-.1)]
 frontcut += [cyl('InsertPilot'+str(i),1.4,v['InsertDepth']+.02,x,y,BOSSBOTTOM-.01),cyl('ScrewTipRelief'+str(i),1.15,2.6,x,y,BOSSBOTTOM-.01),feat('InsertLeadIn'+str(i),Part.makeCone(1.55,1.4,.3,App.Vector(x,y,BOSSBOTTOM-.01)))]
 inserts.append(feat('Hardware_Insert'+str(i+1),Part.makeCylinder(1.5,2,App.Vector(x,y,BOSSBOTTOM)).cut(Part.makeCylinder(.8,2.2,App.Vector(x,y,BOSSBOTTOM-.1))),'M2×2×3 热熔螺母',hardware))
 seat=BR-v['RearSeatT'];screws.append(feat('Hardware_Screw'+str(i+1),Part.makeCylinder(1,5,App.Vector(x,y,seat)).fuse(Part.makeCylinder(2,.8,App.Vector(x,y,seat-.8))),'M2×5 螺丝',hardware))
usb=port('USBThroatAndChamfer',-.00165,BR-1.8,10.4,4.6,-1)
tf=port('TFThroatAndChamfer',4.8511,BR-.8,v['TFSlotW'],v['TFSlotH'],1)
rearcut += [usb,tf];frontcut += [usb,tf]
window=box('LCDWindow',v['WindowW'],v['WindowH'],7,.110-v['WindowW']/2,.123-v['WindowH']/2,PF-.1)
# 0.7 mm bevel keeps the aperture clear toward the outside.
def xywire(cx,cy,z,w,h):
 ps=[App.Vector(cx-w/2,cy-h/2,z),App.Vector(cx+w/2,cy-h/2,z),App.Vector(cx+w/2,cy+h/2,z),App.Vector(cx-w/2,cy+h/2,z)]
 return Part.makePolygon(ps+[ps[0]])
winlead=feat('LCDWindowBevel',Part.makeLoft([xywire(.110,.123,TOP-.7,29.72,29.72),xywire(.110,.123,TOP+.1,31.32,31.32)],True,True))
frontcut += [window,winlead]
buttons={'UP':(-28.707,6.543),'DOWN':(-28.707,-4.760),'LEFT':(-34.168,.955),'RIGHT':(-23.119,.828),'START':(23.998,-15.174),'SELECT':(-23.246,-15.174),'MENU':(23.998,14.798),'A':(34.285,.955),'B':(25.903,-2.728)}
for n,(x,y) in buttons.items():
 relief_top=14.45 if n=='A' else 14.3
 frontcut.append(rounded('SwitchBodyRelief_'+n,7.2,7.2,.45,PF-.1,relief_top-(PF-.1),x,y))
 frontcut.append(rounded('SwitchOpening_'+n,5.8,5.8,.65,14.2,3,x,y))
# LED holes; front RUN path is through unmodified FR4 and must be tried physically.
rearcut.append(cyl('ChargeLEDLightHole',1.,BR+.3,38.476,2.225,-.1))
frontcut.append(cyl('RunLEDObservationHole',1.,5,-32.644,-17.206,PF-.1))
frontcut.append(feat('RunLEDInsideFunnel',Part.makeCone(1.55,1.,.6,App.Vector(-32.644,-17.206,12.95))))
for i,dy in enumerate([-4.8,-2.4,0,2.4,4.8]):rearcut.append(box('SpeakerGrille'+str(i),6,1,FLOOR+.3,SX-3,SY+dy-.5,-.1))
# Captive MSK-12C02 slider, original validated geometry translated to new PCB datum.
s=old.PowerSlider_v03.Shape.copy();s.translate(App.Vector(0,0,BR-13));slider=feat('PowerSlider_v04',s,'电源拨帽 / MSK-12C02',None)
cz=BR-1.15;mid=-5.1686
tracks=fuse('SliderTracks',[box('SliderInnerTrack',1.4,9.6,5,40.3,mid-4.8,cz-2.35),box('SliderOuterTrack',5,6.4,2.7,41.65,mid-3.2,cz-1.35),box('SliderForkRelief',1.1,6.4,2.5,39.65,mid-3.2,cz-1.25)])
rearcut.append(tracks);frontcut.append(tracks)
rear=cut('RearShell_v04',rearbase,fuse('RearCutters',rearcut));rear.Label='后盖 v0.4 / 圆边·薄电池仓·充电灯孔'
front=cut('FrontShell_v04',frontbase,fuse('FrontCutters',frontcut));front.Label='前盖 v0.4 / 裸开关·屏幕限位·RUN观察孔'
construction.removeObject(rear);construction.removeObject(front)
doc.recompute()
printables=[rear,front,slider]
report={'revision':'0.4','units':'mm','shell_size_mm':[85,45,TOP],'board_rear_z_mm':BR,'board_thickness_CAD_mm':v['BoardT'],'board_pocket_mm':v['BoardPocketT'],'seam_gap_mm':v['SeamGap'],'rear_depth_reduction_mm':13-BR,'battery_nominal_placeholder_mm':[50,25,3],'battery_checked_finished_envelope_mm':[51,26,3.3],'battery_frame_clear_mm':[52,27],'lcd_window_mm':[29.72,29.72],'lcd_active_mm':[27.72,27.72],'lcd_glass_recess_mm':TOP-(PF+2),'button_nominal_protrusion_mm':PF+5-TOP,'tf_throat_mm':[14.2,3.8],'usb_throat_mm':[10.4,4.6],'exterior_edge_round_mm':[1.8,1.8],'parts':[],'collisions':[],'clearances_mm':{},'assumptions':['Battery model not chosen; prioritize thin rear. Select finished pack within checked envelope including protection and wrap.','Connector and plug depth remains conservative 5.5 mm, not physically measured.','Front RUN hole is aligned to rear LED; copper and FR4 may block light. No PCB drilling is proposed.','MSK switch carriage stroke2.3 mm and fork play accommodate up to1.8 mm actuator movement; physical electrical end positions need confirmation.','Speaker tab shape is a conservative allowance from image; cable bending and plug strain relief require physical trial.','M2×2×3 insert interference with 2.8 mm pilot is intentional. Heat insertion fit requires trial.']}
def collision(a,b,tag='fit'):
 sa=shape(a);sb=shape(b)
 if not sa.BoundBox.intersect(sb.BoundBox):return
 vol=sa.common(sb).Volume
 if vol>.001:report['collisions'].append({'a':a.Name if hasattr(a,'Name') else 'swept_volume','b':b.Name,'tag':tag,'volume_mm3':vol})
for o in printables:
 s=o.Shape;report['parts'].append({'name':o.Name,'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume})
collision(rear,front)
allrefs=list(refs.Group)+list(keep.Group)
for sh in [rear,front]:
 for r in allrefs:collision(sh,r)
for movable in [batterymax,spmax,tab]:
 for r in allrefs:
  if r.Name.startswith(('Battery_','Speaker_')):continue
  collision(movable,r,'electronics layout')
collision(batterymax,spmax)
for r in [rear,front]+allrefs:collision(slider,r,'slider rest')
# Exact polyhedral slider sweep via union of start/end and swept boundary faces.
ss=slider.Shape;end=ss.copy();end.translate(App.Vector(0,v['SliderTravel'],0));sweep=ss.fuse(end)
for f in ss.Faces:
 try:
  if abs(f.normalAt(0,0).y)>.99:sweep=sweep.fuse(f.extrude(App.Vector(0,v['SliderTravel'],0)))
 except Exception:pass
for r in [rear,front]+allrefs:
 if r.Name=='Ref_SW3':continue
 collision(sweep,r,'continuous slider sweep')
# Full card approach beyond connector edge, and worst-case PCB thickness.
tfapproach=Part.makeBox(11.4,11,1.4,App.Vector(4.8511-5.7,19.9,BR-1.5))
for sh in [rear,front]:collision(tfapproach,sh,'TF insertion path')
for sc in screws:
 for r in allrefs:collision(sc,r,'screw path')
for n,a,b in [('battery_ESP32',batterymax,doc.Ref_U1),('battery_USB',batterymax,doc.USB_Envelope),('battery_speaker_plug',batterymax,doc.SPEAKER_PlugEnvelope),('speaker_battery_connector',spmax,doc.BAT_ConnectorEnvelope),('glass_front',doc.LCD_ToleranceEnvelope,front)]:report['clearances_mm'][n]=a.Shape.distToShape(b.Shape)[0]
report['switch_front_clearances_mm']={n:front.Shape.distToShape(doc.getObject('Ref_'+n).Shape)[0] for n in buttons}
(REPORT/'fit_check_v04.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
doc.saveAs(str(OUT/'myMicrobyte_enclosure_v04.FCStd'))
print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
assert all(x['valid'] and x['solids']==1 for x in report['parts']),'invalid print solid'
assert not report['collisions'],'collisions; inspect report'
Part.export(printables,str(OUT/'myMicrobyte_enclosure_v04.step'))
for o,name in [(rear,'RearShell'),(front,'FrontShell'),(slider,'PowerSlider')]:
 s=o.Shape.copy()
 if o==front:s.rotate(App.Vector(),App.Vector(1,0,0),180)
 elif o==slider:s.rotate(App.Vector(),App.Vector(0,1,0),90)
 b=s.BoundBox;s.translate(App.Vector(-b.XMin,-b.YMin,-b.ZMin))
 m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.035,AngularDeflection=.1,Relative=False)
 assert m.isSolid(),name
 mb=m.BoundBox;m.translate(-mb.XMin,-mb.YMin,-mb.ZMin)
 m.write(str(OUT/(name+'_print.stl')))
print('v0.4 exports complete',flush=True)
