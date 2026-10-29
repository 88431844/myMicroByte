from pathlib import Path
import FreeCAD as App, FreeCADGui as Gui
ROOT=Path(__file__).resolve().parents[1]
path=str(ROOT/'output/v02/myMicrobyte_enclosure_v02.FCStd')
doc=next((d for d in App.listDocuments().values() if d.FileName==path),None)
if doc is None:doc=App.openDocument(path)
App.setActiveDocument(doc.Name)
for o in doc.Objects:
    if o.ViewObject:o.ViewObject.Visibility=False
prints=[doc.RearShell_v02,doc.FrontShell_v02]+[o for o in doc.Objects if o.Name.startswith('Cap_')]
for o in prints:o.ViewObject.Visibility=True;o.ViewObject.ShapeColor=(0.13,0.135,0.14)
for o in doc.PCBReference.Group:o.ViewObject.Visibility=True;o.ViewObject.ShapeColor=(0.15,0.42,0.25)
doc.PCBReference.ViewObject.Visibility=True
doc.ConnectorKeepouts.ViewObject.Visibility=False
doc.LCD_Assumed_5mm.ViewObject.ShapeColor=(0.025,0.075,0.095)
doc.USB_Envelope.ViewObject.ShapeColor=(0.55,0.56,0.58)
doc.Battery_Assumed.ViewObject.ShapeColor=(0.65,0.67,0.71)
doc.Speaker_1510.ViewObject.ShapeColor=(0.35,0.36,0.38)
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
doc.recompute();doc.save()
