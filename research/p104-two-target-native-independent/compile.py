#!/usr/bin/env python3
"""Compile only PR2445's added finite transports and their exact adjoints.

Adapted from Chafik Boukhalfa's PR1991 native P104 compiler, using icekylinx's
retained exact Clifford lowering. Ross Richardson with OpenAI Codex assistance.
Apache-2.0. This is a producer; the independent checker does not import it.
"""
import argparse
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'p104-native-channel'
_loader_path = HERE / 'source_exec.py'
_loader = {'__file__': str(_loader_path)}
exec(compile(_loader_path.read_bytes(), str(_loader_path), 'exec'), _loader)
INPUTS = _loader['authenticated_inputs'](HERE)
CE = _loader['load_source']('p104_native_ce', BASE / 'vendor/clifford_exact.py',
                          INPUTS['research/p104-native-channel/vendor/clifford_exact.py'])


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    for bit in sorted(pivots):
        for other in pivots:
            if other > bit and pivots[other] >> bit & 1:
                pivots[other] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def build():
    raw = INPUTS['inputs/CIRCUIT.json']
    word = json.loads(raw)
    inherited = json.loads(gzip.decompress(INPUTS['research/p104-native-channel/NATIVE-RECIPES.json.gz']))
    iso = inherited['label_isometry']
    dual = iso['compressed_dual_gram']
    orth = iso['orthonormal_basis_compressed']

    def image(value):
        return sum(CE.parity(value & CE.mv(dual, v)) << j for j, v in enumerate(orth))

    def frame(vectors):
        return canonical(image(v) for v in vectors)

    edges = {}
    profile = Counter()
    for slot, insertion in enumerate(word['insertions']):
        for index, event in enumerate(insertion['events']):
            if event[0] != 'transport':
                continue
            old, new, rank = frame(event[2]), frame(event[3]), event[4]
            need(rank == len(new)-len(old) > 0, 'positive nested gap')
            need(CE.rank(list(old)+list(new)) == len(new), 'nested physical frames')
            entry = edges.setdefault((old, new), {'rank': rank, 'occurrences': []})
            need(entry['rank'] == rank, 'consistent edge rank')
            entry['occurrences'].append([slot, index])
            profile[rank] += 1

    @lru_cache(None)
    def chart(basis):
        return CE.canonical_frame(9, basis)

    records = []
    for number, ((old, new), entry) in enumerate(sorted(edges.items())):
        op = chart(old).adjoint().then(chart(new))
        forward, _ = CE.lower_child(op)
        adjoint, _ = CE.lower_child(op.adjoint())
        need(forward['rank'] == adjoint['rank'] == entry['rank'], 'both native child ranks')
        records.append(dict(old=list(old), new=list(new), **entry,
                            forward=forward, adjoint=adjoint))
        if number % 40 == 0:
            print('COMPILED', number + 1, 'of', len(edges), flush=True)
    need(dict(profile) == {1:142, 2:16, 6:18, 7:60}, 'inherited added profile')
    return dict(schema_version=1, source_circuit_sha256=hashlib.sha256(raw).hexdigest(),
                label_isometry=iso, transports=records,
                added_profile={str(k): v for k, v in sorted(profile.items())},
                added_rank_mass=sum(k*v for k, v in profile.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    certificate = build()
    raw = (json.dumps(certificate, sort_keys=True, indent=2) + '\n').encode()
    with args.out.open('xb') as out:
        out.write(gzip.compress(raw, mtime=0))
    print('COMPILED_P104_TWO_TARGET_NATIVE', len(certificate['transports']),
          'edges', sum(certificate['added_profile'].values()), 'occurrences', flush=True)


if __name__ == '__main__':
    main()
