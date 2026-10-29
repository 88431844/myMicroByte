from pathlib import Path
import FreeCAD as App, FreeCADGui as Gui
ROOT=Path('/Users/luckmiracle/Documents/ChatGPT/myMicroBye外壳设计')
file=ROOT/'output/myMicrobyte_enclosure_v01.FCStd'
d=next((o for o in App.listDocuments().values() if o.FileName==str(file)),None)
if d is None:d=App.openDocument(str(file))
App.setActiveDocument(d.Name)
for o in d.Objects:
 if o.ViewObject:o.ViewObject.Visibility=False
for name in ['RearShell','FrontShell']:
 o=d.getObject(name);o.ViewObject.Visibility=True;o.ViewObject.ShapeColor=(0.16,0.23,0.31);o.ViewObject.LineColor=(0.08,0.12,0.16)
for o in d.Objects:
 if o.Name.startswith('Cap_'):
  o.ViewObject.Visibility=True;o.ViewObject.ShapeColor=(0.95,0.45,0.16)
g=d.getObject('PCBReference');g.ViewObject.Visibility=True
for o in g.Group:
 o.ViewObject.Visibility=True;o.ViewObject.ShapeColor=(0.18,0.58,0.30)
d.LCD_Assumed_5mm.ViewObject.ShapeColor=(0.04,0.10,0.16)
d.Battery_Assumed.ViewObject.ShapeColor=(0.6,0.6,0.65)
d.Battery_Assumed.ViewObject.Transparency=70
d.USB_Envelope.ViewObject.ShapeColor=(0.7,0.7,0.75)
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
d.recompute();d.save()
Gui.activeDocument().activeView().saveImage(str(ROOT/'reports/assembly.png'),1600,1000,'White')
