"""Unchanged full-driver candidate entry; output supplied only by replay guard."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
pins=json.loads((ROOT/'CODE-SOURCES.json').read_text())['files']
for name in ('full_C.py','archive_support.py'):
    if sha256((ROOT/name).read_bytes()).hexdigest()!=pins[name]:raise ValueError('entry source pin: '+name)
namespace=dict(__file__=str(ROOT/'archive_support.py'))
exec(compile((ROOT/'archive_support.py').read_bytes(),namespace['__file__'],'exec'),namespace)
namespace['full_entry']('C')
