#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""Exact enlarged-seam certificate. Standard library; checks survive -O."""
import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'
PRIOR = 'research/r439-dirty-workspace-frame-bound/CERTIFICATE.json'
CUT = 1991
FRAME = 508
REGS = (19, 27, 35, 43, 57, 65, 66, 74, 89, 97, 466)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def pins(root=ROOT):
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    records = {x['path']: x for x in manifest['files'] if x['usage'] == 'input'}
    need(set(records) == {WORD, PRIOR}, 'input inventory')
    out = {}
    for name, pin in records.items():
        data = (root / name).read_bytes()
        need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source SHA256: ' + name)
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        need(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'source Git blob: ' + name)
        out[name] = json.loads(gzip.decompress(data) if name.endswith('.gz') else data)
    return out


def bits(x):
    while x:
        bit = x & -x
        yield bit.bit_length() - 1
        x ^= bit


def geometry(word):
    @lru_cache(None)
    def basis(ids):
        pivots, chosen = {}, []
        for i in ids:
            row = list(map(Fraction, word['lines'][i]))
            for p, old in sorted(pivots.items()):
                q = row[p]
                if q:
                    row = [x - q*y for x, y in zip(row, old)]
            p = next((j for j, x in enumerate(row) if x), None)
            if p is not None:
                q = row[p]
                pivots[p] = tuple(x/q for x in row)
                chosen.append(i)
        return tuple(chosen)
    return lambda ids: basis(tuple(sorted(set(ids))))


def elementary(ops):
    return [(d, s) for _, d, ss in ops for s in ss]


def matrix(n, gates):
    rows = [1 << i for i in range(n)]
    for d, s in gates:
        need(d != s and 0 <= d < n and 0 <= s < n, 'invalid elementary ADD')
        rows[d] ^= rows[s]
    return rows


def product(a, b):
    result = []
    for row in a:
        value = 0
        for j in bits(row):
            value ^= b[j]
        result.append(value)
    return result


def profile(c):
    return {str(r): count for r, count in sorted(c.items()) if count and r}


def validate_contract(w):
    v = w['v']
    need(v == 111 and w['R'] == 439, 'word dimensions')
    need(len(w['start']) == len(w['final']) == 661, 'register inventory')
    for i in range(v):
        need(w['frames'][w['start'][i]] == [i], 'original source label')
    for f, d, ss in w['A']:
        need(d >= 2*v, 'source-preserving A premise')
        need(all(not v <= s < 2*v for s in ss), 'no target feedback in A')
    for f, d, ss in w['B']:
        if not v <= d < 2*v:
            need(all(not v <= s < 2*v for s in ss), 'no target feedback in B')


