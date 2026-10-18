#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""Compose the shortest recorded R439 phase-B block programs with the helper-star D line.

composition  = main's PR967 helper-star word (11,783 ADDs) with nine PR1015 multi-write block
               programs and the incorporated PR923 frame-520 program spliced into B, and the
               literal cleanup C rebuilt.  D is unchanged.
candidate    = the unchanged seed-19 helper-star search (main's research/r439-helper-stars-seed19/
               build.py, called as a library) rerun on the same PR915 target-compensation parent
               after the same B splice.  Smaller block transfers relax the precision guard, so the
               identical gain-ordered pass admits stars it previously rejected.
pair_control = the same rerun restricted to disjoint pairs (degree one).

Deterministic; standard library only.
"""
import argparse, copy, gzip, hashlib, json, runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STARS = 'research/r439-helper-stars-seed19/'
PARENT = 'research/r439-target-compensation/candidate.json.gz'
F520 = 'research/r439-frame520/candidate.json'
PR1015 = HERE / 'inputs/PR1015-CANDIDATE.json'
# frame -> (first, stop) slice of B in the PR589 word; identical in every word of this line
BLOCKS = {506: (102, 128), 507: (128, 163), 519: (163, 205), 508: (205, 242), 520: (242, 283),
          509: (283, 314), 521: (314, 361), 522: (361, 404), 523: (404, 449), 524: (449, 490)}


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def load(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def pins(root):
    manifest = load(HERE / 'SOURCES.json')
    for path, sha in manifest['files'].items():
        p = (HERE / path) if path.startswith('inputs/') else (root / path)
        need(hashlib.sha256(p.read_bytes()).hexdigest() == sha, 'source pin: ' + path)
    return manifest


def programs(root):
    """Ten replacement block programs: PR1015 for nine frames, PR923 for frame 520."""
    cand = load(PR1015)
    out = {}
    for b in cand['blocks']:
        need(tuple(b['slice']) == BLOCKS[b['frame']], 'PR1015 slice %d' % b['frame'])
        out[b['frame']] = dict(source='PR1015', gates=b['gates'])
    f520 = load(root / F520)
    need(f520['frame'] == 520 and f520['candidate_gate_count'] == len(f520['candidate_ops']) == 29, 'PR923 frame 520')
    out[520] = dict(source='PR923', gates=f520['candidate_ops'])
    need(sorted(out) == sorted(BLOCKS), 'block inventory')
    return out


def cleanup(w):
    full = next(i for i, f in enumerate(w['frames']) if len(f) == w['v'])
    return [[full, d, list(ss)] for _, d, ss in reversed(w['A'] + w['B']) if d < w['v'] or d >= 2 * w['v']]


def splice(word, progs):
    w = copy.deepcopy(word)
    for frame in sorted(BLOCKS, key=lambda f: -BLOCKS[f][0]):
        a, b = BLOCKS[frame]
        w['B'][a:b] = copy.deepcopy(progs[frame]['gates'])
    w['C'] = cleanup(w)
    return w


def build(root):
    stars = runpy.run_path(str(root / STARS / 'build.py'))
    progs = programs(root)
    composition = splice(load(root / STARS / 'candidate.json.gz'), progs)
    parent = splice(load(root / PARENT), progs)
    candidate, cert = stars['search'](parent, 2)
    pair, pair_cert = stars['search'](parent, 1)
    for c in (cert, pair_cert):
        c['parent_note'] = 'PR915 target-compensation parent with the ten spliced B blocks and rebuilt C'
    return dict(composition=composition, candidate=candidate, pair_control=pair,
                candidate_search=cert, pair_control_search=pair_cert)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    pins(ROOT)
    out = build(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    for name in ('composition', 'candidate', 'pair_control'):
        (a.output / (name + '.json.gz')).write_bytes(gzip.compress(canonical(out[name]), mtime=0))
    for name in ('candidate_search', 'pair_control_search'):
        (a.output / (name + '.json')).write_text(json.dumps(out[name], indent=1, sort_keys=True) + '\n')
    print({k: out[k + '_search']['native_ADDs'] for k in ('candidate', 'pair_control')})
