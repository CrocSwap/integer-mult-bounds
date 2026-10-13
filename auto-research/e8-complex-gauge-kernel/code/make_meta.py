"""Write SOURCE.json (inventories of the upstream packages this package runs) and MANIFEST.json (this package's files).  Apache-2.0.
usage: python -B research/e8-complex-gauge-kernel/code/make_meta.py"""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; R = ROOT.parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory(p): return {f.relative_to(p).as_posix(): sha(f) for f in sorted(Path(p).rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
packages = ['idle-axis-hosting', 'split-centres-global', 'e8-early-reset-kernel', 'e8-early-reset-reuse']
(ROOT / 'SOURCE.json').write_text(json.dumps(dict(note='inventories of the packages of PR #442 and its parents that verify.py runs unchanged', packages={p: dict(files=inventory(R / p)) for p in packages}), indent=1, sort_keys=True) + '\n')
inv = inventory(ROOT); inv.pop('MANIFEST.json', None)
(ROOT / 'MANIFEST.json').write_text(json.dumps(dict(files=inv), indent=1, sort_keys=True) + '\n')
print('SOURCE.json and MANIFEST.json written;', len(inv), 'files')
