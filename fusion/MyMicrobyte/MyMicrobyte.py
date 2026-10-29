import adsk.core, adsk.fusion, traceback, json
from pathlib import Path
ROOT=Path('/Users/luckmiracle/Documents/ChatGPT/myMicroBye外壳设计')
def run(context):
 app=adsk.core.Application.get()
 try:
  src=ROOT/'reference/pcb-current.step'
  if not src.exists(): raise RuntimeError('Waiting for current PCB STEP export')
  opts=app.importManager.createSTEPImportOptions(str(src))
  doc=app.importManager.importToNewDocument(opts)
  design=adsk.fusion.Design.cast(app.activeProduct)
  records=[]
  for o in design.rootComponent.allOccurrences:
   for b in o.bRepBodies:
    bb=b.boundingBox
    records.append({'component':o.component.name,'body':b.name,'solid':b.isSolid,'volumeMm3':b.volume*1000,'bounds':[[bb.minPoint.x*10,bb.minPoint.y*10,bb.minPoint.z*10],[bb.maxPoint.x*10,bb.maxPoint.y*10,bb.maxPoint.z*10]]})
  for b in design.rootComponent.bRepBodies:
   bb=b.boundingBox;records.append({'component':'root','body':b.name,'solid':b.isSolid,'bounds':[[bb.minPoint.x*10,bb.minPoint.y*10,bb.minPoint.z*10],[bb.maxPoint.x*10,bb.maxPoint.y*10,bb.maxPoint.z*10]]})
  (ROOT/'reports/pcb-step-audit.json').write_text(json.dumps(records,indent=2,ensure_ascii=False))
  app.activeViewport.fit()
  app.activeViewport.saveAsImageFile(str(ROOT/'reports/pcb-import.png'),1600,1000)
 except:
  (ROOT/'reports/fusion-error.txt').write_text(traceback.format_exc())
  app.userInterface.messageBox(traceback.format_exc(),'myMicrobyte')
