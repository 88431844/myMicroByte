"""Build one portable, offline HTML page with actual v0.7 CAD meshes."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
template = (ROOT/'src/page.html').read_text()
orbit = (ROOT/'vendor/OrbitControls.js').read_text()
orbit = re.sub(r"import\s*\{(.*?)\}\s*from 'three';", r'const {\1} = THREE;', orbit, flags=re.S)
orbit = orbit.replace('export { OrbitControls };', '')
parts = {'/* INLINE_STYLE */': (ROOT/'src/style.css').read_text(),
         'INLINE_GEOMETRY': (PROJECT/'reports/v07/preview_meshes.b64').read_text().strip(),
         '/* INLINE_THREE */': (ROOT/'vendor/three.min.js').read_text(),
         '/* INLINE_ORBIT */': orbit,
         '/* INLINE_APP */': (ROOT/'src/app.js').read_text()}
for marker, value in parts.items():
    assert template.count(marker) == 1, marker
    template = template.replace(marker, value)
(ROOT/'index.html').write_text(template)
print('Built', ROOT/'index.html', len(template.encode()), 'bytes')
