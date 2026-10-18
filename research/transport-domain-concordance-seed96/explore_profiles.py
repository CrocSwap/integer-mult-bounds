#!/usr/bin/env python3
"""Optional reproduction of the bounded exploratory PR589 profile probe.

This is not the final certificate checker or a complete negative theorem.
Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import ROOT, WORD, digest, load, source_checks


def run(limit, seconds):
    source_checks()
    coverage = load('exploratory_coverage', HERE / 'vendor/pr1392/coverage.py')
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    baseline = coverage.State(word, coverage.Frames(word))
    ops = {op[3]: op for sec in 'AB' for op in baseline.sections[sec]}
    single = set()
    for sec in 'AB':
        flat = 0
        for _, _, sources in word[sec]:
            if len(sources) == 1:
                single.add((sec, flat))
            flat += len(sources)
    touches = defaultdict(set)
    for oid, op in ops.items():
        for reg in op[1:3]:
            touches[reg].add(oid)
    pairs = sorted({(x, y) for ids in touches.values() for x in ids for y in ids
                    if x != y and x[0] == y[0] and x in single and y in single})
    pairs = pairs[96:] + pairs[:96]
    start = time.monotonic()
    checked = []
    witnesses = []
    for x, y in pairs[:limit]:
        registers = set(ops[x][1:3] + ops[y][1:3])
        projected = baseline.clone()
        projected.sections = {sec: [o for o in baseline.sections[sec] if registers & set(o[1:3])]
                              for sec in 'AB'}
        index = projected.index(x)
        identity_signature = tuple(sum(r in o[1:3] for o in projected.sections[x[0]][:index])
                                   for r in ops[x][1:3])
        first = coverage.legal_moves(projected, x) + [(index, ops[x][0], identity_signature)]
        groups = defaultdict(list)
        for q, frame, signature in first:
            groups[(frame, signature)].append(q)
        for (frame, signature), slots in groups.items():
            if len(slots) < 2:
                continue
            representative = min(slots, key=lambda q: (abs(q-index), q))

            def reachable(q):
                after = projected.moved(x, q, frame)
                candidates = coverage.legal_moves(after, y) + [(after.index(y), ops[y][0], ())]
                return {tuple(sorted(after.moved(y, q2, f2).profile(registers).items()))
                        for q2, f2, _ in candidates}

            kept = reachable(representative)
            for q in slots:
                if q == representative:
                    continue
                missing = sorted(reachable(q) - kept)
                if missing:
                    witnesses.append({'x': x, 'y': y, 'frame': str(frame), 'signature': signature,
                                      'kept_slot': representative, 'alternative_slot': q,
                                      'missing_profiles': missing})
                    break
            if witnesses:
                break
        checked.append((x, y))
        if witnesses or time.monotonic() - start >= seconds:
            break
    return {'assignment_seed': 96, 'domain_size': len(pairs), 'requested_prefix': limit,
            'completed_prefix': len(checked), 'completed_prefix_sha256': digest(checked),
            'first_pair': checked[0] if checked else None,
            'last_pair': checked[-1] if checked else None,
            'witnesses': witnesses, 'seconds': time.monotonic() - start,
            'scope': 'Fixed-catalogue same-section original-single-source pairs only; not PR933 global-frame coverage.',
            'status': 'WITNESS' if witnesses else 'NO_MISSING_PROFILE_IN_COMPLETED_PREFIX'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=18715)
    parser.add_argument('--seconds', type=float, default=120)
    args = parser.parse_args()
    if not 1 <= args.limit <= 41978 or not 0 < args.seconds <= 600:
        parser.error('limit must be 1..41978 and seconds must be in (0,600]')
    print(json.dumps(run(args.limit, args.seconds), sort_keys=True, indent=2))
