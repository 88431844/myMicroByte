import sys,json
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as A,Part
D=A.openDocument('output/v10/myMicrobyte_enclosure_v10.FCStd')
for g in [D.PCBReference,D.ConnectorKeepouts,D.Hardware_v10]:
 for o in g.Group:
  b=o.Shape.BoundBox
  print(o.Name,o.Label,[round(x,3) for x in [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]])
print('rear features',[(o.Name,o.Label) for o in D.Objects if 'Battery' in o.Name])
