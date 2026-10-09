#!/usr/bin/env python3
"""Explicitly freeze reviewed inputs; ordinary verification never repins."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
files=list(HERE.glob('*.py'))+list(HERE.glob('*.md'))+[HERE/'selection.json',HERE/'ENGINE-PATCH.diff']
files += [HERE/f'{stem}-{h}.{ext}' for h in (23,25) for stem,ext in [('word','json.gz'),('profile','json'),('transitions','json')]]
files += [ROOT/f'references/frame-compiler/{pr}/SOURCE.json' for pr in ('pr69','pr71','pr82','pr84')]
files += [ROOT/'research/rank-pair-refinement/refine.py',ROOT/'research/balanced-split-frames/certificate.json',ROOT/'research/aligned-exchange-frames/certificate.json']
files += [ROOT/f'research/aligned-exchange-frames/{stem}-23.{ext}' for stem,ext in [('word','json.gz'),('profile','json'),('transitions','json')]]
manifest={'files':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))},
          'scope':'Root-relative source, complete derived-engine diff, selected words/profiles/transitions, and unchanged h23 baseline. Original archived manifests bind the inherited source closure. Receipts are checked outputs.'}
(HERE/'SOURCE.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
