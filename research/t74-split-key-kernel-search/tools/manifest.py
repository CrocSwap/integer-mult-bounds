"""Write MANIFEST.json: SHA-256 of every package file and of the external inputs the tools read.  usage: manifest.py"""
import hashlib, json
from pathlib import Path
PKG = Path(__file__).resolve().parents[1]; ROOT = PKG.parents[1]
PR1957 = 'research/t74-k554-local-exhaustion'
MAIN_INPUTS = [  # resolved from the repository by PR1957's vendored PR1186 toolkit (frames.py, model.py, writeback.py)
    'research/gauge44-frames-x/independent/audit_local.py',
    'research/frame-domain-ceiling/vendor/static44/gk/gk_word.py',
    'research/frame-domain-ceiling/vendor/static44/gk/gk_common.py',
    'research/frame-domain-ceiling/engines/moment.py',
    'research/frame-domain-ceiling/engines/base_two_moment.py']
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
files = {p.relative_to(PKG).as_posix(): sha(p) for p in sorted(PKG.rglob('*'))
         if p.is_file() and '__pycache__' not in p.parts and p.name != 'MANIFEST.json'}
inputs = {n: sha(ROOT / n) for n in [PR1957 + '/MANIFEST.json'] + MAIN_INPUTS}
(PKG / 'MANIFEST.json').write_text(json.dumps(dict(files=files, inputs=inputs, pr1957_manifest=PR1957 + '/MANIFEST.json'), indent=1) + '\n')
print('wrote MANIFEST.json', len(files), 'files', len(inputs), 'inputs')
