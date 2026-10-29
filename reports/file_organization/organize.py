from pathlib import Path
import re,hashlib,json,shutil
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[2]
records=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def move(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():raise RuntimeError(f'Destination already exists: {dest}')
 digest=sha(src);size=src.stat().st_size
 shutil.move(str(src),str(dest))
 assert sha(dest)==digest and not src.exists()
 records.append(dict(source=str(src),destination=str(dest.relative_to(ROOT)),bytes=size,sha256=digest))
for base in [Path.home()/'Downloads',Path.home()/'Desktop']:
 for src in sorted(base.iterdir()):
  match=re.fullmatch(r'myMicrobyte-(v\d+)-(装配视图(?: \(\d+\))?\.png|装配调整(?: \(\d+\))?\.json)',src.name)
  if src.is_file() and match:
   move(src,ROOT/'reports/assembly_exports'/match[1]/src.name)
old=Path('/Users/luckmiracle/.codex/visualizations/2026/10/14/01a13a7f-6902-7111-8be9-d1a9fbe6a612/microbyte-v03-assembly.html')
new=ROOT/'output/assembly-guide-v03-legacy/index.html'
move(old,new)
# Preserve already shared external preview links; all actual contents live inside this project.
old.symlink_to(new)
updated=[]
for p in ROOT.rglob('*'):
 if not p.is_file() or p.suffix not in {'.json','.py','.md','.html','.js'} or '.git' in p.parts or p==Path(__file__).resolve():continue
 try:s=p.read_text()
 except (UnicodeError,OSError):continue
 if str(old) in s:
  p.write_text(s.replace(str(old),str(new)));updated.append(str(p.relative_to(ROOT)))
manifest={'date':'2026-10-22','moved_files':records,'updated_references':updated,'legacy_link':{'path':str(old),'target':str(new)},'verification':'SHA-256 verified for every moved file; originals removed except compatibility symlink'}
(ROOT/'reports/file_organization/move_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Moved:',len(records),'files;',sum(r['bytes'] for r in records),'bytes')
print('By type:',{ext:sum(Path(r['destination']).suffix==ext for r in records) for ext in ['.png','.json','.html']})
print('Updated:',updated)
# Unified local file index, using relative links so the project folder remains portable.
sections={
 '外壳模型与交换文件':[], 'STL 打印模型':[], '拓竹打印工程与切片':[],
 '3D 交互装配与爆炸图页面':[], '图片与对比图':[], '说明、校核与参数文件':[]}
for p in sorted(ROOT.rglob('*')):
 if not p.is_file() or any(x in p.parts for x in ['.git','__pycache__','file_organization']) or p.name.startswith('.'):continue
 rel=p.relative_to(ROOT);ext=p.suffix.lower()
 if rel.parts[0] not in {'output','reports','printing','reference'}:continue
 if ext in {'.fcstd','.step','.stp','.f3d','.f3z'}:key='外壳模型与交换文件'
 elif ext=='.stl':key='STL 打印模型'
 elif ext=='.3mf':key='拓竹打印工程与切片'
 elif ext=='.html' and p.name=='index.html':key='3D 交互装配与爆炸图页面'
 elif ext in {'.png','.jpg','.jpeg','.webp','.svg','.pdf'}:key='图片与对比图'
 elif ext in {'.md','.json','.csv','.xlsx'} and 'vendor' not in rel.parts and p.stat().st_size<500000:key='说明、校核与参数文件'
 else:continue
 sections[key].append(rel)
lines=['# 项目文件索引','', '整理日期：2026-10-22。以下均为项目目录内文件，按类型和版本路径排列。','', '新增移入的装配视图在 `reports/assembly_exports/`，早期在线依赖预览在 `output/assembly-guide-v03-legacy/`。新版交互页面含内嵌模型与脚本。','']
for key,paths in sections.items():
 lines += [f'## {key}（{len(paths)}）','']
 lines += [f'- [{p.as_posix()}]({quote(p.as_posix(),safe="/")})' for p in paths]
 lines.append('')
(ROOT/'项目文件索引.md').write_text('\n'.join(lines))
print('Index counts:',{k:len(v) for k,v in sections.items()})
