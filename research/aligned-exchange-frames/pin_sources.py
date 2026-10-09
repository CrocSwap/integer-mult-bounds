#!/usr/bin/env python3
"""Record reviewed root-relative construction inputs; verification never repins."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
files=list(HERE.glob('*.py'))+list(HERE.glob('*.md'))+[HERE/'selection.json']
files += [HERE/f'{stem}-{h}.{ext}' for h in (23,25) for stem,ext in [('word','json.gz'),('profile','json'),('transitions','json')]]
files += [ROOT/f'references/frame-compiler/{pr}/SOURCE.json' for pr in ('pr69','pr71','pr82','pr84')]
files += [ROOT/'research/rank-pair-refinement/refine.py',ROOT/'research/balanced-split-frames/certificate.json']
manifest={'files':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)},'scope':'Root-relative selected code, proof, exact words and profiles; archived manifests bind original Git sources. Axis, graph and arithmetic receipts are checked outputs.'}
(HERE/'SOURCE.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
