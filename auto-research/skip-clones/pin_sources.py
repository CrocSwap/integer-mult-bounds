#!/usr/bin/env python3
"""Explicitly freeze reviewed sources and available finite inputs; never run by verification.

Prepared by Chafik Boukhalfa with OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run():
    names = set()
    for directory in ('copied-fixed', 'skip-strips'):
        path = ROOT/'research'/directory
        names.update(json.loads((path/'SOURCE.json').read_text())['files'])
        names.add(str((path/'SOURCE.json').relative_to(ROOT)))
        names.update(str(p.relative_to(ROOT)) for p in path.glob('*.py'))
    # Explicit native graph dependency closure, including the binary format.
    names.update(str(p.relative_to(ROOT)) for p in (ROOT/'scripts/partial_swap').glob('*.py'))
    names.update(str(p.relative_to(ROOT)) for p in (ROOT/'scripts/partial_swap').glob('*.hpp'))
    names.add('scripts/exclusion_circuit.py')
    for path in HERE.iterdir():
        if path.suffix in ('.py', '.cpp', '.uses', '.md', '.json') and path.name not in (
                'SOURCE.json', 'certificate.json', 'validation.json', 'producer-receipt.json'):
            names.add(str(path.relative_to(ROOT)))
    source = dict(
        base=dict(repository='CrocSwap/integer-mult-bounds', pull_request=53,
                  commit='3ffd4021995c959ac02d12920e0279ae97dd03c7',
                  author='Avi Eisenberg with Anthropic Claude Opus 5.5 assistance'),
        increment=dict(author='Chafik Boukhalfa with OpenAI Codex assistance',
                       construction='Paid original-envelope whole-chain clones on the PR53 skip-prefix graph family; clone idea credited to RaD / hipotures PR51 with OpenAI Codex assistance'),
        comparison_PR50=dict(author='Rohan Gupta (gupt1156) with Antigravity assistance',
                             commit='5581d15c', role='Contemporaneous benchmark only; no construction component imported'),
        scope='Explicit reviewed source/input freeze. Certificates and run receipts are derived outputs.',
        files={name: sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(names)})
    (HERE/'SOURCE.json').write_text(json.dumps(source, indent=2, sort_keys=True)+'\n')
    return len(names)


if __name__ == '__main__':
    print('Pinned', run(), 'sources and finite inputs')
