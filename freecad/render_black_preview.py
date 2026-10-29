from pathlib import Path
import FreeCAD as App, FreeCADGui as Gui
ROOT=Path('/Users/luckmiracle/Documents/ChatGPT/myMicroBye外壳设计')
source=next((d for d in App.listDocuments().values() if d.FileName==str(ROOT/'output/myMicrobyte_enclosure_v01.FCStd')),None)
if source is None:source=App.openDocument(str(ROOT/'output/myMicrobyte_enclosure_v01.FCStd'))
preview=App.newDocument('myMicrobyte_Black_PLA_Preview')
assembled=preview.addObject('App::DocumentObjectGroup','Assembled')
assembled.Label='黑色 PLA 装配外观'
exploded=preview.addObject('App::DocumentObjectGroup','Exploded')
exploded.Label='分解装配（屏幕、电池含假定占位）'
def copy(o,group,offset,color):
 f=preview.addObject('Part::Feature','Preview_'+o.Name)
 f.Label=o.Label;f.Shape=o.Shape.copy();f.Placement.Base.z+=offset
 group.addObject(f);f.ViewObject.ShapeColor=color;f.ViewObject.LineColor=(0.24,0.24,0.25)
 f.ViewObject.DisplayMode='Flat Lines'
 return f
black=(0.13,0.135,0.14)
parts=[source.RearShell,source.FrontShell]+[o for o in source.Objects if o.Name.startswith('Cap_')]
for o in parts:copy(o,assembled,0,black)
copy(source.LCD_Assumed_5mm,assembled,0,(0.025,0.075,0.095))
copy(source.USB_Envelope,assembled,0,(0.55,0.56,0.58))
for o in parts:
 offset=0 if o==source.RearShell else (32 if o==source.FrontShell else 40)
 copy(o,exploded,offset,black)
for o in source.PCBReference.Group:
 color=(0.15,0.42,0.25)
 offset=15
 if o==source.Battery_Assumed:color=(0.60,0.60,0.63);offset=1
 elif o==source.LCD_Assumed_5mm:color=(0.025,0.075,0.095);offset=15
 elif o==source.USB_Envelope:color=(0.55,0.56,0.58)
 copy(o,exploded,offset,color)
for o in exploded.Group:o.ViewObject.Visibility=False
exploded.ViewObject.Visibility=False
assembled.ViewObject.Visibility=True
preview.recompute()
view=Gui.activeDocument().activeView();view.viewAxonometric();view.fitAll();Gui.updateGui()
preview.saveAs(str(ROOT/'output/myMicrobyte_blackPLA_preview.FCStd'))
view.saveImage(str(ROOT/'reports/blackPLA_assembly.png'),1800,1200,'White')
