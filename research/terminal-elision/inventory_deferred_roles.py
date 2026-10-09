#!/usr/bin/env python3
"""Read-only structural elimination inventory of an exported deferred word.

No word is changed. Terminal candidates additionally require all current
target readout frames to fit their earliest replaced gate frame.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
from frame_extension import basis, contains


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--word', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    w = json.loads(gzip.decompress(a.word.read_bytes()))
    frames = {int(k): v for k, v in w['frames'].items()}
    sigma = {int(k): v for k, v in w['sigma'].items()}
    leaves = {int(k): v for k, v in w['leaf_of'].items()}
    roots = {int(k): v for k, v in w['role_root'].items()}
    dest, source = [Counter() for _ in range(2)]
    gate_frames = [[] for _ in range(w['R'])]
    for op in w['ops']:
        if op[0] == 'add':
            dst, src = op[1], op[2]
        elif op[0] == 'copy':
            src, dst = op[1], op[2]
        else:
            continue
        dest[dst] += 1
        source[src] += 1
        gate_frames[dst].append(frames[op[3]])
    bytarget = [[] for _ in range(w['v'])]
    for s in w['deferred']:
        for t in w['reach'][s]:
            bytarget[t].append(sigma[s])
    pure = []
    terminal = []
    terminal_blocked = Counter()
    for s in range(w['R']):
        if s in leaves and dest[s] == 0 and s in sigma:
            assert basis(sigma[s]) == basis(frames[w['first_node'][s]])
            assert w['adjoint_centre'][s] is None
            pure.append(s)
        if s not in roots or w['kind'][roots[s]] or source[s]:
            continue
        if s not in sigma:
            terminal_blocked['not_deferred'] += 1
            continue
        t = w['target'][roots[s]]
        birth_frame = frames[w['first_node'][s]]
        update_frames = ([birth_frame] if s in leaves else []) + gate_frames[s]
        if not update_frames:
            terminal_blocked['no_updates'] += 1
            continue
        if not all(contains(B, F) for B in bytarget[t] for F in update_frames):
            terminal_blocked['target_past_update_frame'] += 1
            continue
        terminal.append(s)
    removed = set(pure) | set(terminal)
    hist = Counter()
    for s in removed:
        ds = w['chain_dims'][s]
        for lo, hi in zip(ds[:-1], ds[1:-1]):
            if hi > lo:
                hist[hi-lo] += 2*w['v']
        hist[w['h']-ds[-2]] += 2*w['v']
        hist[w['h']*w['h']-w['h']+ds[0]] += 2*w['v']
    hist.pop(0, None)
    assert sum(k*v for k, v in hist.items()) == 2*w['v']*len(removed)*w['h']**2
    out = dict(word_sha256=hashlib.sha256(a.word.read_bytes()).hexdigest(),
        scope='Read-only candidate inventory; combined deletion conflicts and a literal replacement word remain unchecked.',
        R=w['R'], deferred_count=len(w['deferred']),
        pure_leaf_count=len(pure), pure_leaf_roles=pure,
        terminal_count=len(terminal), terminal_roles=terminal,
        terminal_blocked=dict(terminal_blocked), union=len(removed),
        hypothetical_removed_child_multiplicities=dict(sorted(hist.items())),
        source_histogram=dict(sorted(Counter(source[s] for s in pure).items())),
        terminal_types={str(k):v for k,v in Counter((s in leaves,dest[s],len(basis(sigma[s]))) for s in terminal).items()})
    a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if not k.endswith('_roles')},indent=2))


if __name__ == '__main__':
    main()
