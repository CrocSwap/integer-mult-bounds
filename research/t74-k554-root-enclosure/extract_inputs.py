#!/usr/bin/env python3
"""Rebuild INPUTS.json from the two pinned PR heads (needs a fetched pull ref).

    git fetch origin pull/1672/head pull/1928/head
    python3 research/t74-k554-root-enclosure/extract_inputs.py [--check]

Reads only data fields of each package's new/SPEC.json. Imports nothing from
either package. Aaron Wang, with help from opencode. Apache-2.0.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = {
    'pr1672': dict(pr=1672, head='b8ab040dbb7638e79249e763c60e877765d9d3b7',
                   path='research/gmx-t74-k554-signed-001/new/SPEC.json', grid_digits=70,
                   kappa=('research/gmx-t74-k554-signed-001/new/SPEC.json', ('expected', 'kappa'))),
    'pr1928': dict(pr=1928, head='07e4e4231459e36b1055396306dcbd950248df62',
                   path='research/capped-fusion-t74-k554/new/SPEC.json', grid_digits=10000,
                   kappa=('research/capped-fusion-t74-k554/outer/OUTER-CLAIM.json', ('kappa_rational',))),
}


def git(*args):
    return subprocess.run(['git', *args], check=True, capture_output=True, cwd=HERE).stdout


def build():
    out = dict(schema_version=1, m=73, sources={})
    for key, src in SOURCES.items():
        raw = git('show', src['head'] + ':' + src['path'])
        spec = json.loads(raw)
        exp = spec['expected']
        kpath, kkeys = src['kappa']
        kraw = git('show', src['head'] + ':' + kpath)
        kappa = json.loads(kraw)
        for k in kkeys:
            kappa = kappa[k]
        out['sources'][key] = dict(
            headline_kappa=kappa, headline_kappa_path=kpath, headline_kappa_field='/'.join(kkeys),
            headline_kappa_git_blob=git('rev-parse', src['head'] + ':' + kpath).decode().strip(),
            headline_kappa_file_sha256=hashlib.sha256(kraw).hexdigest(),
            pr=src['pr'], url='https://github.com/CrocSwap/integer-mult-bounds/pull/%d' % src['pr'],
            head=src['head'], path=src['path'],
            git_blob=git('rev-parse', src['head'] + ':' + src['path']).decode().strip(),
            sha256=hashlib.sha256(raw).hexdigest(), grid_digits=src['grid_digits'],
            live=exp['live'], rank_mass=exp['rank_mass'], global_profile=exp['global_profile'],
            idle_remainder_profile=exp['idle_remainder_profile'], provider_counts=exp['provider_counts'],
            provider_profiles={p: v['expected_profile'] for p, v in spec['providers'].items()},
            complex_lower=exp['complex_lower'], conservative_complex_lower=exp['conservative_complex_lower'])
    return json.dumps(out, indent=1, sort_keys=True) + '\n'


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='compare with the committed INPUTS.json instead of writing')
    a = ap.parse_args()
    text = build()
    if a.check:
        assert (HERE / 'INPUTS.json').read_text(encoding='utf-8') == text, 'INPUTS.json differs from the pinned PR heads'
        print('PASS_INPUTS_MATCH_PINNED_PR_HEADS')
    else:
        (HERE / 'INPUTS.json').write_text(text, encoding='utf-8', newline='\n')
        print('wrote INPUTS.json')