def compute(w, prior):
    validate_contract(w)
    n, v = 661, w['v']
    basis = geometry(w)
    frames = list(map(set, w['frames']))
    dims = [len(basis(f)) for f in frames]
    block_indices = [i for i, (f, _, _) in enumerate(w['B']) if f == FRAME]
    need(block_indices == list(range(174, 195)), 'B508 interval')
    end = block_indices[-1] + 1
    old_block = next(b for b in prior['blocks'] if b['frame'] == FRAME)
    need(old_block['registers'] == list(REGS), 'predecessor wire identity')
    need(w['A'][CUT] == [508, 385, [43, 57, 297, 416, 433, 466, 467]], 'enlarged left boundary')

    current = w['start'].copy()
    paths = [[f] for f in current]
    seam_paths = None
    copy_frames = None
    for sec in 'DABC':
        for k, (f, d, ss) in enumerate(w[sec]):
            if sec == 'A' and k == CUT:
                entry = current.copy()
                seam_paths = [[f0] for f0 in current]
            in_seam = (sec == 'A' and k >= CUT) or (sec == 'B' and k < end)
            for r in (d, *ss):
                old = current[r]
                if old != f:
                    need(frames[old] < frames[f] and dims[old] < dims[f], 'monotone source path')
                    current[r] = f
                    paths[r].append(f)
                    if in_seam:
                        seam_paths[r].append(f)
        if sec == 'A':
            copy_frames = [current[r] for r in w['ret']]
    for r, f in enumerate(w['final']):
        if current[r] != f:
            need(frames[current[r]] < frames[f], 'final path inclusion')
            paths[r].append(f)
    need([dims[f] for f in copy_frames] == [7]*9, 'nine COPY ranks')
    whole = Counter(dims[b] - dims[a] for p in paths for a, b in zip(p, p[1:]))
    whole.update([7]*9)
    need(profile(whole) == {'1':1323,'2':1342,'3':79,'4':44,'5':102,'6':11,'7':19}, 'whole baseline invoice')
    seam_bill = Counter(dims[b] - dims[a] for p in seam_paths for a, b in zip(p, p[1:]))

    a_gates = elementary(w['A'][CUT:])
    b_gates = elementary(w['B'][:end])
    # COPY/scatter/ERASE is a target-only ADD map on the original registers.
    scatter = [(v+i, w['ret'][j]) for j in range(9) for i, ss in enumerate(w['scatter']) if j in ss]
    all_gates = a_gates + scatter + b_gates
    M = matrix(n, all_gates)
    inv = matrix(n, list(reversed(all_gates)))
    identity = [1 << i for i in range(n)]
    need(product(M, inv) == product(inv, M) == identity, 'complete two-sided inverse')
    no_scatter = matrix(n, a_gates + b_gates)
    subsystem = list(range(v)) + list(range(2*v, n))
    need(all(M[r] == no_scatter[r] for r in subsystem), 'scatter return channel')
    need(all(not (M[r] >> v) & ((1 << v)-1) for r in subsystem), 'target independence')
    copies = matrix(n, a_gates)
    inverse_b = matrix(n, list(reversed(b_gates)))
    need(inv[:v] == inverse_b[:v], 'source-preserving prefix inverse identity')

    source_mask = (1 << v)-1
    dual = {r: sum(1 << j for j in range(v) if inv[j] >> r & 1) for r in REGS}
    records = []
    main_bill = Counter()
    for r in REGS:
        forward = M[r] & source_mask
        own = 1 << r if r < v else 0
        origins = list(bits(forward | dual[r] | own))
        witness = basis(origins)
        need(len(witness) == 4 and len(basis([*origins, *frames[FRAME]])) == 4, 'source-only full-frame witness')
        need(dims[entry[r]] in (1, 2), 'main entry dimension')
        need(seam_paths[r] == [entry[r], FRAME], 'attaining original path')
        charge = 4 - dims[entry[r]]
        main_bill[charge] += 1
        records.append({'register':r, 'entry_frame':entry[r], 'entry_rank':dims[entry[r]],
                        'forward_sources':list(bits(forward)), 'inverse_source_outputs':list(bits(dual[r])),
                        'source_only_witness':list(witness), 'forced_frame':FRAME, 'minimum_increment':charge})
    need(profile(main_bill) == {'2':8,'3':3}, 'eleven-wire lower bill')
    need(records[0]['forward_sources'] == [19] and records[0]['inverse_source_outputs'] == [19,35,66,89,97], 'exceptional source witness')

    # M_(k-1)=M_k E_(k-1); A fixes source coordinates, so inverse source rows do not change.
    rows = {r:M[r] for r in REGS}
    atlas = []
    for cut in range(CUT, -1, -1):
        record = []
        for r in REGS:
            forward = rows[r] & source_mask
            roots = list(bits(forward | dual[r] | ((1 << r) if r < v else 0)))
            witness = basis(roots)
            need(len(witness) == 4 and len(basis([*roots, *frames[FRAME]])) == 4, 'earlier-cut source-only witness')
            record.append([r, forward, dual[r], list(witness)])
        atlas.append([cut, record])
        if cut:
            _, d, ss = w['A'][cut-1]
            mask = sum(1 << s for s in ss)
            need(len(ss) == len(set(ss)), 'right-product source multiplicity')
            for r in REGS:
                if rows[r] >> d & 1:
                    rows[r] ^= mask
    atlas.reverse()
    remainder = seam_bill - main_bill
    return {'schema_version':1, 'status':'SCOPED_PROOF_AND_FINITE_CERTIFICATE', 'no_new_kappa':True,
            'interval':{'A_start_inclusive':CUT,'A_stop_exclusive':len(w['A']),
                        'B_start_inclusive':0,'B_stop_exclusive':end,
                        'stored_AB_operations':len(w['A'])-CUT+end,
                        'elementary_AB_ADDs':len(a_gates)+len(b_gates),
                        'scatter_ADDs':len(scatter), 'original_registers':n},
            'copy_observations':{'registers':w['ret'],'frames':copy_frames,'ranks':[7]*9,
                                 'rows_sha256':digest([copies[r] for r in w['ret']])},
            'full_endpoint_rows_sha256':digest(M), 'full_inverse_rows_sha256':digest(inv),
            'wires':records, 'minimum_eleven_wire_profile':profile(main_bill), 'minimum_eleven_wire_rank_mass':25,
            'baseline_seam_profile':profile(seam_bill), 'baseline_other_wire_profile':profile(remainder),
            'baseline_seam_rank_mass':sum(r*c for r,c in seam_bill.items()),
            'baseline_whole_word_profile':profile(whole),'baseline_whole_word_rank_mass':sum(r*c for r,c in whole.items()),
            'earlier_cut_atlas':{'first_cut':0,'last_cut':CUT,'cuts':len(atlas),
                                 'wire_cut_checks':len(atlas)*len(REGS),'all_forced_ranks':4,'rows_sha256':digest(atlas)},
            'limits':['The sharp invoice concerns eleven named wires before the fixed right cut.',
                      'Other wires, changed exit frames, later continuation, hosting and normalization require a complete new invoice.',
                      'COPY may write targets only; no returned copy or target feedback enters the reversible source/helper subsystem.',
                      'No whole-seam optimum, new supplier, selected cold replay or new exponent is certified.']}


def validate_certificate(expected, actual):
    need(canonical(expected) == canonical(actual), 'certificate mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    inputs = pins(args.root)
    result = compute(inputs[WORD], inputs[PRIOR])
    if args.output:
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
    else:
        validate_certificate(json.loads((HERE/'CERTIFICATE.json').read_text()), result)
    print('PASS_R439_ENLARGED_SEAM cuts=1992 wire_cut_checks=21912 '
          'minimum=8H2+3H3 mass=25 no_new_kappa')


if __name__ == '__main__':
    main()
