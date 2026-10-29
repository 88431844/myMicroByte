"""Geometric feasibility of dry-fit latches and side springs, not force/FEA validation."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];d=A.openDocument(str(R/'output/v07/myMicrobyte_enclosure_v07.FCStd'))
fail=[];steps=[]
latches=[d.LidLatch0,d.LidLatch1]
rigid=d.RearRigidWithoutSpeakerSprings.Shape
for c in latches:rigid=rigid.cut(c.Shape)
for c in latches:
 s=c.Shape.copy();s.translate(A.Vector(0,-.25,0));rigid=rigid.fuse(s)
obs=[('rear with latches retracted .25 mm',rigid),('speaker max',d.Speaker_ToleranceEnvelope.Shape),('battery max',d.Battery_ToleranceEnvelope.Shape)]
obs += [(n,d.getObject(n).Shape) for n in ['SpeakerSideSpringL','SpeakerSideSpringR']]
def check_lid(angle,dy):
 s=d.AcousticLid_v07.Shape.copy();s.rotate(A.Vector(0,7.2,6.0),A.Vector(1,0,0),angle);s.translate(A.Vector(0,dy,0))
 for n,o in obs:
  if not s.BoundBox.intersect(o.BoundBox):continue
  vol=s.common(o).Volume
  if vol>.001:fail.append({'phase':'lid hook-and-snap installation','angle_deg':angle,'dy_mm':dy,'obstacle':n,'overlap_mm3':vol})
 steps.append({'angle_deg':angle,'dy_mm':dy})
for i in range(11):check_lid(-6,-2+i*.2)
for i in range(13):check_lid(-6+i*.5,0)
# Inclined speaker spring deflection: affine approximation with a fixed root plane.
# The user spreads the springs slightly during insertion; positive .30 mm at Z5.4.
flex=[]
for n,sign in [('SpeakerSideSpringL',-1),('SpeakerSideSpringR',1)]:
 m=A.Matrix();m.A13=sign*.30/3.6;m.A14=-sign*.30/3.6*1.8
 s=d.getObject(n).Shape.transformGeometry(m)
 # Ignore the base embedded in floor/wall. Check only active spring segment.
 active=s.common(Part.makeBox(100,100,20,A.Vector(-50,-50,2.05)))
 v=active.common(d.Speaker_ToleranceEnvelope.Shape).Volume
 if v>.001:fail.append({'phase':'speaker springs manually spread','spring':n,'overlap_mm3':v})
 # Spring is permitted to share its root with the wall; active segment must remain clear.
 wallgap=active.distToShape(d.ChamberWallWithSpringRelief.Shape)[0]
 flex.append({'spring':n,'assumed_tip_spread_mm':.30,'speaker_intersection_mm3':v,'active_wall_clearance_mm':wallgap})
r={'revision':'0.7','lid_sampled_poses':steps,'latch_release_mm':.25,'speaker_spring_deflection':flex,'failures':fail,'limitations':['Lid motion sampled at 0.2 mm slide / 0.5 degree rotation; not a continuous swept-volume proof.','Spring deformation is a geometric approximation, not FEA or measured force/fatigue. FDM tolerances and material strength need a physical trial.','Speaker contact is on the assumed rigid side frame; verify actual driver frame and vent layout before applying force.']}
(R/'reports/v07/acoustic_motion_v07.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2),flush=True);assert not fail
