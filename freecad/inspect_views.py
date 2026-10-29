from pathlib import Path
import FreeCAD as App, FreeCADGui as Gui
ROOT=Path('/Users/luckmiracle/Documents/ChatGPT/myMicroBye外壳设计')
d=App.ActiveDocument
for o in d.Objects:
 if o.ViewObject:o.ViewObject.Visibility=False
d.RearShell.ViewObject.Visibility=True
view=Gui.activeDocument().activeView();view.viewAxonometric();view.fitAll()
view.saveImage(str(ROOT/'reports/rear_inside.png'),1600,1000,'White')
d.RearShell.ViewObject.Visibility=False;d.FrontShell.ViewObject.Visibility=True
view.viewBottom();view.fitAll()
view.saveImage(str(ROOT/'reports/front_inside.png'),1600,1000,'White')
exec(compile((ROOT/'freecad/open_and_present.py').read_text(),'open_and_present.py','exec'))
