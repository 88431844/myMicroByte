from pathlib import Path
import json,zipfile,hashlib,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];d=ROOT/'printing/A1_black_green_blue_PLA_v07';p=d/'myMicrobyte_v07_A1_black_green_blue.gcode.3mf'
expected=dict(json.loads((d/'objects.json').read_text()))
with zipfile.ZipFile(p) as z:
 s=json.loads(z.read('Metadata/project_settings.config'));si=ET.fromstring(z.read('Metadata/slice_info.config'));plates=si.findall('plate');assert len(plates)==1
 plate=plates[0];meta={m.get('key'):m.get('value') for m in plate.findall('metadata')};objs=plate.findall('object');names=[o.get('name') for o in objs]
 assert set(names)==set(expected) and len(names)==9 and all(o.get('skipped')=='false' for o in objs)
 assert meta['outside']=='false' and meta['nozzle_diameters']=='0.4'
 assert s['printer_model']=='Bambu Lab A1' and s['layer_height']=='0.16' and s['wall_generator']=='arachne'
 assert s['support_on_build_plate_only']=='1' and s['wall_loops']=='4'
 filaments=[dict(f.attrib) for f in plate.findall('filament')]
 assert [f['type'] for f in filaments]==['PLA']*3
 assert [f['color'] for f in filaments]==['#171717','#25B84A','#2459C4']
 source_project=d/'myMicrobyte_v07_A1_black_green_blue.3mf'
 with zipfile.ZipFile(source_project) as zp: model=ET.fromstring(zp.read('Metadata/model_settings.config'))
 assignments={}
 for o in model.findall('object'):
  m={m.get('key'):m.get('value') for m in o.findall('metadata') if m.get('key')}
  assignments[m['name']]=int(m['extruder'])
 assert assignments==expected
 bbox=json.loads(z.read('Metadata/plate_1.json'))['bbox_all'];assert min(bbox)>=0 and max(bbox)<256
 g=z.read('Metadata/plate_1.gcode')
 id_names={int(o.get('identify_id')):o.get('name') for o in objs}
 active=None;tool=0;feature='';actual={n:set() for n in names}
 for line in g.decode().splitlines():
  if line.startswith('; start printing object'): active=id_names[int(line.rsplit(':',1)[1])]
  elif line.startswith('; stop printing object'): active=None
  elif line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
  elif re.fullmatch(r'T[012]',line):tool=int(line[1:])
  elif active and feature in ('Outer wall','Inner wall','Top surface','Bottom surface') and re.match(r'G[123] ',line) and re.search(r'E[0-9.]',line):actual[active].add(tool+1)
 assert actual=={n:{i} for n,i in expected.items()},actual
 assert hashlib.md5(g).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
 for name in expected:
  source=ROOT/'output/v07'/('PowerSlider_print.stl' if name.startswith('PowerSlider_') else name)
  assert (d/name).read_bytes()==source.read_bytes()
 report=dict(status='validated',file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),printer=s['printer_model'],nozzle_mm=.4,plate_count=1,objects=assignments,layer_height_mm=.16,wall_generator=s['wall_generator'],walls=4,infill=s['sparse_infill_density'],filaments=filaments,estimated_seconds=int(meta['prediction']),estimated_grams=float(meta['weight']),bed_type=s['curr_bed_type'],plate_bbox_xy=bbox,ams_mapping_required={'1_black':'A4','2_green':'A2','3_blue':'A1'},camera_bed_empty=True,toolpath_review='Acoustic springs and latches retain independent paths. Four support segments in wider review crop belong to adjacent corner boss, outside acoustic wall.',job_sent=False)
(ROOT/'reports/v07/print_project_validation_v07.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
