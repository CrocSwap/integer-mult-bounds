"""Portable exact orthogonal-restriction builder. Apache-2.0; AI assistance."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import sys, json, ast, gzip
import argparse, hashlib
_parser = argparse.ArgumentParser()
_parser.add_argument('--source-root', required=True, type=Path)
_args = _parser.parse_args()
H = Path(__file__).resolve().parent
R = _args.source_root.resolve()
_manifest = json.loads((H / 'SOURCE-CLOSURE-ROUND3.json').read_text(encoding='utf-8'))
for _row in _manifest['files']:
    if not hashlib.sha256((R / _row['path']).read_bytes()).hexdigest() == _row['sha256']:
        raise ValueError('Changed source: ' + _row['path'])
for _name, _hash in _manifest['owned_modules'].items():
    if not hashlib.sha256((H / _name).read_bytes()).hexdigest() == _hash:
        raise ValueError('Changed owned module: ' + _name)
sys.path.insert(0, str(H))
from synthesis import synthesize as _resynthesize
sys.path.insert(0, str(R / 'research/joint-helper-lattice'))
import native_joint as J
F = J.F
_raw=gzip.decompress((H/'BASE-ROUND3-WORD.json.gz').read_bytes())
if hashlib.sha256(_raw).hexdigest()!=_manifest['base_actual_word_payload_sha256']:
    raise ValueError('Changed round-three source word')
_z=json.loads(_raw)
c,p=_z['canonical'],_z['programs']
h = 153
oldframes = c['frames']
frames = [[], [1 << i for i in range(9)]]
labels = {frozenset({0}): 0, F.span(frames[1]): 1}
remap = {}

def basis(s):
    b = []
    cur = {0}
    for x in sorted(s):
        if x not in cur:
            b.append(x)
            cur |= {v ^ x for v in tuple(cur)}
    return b
for i, b in enumerate(oldframes):
    sp = frozenset((x for x in F.span(b) if (x & h).bit_count() % 2 == 0))
    if sp not in labels:
        labels[sp] = len(frames)
        frames.append(basis(sp))
    remap[i] = labels[sp]
cc = deepcopy(c)
cc['frames'] = frames
cc['start'] = [remap[x] for x in c['start']]
cc['final'] = [remap[x] for x in c['final']]
pp = {}
for d, word in p.items():
    out = []
    for e in deepcopy(word):
        if e[0] == 'climb':
            continue
        if e[0] == 'scalar':
            e[2] = remap[e[2]]
        elif e[0] == 'warp':
            e[3:5] = [remap[e[3]], remap[e[4]]]
        elif e[0] == 'center':
            e[2:4] = [remap[e[2]], remap[e[3]]]
            e[4] = abs(len(frames[e[2]]) - len(frames[e[3]]))
        out.append(e)
    pp[d] = out
pp = {d: _resynthesize(F, cc, p) for d, p in pp.items()}
profiles = {}
for d, p in pp.items():
    P = Counter((e[5] for e in p if e[0] == 'climb'))
    P.update((e[4] for e in p if e[0] == 'center'))
    P.update((abs(len(frames[e[3]]) - len(frames[e[4]])) for e in p if e[0] == 'warp'))
    P.pop(0, None)
    profiles[d] = dict(P)
if not profiles['forward'] == profiles['backward']:
    raise ValueError('Exact check failed at original source line 44')
HH = Counter((len(frames[b]) - len(frames[a]) for a, b in zip(cc['start'][224:], cc['final'][224:])))
if not min(HH) > 0:
    raise ValueError('Exact check failed at original source line 44')
out = dict(normal=h, frames=len(frames), paid=profiles['forward'], helpers=dict(HH), local_deficit=sum((k * n for k, n in profiles['forward'].items())) - sum((k * n for k, n in HH.items())), main_ranks=dict(Counter((len(frames[b]) - len(frames[a]) for a, b in zip(cc['start'][:224], cc['final'][:224])))), status='MINIMUM_WARP_RANK_PROFILE_PENDING_SHARED_MAP_ADMISSION')
(H / 'INTERSECTION153-ROUND3-MIN-PROFILE.json').write_text(json.dumps(out, indent=2))
(H / 'INTERSECTION153-ROUND3-DISCOVERY-WORD.json').write_text(json.dumps(dict(canonical=cc, programs=pp)))
print(json.dumps(out, indent=2))
