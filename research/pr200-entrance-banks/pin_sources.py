#!/usr/bin/env python3
"""Pin every source and finite input that verify.py reads. Apache-2.0."""
from hashlib import sha256
from pathlib import Path
import json

PKG = Path(__file__).resolve().parent
REPO = PKG.parents[1]
BIT = 'research/paired-cube-diagonal-bit-168/'
FILES = [BIT + name for name in (
    'bit/word.py', 'bit/base_word.py', 'bit/terminal.py',
    'references/pr168-v4/research/paired-cube-bit/check_paired_cube_bit.py',
    'selected/bit/graph_p12.json', 'selected/bit/profile_p12.json', 'selected/bit/word_p12.json.gz',
    'selected/bit/frames_p12.json.gz', 'selected/bit/kchron_p12.json', 'selected/bit/sinks.json',
    'arithmetic/interval_moment.py', 'certificate.json')] + [
    'research/source-assisted/global/assemble_profiles.py',
    'research/source-assisted/global/FINITE_BRIDGE.txt',
    'scripts/paired_cube_assembly.py',
    'research/source-assisted-v4/certificate.json',
]


def main():
    own = sorted(p.relative_to(REPO).as_posix() for p in PKG.rglob('*')
                 if p.is_file() and p.name not in ('SOURCE.json', 'certificate.json') and '__pycache__' not in p.parts)
    files = {name: sha256((REPO / name).read_bytes()).hexdigest() for name in sorted(set(FILES + own))}
    (PKG / 'SOURCE.json').write_text(json.dumps(dict(
        canonical_command='python3 -B research/pr200-entrance-banks/verify.py',
        base='PR202 at 8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d with the Linux-regenerated v4 certificate',
        files=files), indent=2, sort_keys=True) + '\n')
    print(len(files), 'files pinned')


if __name__ == '__main__':
    main()
