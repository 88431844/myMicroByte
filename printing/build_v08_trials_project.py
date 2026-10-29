from pathlib import Path
import subprocess,json,zipfile,os,shutil
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'printing/A1_black_PLA_v08_trials'
report=json.loads((ROOT/'reports/v08_trials/trial_geometry_validation.json').read_text());assert not report['collisions']
ids=['F1','F2','F3','F4','R1','R2','S1','S2','S3','L1','L2'];models=[]
for code in ids:
 p=OUT/(code+'_print.stl');shutil.copy2(ROOT/'output/v08_trials'/p.name,p);models.append(p)
args=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--debug','2','--load-settings',str(OUT/'machine.json')+';'+str(OUT/'process.json'),'--load-filaments',str(OUT/'filament.json'),'--load-defaultfila=1','--arrange=1','--orient=0','--slice=0','--export-3mf','myMicrobyte_v08_trials_black.3mf','--outputdir',str(OUT),'--export-settings',str(OUT/'resolved_settings.json')]+[str(p) for p in models]
(OUT/'command.json').write_text(json.dumps(args,ensure_ascii=False,indent=2))
with (OUT/'slice.log').open('w') as log:r=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT)
print('Slicer exit',r.returncode,flush=True);print((OUT/'slice.log').read_text()[-5000:],flush=True)
assert r.returncode==0
project=OUT/'myMicrobyte_v08_trials_black.3mf';temp=OUT/'project_patched.3mf'
# Preserve all our process settings when Bambu GUI resolves the system preset.
process=json.loads((OUT/'process.json').read_text());keys=sorted(k for k in process if k not in ['name','type','from','instantiation','setting_id','description','compatible_printers'])
with zipfile.ZipFile(project) as src,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as dst:
 for entry in src.infolist():
  data=src.read(entry.filename)
  if entry.filename=='Metadata/project_settings.config':
   s=json.loads(data);s['different_settings_to_system']=[';'.join(keys),'filament_colour',''];data=json.dumps(s,ensure_ascii=False,indent=2).encode()
  dst.writestr(entry,data)
os.replace(temp,project)
print('Project ready',project,flush=True)
