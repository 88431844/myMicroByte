from pathlib import Path
import json,zipfile,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'printing/A1_black_PLA_v04/myMicrobyte_v04_A1_black_PLA_sliced.3mf'
with zipfile.ZipFile(p) as z:
 settings=json.loads(z.read('Metadata/project_settings.config'));info=ET.fromstring(z.read('Metadata/slice_info.config'));plates=info.findall('plate');assert len(plates)==1
 plate=plates[0];meta={m.get('key'):m.get('value') for m in plate.findall('metadata')};objs=plate.findall('object');names=[o.get('name') for o in objs]
 assert set(names)=={'RearShell_print.stl','FrontShell_print.stl','PowerSlider_print.stl'} and all(o.get('skipped')=='false' for o in objs)
 assert meta['outside']=='false' and meta['nozzle_diameters']=='0.4';assert settings['printer_model']=='Bambu Lab A1' and settings['wall_loops']=='4'
 fila=plate.find('filament');assert fila.get('type')=='PLA' and fila.get('color')=='#171717'
 bbox=json.loads(z.read('Metadata/plate_1.json'))['bbox_all'];assert min(bbox)>=0 and max(bbox)<256
 for n in z.namelist():
  if n.endswith('.gcode'):assert hashlib.md5(z.read(n)).hexdigest().lower()==z.read(n+'.md5').decode().strip().lower()
 report=dict(status='validated',file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),printer=settings['printer_model'],nozzle_mm=.4,plate_count=1,objects=names,layer_height_mm=settings['layer_height'],walls=4,infill=settings['sparse_infill_density'],pattern=settings['sparse_infill_pattern'],support=settings['enable_support'],estimated_seconds=int(meta['prediction']),estimated_grams=float(meta['weight']),filament='black PLA',bed_type=settings['curr_bed_type'],plate_bbox_xy=bbox,job_sent=False)
 for n in ['Metadata/plate_1.png','Metadata/top_1.png']:
  if n in z.namelist():z.extract(n,ROOT/'reports/v04/slicer')
(ROOT/'reports/v04/print_project_validation_v04.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
