from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
import json,os
root=Path(__file__).resolve().parents[2]
directory=root/'output/assembly-guide-v10'
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(directory)))
(Path(__file__).parent/'preview-server.json').write_text(json.dumps({'pid':os.getpid(),'url':f'http://127.0.0.1:{server.server_address[1]}/','directory':str(directory)},ensure_ascii=False,indent=2))
server.serve_forever()
