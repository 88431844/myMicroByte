"""Additional tolerance scenarios following real v0.4 fit failure.
These are stated manufacturing allowances, not measurements of the user's PCB.
"""
from pathlib import Path
import sys,json
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1]
d=A.openDocument(str(R/'output/v06/myMicrobyte_enclosure_v06.FCStd'))
f=d.FrontShell_v06.Shape;r=d.RearShell_v06.Shape
fail=[];results=[]
# Worst provided LCD envelope plus 0.2 mm board-thickness growth / placement offset.
# Switch envelopes additionally allow +0.2 mm solder stand-off.
names=['LCD_ToleranceEnvelope','Ref_UP','Ref_DOWN','Ref_LEFT','Ref_RIGHT','Ref_START','Ref_SELECT','Ref_MENU','Ref_A','Ref_B']
for n in names:
 gap=100
 for dx,dy in [(0,0),(.2,.2),(.2,-.2),(-.2,.2),(-.2,-.2)]:
  s=d.getObject(n).Shape.copy();s.translate(A.Vector(dx,dy,.2 if n.startswith('LCD') else .4))
  vol=f.common(s).Volume;gap=min(gap,f.distToShape(s)[0])
  if vol>.001:fail.append(dict(part=n,offset=[dx,dy],overlap=vol))
 results.append(dict(part=n,xy_offset_mm=.2,z_growth_mm=.2 if n.startswith('LCD') else .4,min_clearance_mm=gap))
# Full board including its true rounded edge, displaced within the XY allowance.
for dx,dy in [(.15,.15),(.15,-.15),(-.15,.15),(-.15,-.15)]:
 s=d.Ref_Board.Shape.copy();s.translate(A.Vector(dx,dy,0))
 for name,sh in [('front',f),('rear',r)]:
  vol=sh.common(s).Volume
  if vol>.001:fail.append(dict(part='board',shell=name,offset=[dx,dy],overlap=vol))
# Upper support pocket: 1.80 mm PCB + 0.15 mm proud insert remains 0.20 mm free.
pocket=2.15;board=1.8;proud=.15
results.append(dict(part='support_stack',pocket_mm=pocket,board_scenario_mm=board,insert_proud_scenario_mm=proud,remaining_mm=pocket-board-proud))
# Minimum threaded engagement after lifting the insert seat; useful for M2x5 reuse.
results.append(dict(part='M2x5_engagement',minimum_nominal_mm=7.9+5-11.15))
# Uniform rectangular envelopes plus extra positioning error, without shrinking connectors.
bat=d.Battery_ToleranceEnvelope.Shape
for n in ['Ref_U1','USB_Envelope','SPEAKER_ConnectorEnvelope','SPEAKER_PlugEnvelope']:
 s=d.getObject(n).Shape
 results.append(dict(part='battery_to_'+n,min_clearance_mm=bat.distToShape(s)[0]))
report=dict(revision='0.6',scenarios=results,failures=fail,limitations=['Checks use conservative dimensions and source STEP. Solder blobs, warped parts, rough support removal and actual switch electrical stroke still need trial fitting.','The PCB is supported from the rear with a free upper clearance. If the assembled board rattles, use local thin nonconductive pads on the four supports; never pad against LCD or battery.'])
(R/'reports/v06/tolerance_validation_v06.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert not fail,fail
