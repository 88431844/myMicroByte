"""Read-only layout study; does not replace the v0.5 enclosure."""
from pathlib import Path
import sys,json,math
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];d=A.openDocument(str(R/'output/v05/myMicrobyte_enclosure_v05.FCStd'))
def rr(w,h,r,z,t,cx,cy):
 s=Part.makeBox(w-2*r,h,t,A.Vector(cx-w/2+r,cy-h/2,z)).fuse(Part.makeBox(w,h-2*r,t,A.Vector(cx-w/2,cy-h/2+r,z)))
 for x in [-1,1]:
  for y in [-1,1]:s=s.fuse(Part.makeCylinder(r,t,A.Vector(cx+x*(w/2-r),cy+y*(h/2-r),z)))
 return s.removeSplitter()
def cap(w,l,z,h,cx,cy):
 return Part.makeBox(w,l-w,h,A.Vector(cx-w/2,cy-(l-w)/2,z)).fuse(Part.makeCylinder(w/2,h,A.Vector(cx,cy-(l-w)/2,z))).fuse(Part.makeCylinder(w/2,h,A.Vector(cx,cy+(l-w)/2,z))).removeSplitter()
cx=30.4;cy=-1.5
outer=rr(13.2,20.1,1.8,1.4,5.6,cx,-2.65)
void=rr(11.2,18.1,.8,1.4,4.8,cx,-2.65)
walls=outer.cut(void).removeSplitter()
sp=cap(10,15,2.1,3.5,cx,cy);spmax=cap(10.2,15.2,2.1,3.9,cx,cy)
tab=Part.makeBox(3,2.5,1,A.Vector(cx-1.5,cy-10,2.1))
frontair=cap(8,13,1.4,.7,cx,cy)
seat=cap(10.8,15.8,1.4,.4,cx,cy).cut(cap(8,13,1.3,.6,cx,cy))
# Air volume counts the installed speaker as solid and subtracts the front sound path.
air=void.cut(sp).cut(tab).cut(frontair).cut(seat).removeSplitter()
obs=[o for o in list(d.PCBReference.Group)+list(d.ConnectorKeepouts.Group) if not o.Name.startswith('Speaker_')]
obs += [d.PowerSlider_v05,d.FrontShell_v05]
# The old speaker mount/grille would be rebuilt, so exclude it but check other rear features.
for n in ['BatteryCableExit','RearPost0','RearPost1','RearPost2','RearPost3','ChargeLEDLightHole']:
 o=d.getObject(n)
 if o:obs.append(o)
conflicts=[];gaps=[]
for obj in obs:
 for name,s in [('chamber',walls),('speaker_max',spmax),('speaker_tab',tab)]:
  if s.BoundBox.intersect(obj.Shape.BoundBox):
   v=s.common(obj.Shape).Volume
   if v>.001:conflicts.append(dict(candidate=name,obstacle=obj.Name,mm3=v))
  if name=='chamber':
   dist=s.distToShape(obj.Shape)[0]
   if dist<2:gaps.append(dict(obstacle=obj.Name,clearance_mm=dist))
# Clip proposed slots to the existing unobstructed seat aperture.
slots=[]
for dy in [-4.4,-2.2,0,2.2,4.4]:slots.append(Part.makeBox(7,1.2,1,A.Vector(cx-3.5,cy+dy-.6,0)))
vents=slots[0]
for s in slots[1:]:vents=vents.fuse(s)
vents=vents.common(cap(8,13,0,1,cx,cy))
report={'status':'layout feasibility only; not acoustic validation or ready-to-print design','speaker_image':'1510, 15x10x3.5 mm, 8 ohm, 1 W; appears to be bare driver, not a complete boxed module','candidate_shift_from_v05_mm':[-1.6,-.5,0],'chamber_outer_mm':[13.2,20.1,5.6],'chamber_wall_mm':1.,'lid_mm':.8,'top_z_mm':7.,'free_rear_air_volume_nominal_cm3':air.Volume/1000,'current_grille_open_area_mm2':30.,'candidate_grille_open_area_mm2':vents.Volume,'nearby_clearances':gaps,'conflicts':conflicts,'limitations':['Speaker rear vent layout, fs, Vas, Qts and acoustic measurements are unavailable. No predicted SPL gain or tuned port claim.','Requires continuous front perimeter seal and sealed wire exit. Volume excludes front plenum but is approximate because speaker reference is a solid envelope.','Small sealed volume may raise resonance and reduce bass; removable lid allows A/B evaluation.','This study relocates the speaker slightly and replaces its old mount/grille; existing v0.5 is not edited.']}
(R/'reports/acoustic-study/feasibility.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
