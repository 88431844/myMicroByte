"""Slice the existing print-oriented STLs locally, without sending a printer job."""
from pathlib import Path
import subprocess, json, zipfile, os, sys, shutil
ROOT=Path(__file__).resolve().parents[1]
V02='--v02' in sys.argv
V03='--v03' in sys.argv
V04='--v04' in sys.argv
OUT=ROOT/('printing/A1_black_PLA_v04' if V04 else 'printing/A1_black_PLA_v03' if V03 else 'printing/A1_black_PLA_v02' if V02 else 'printing/A1_black_PLA')
MODEL_DIR=ROOT/('output/v04' if V04 else 'output/v03' if V03 else 'output/v02' if V02 else 'output')
OUT.mkdir(parents=True,exist_ok=True)
if V02 or V03 or V04:
 for name in ['machine.json','process.json','filament.json']:
  shutil.copy2(ROOT/'printing/A1_black_PLA'/name,OUT/name)
project_name='myMicrobyte_v04_A1_black_PLA_sliced.3mf' if V04 else 'myMicrobyte_v03_A1_black_PLA_sliced.3mf' if V03 else 'myMicrobyte_v02_A1_black_PLA_sliced.3mf' if V02 else 'myMicrobyte_A1_black_PLA_sliced.3mf'
models=[MODEL_DIR/'RearShell_print.stl',MODEL_DIR/'FrontShell_print.stl']+sorted(MODEL_DIR.glob('Cap_*_print.stl'))
if V03 or V04:models.append(MODEL_DIR/'PowerSlider_print.stl')
args=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--debug','2',
 '--load-settings',str(OUT/'machine.json')+';'+str(OUT/'process.json'),
 '--load-filaments',str(OUT/'filament.json'),'--load-defaultfila=1',
 '--arrange=1','--orient=0','--slice=0',
 '--export-3mf',project_name,
 '--outputdir',str(OUT),'--export-settings',str(OUT/'resolved_settings.json')]+[str(p) for p in models]
with (OUT/'slice.log').open('w') as log:
 result=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT)
print('Slicer exit:',result.returncode)
print((OUT/'slice.log').read_text()[-5000:])
if result.returncode == 0:
 # Bambu's CLI writes numeric overrides but leaves the preset-difference list
 # empty. Its GUI then restores system defaults when the project is opened.
 # Explicitly mark our project overrides so both entry points agree.
 project=OUT/project_name
 patched=project.with_suffix('.tmp.3mf')
 with zipfile.ZipFile(project) as src, zipfile.ZipFile(patched,'w',zipfile.ZIP_DEFLATED) as dst:
  for entry in src.infolist():
   data=src.read(entry.filename)
   if entry.filename=='Metadata/project_settings.config':
    settings=json.loads(data)
    settings['different_settings_to_system']=[
     'brim_type;brim_width;enable_support;sparse_infill_density;sparse_infill_pattern;support_on_build_plate_only;support_type;wall_loops',
     'filament_colour','']
    data=json.dumps(settings,ensure_ascii=False,indent=2).encode()
   dst.writestr(entry,data)
 os.replace(patched,project)
raise SystemExit(result.returncode)
