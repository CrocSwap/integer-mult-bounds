#!/usr/bin/env python3
"""Independent source-bound logical zero-address/frame audit; standard library only.

No producer verifier or source evaluator is imported. This checks the finite
premises of the accompanying moving-frame proof, not full physical admission.
"""
import argparse
from collections import Counter
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path

SOURCE_SHA = '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'
SOURCE_BLOB = '46d929df83817b85a5387bcdb9745e0627d6366e'
PROGRAM_SHA = {
    'forward': '03e406a5672ada3e1762011d667c79ec04a55d7d1163a9423d0005720234d2ca',
    'backward': 'a4ff7b7ca8f23c858f8e6f1044bc6abf92168ab17abd2aa420ad384f58a519d3',
}
PROFILE = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}
PHASES = ['zero_frame_precondition', 'entry_adapters', 'A', 'centers', 'B',
          'cleanup_tail', 'final', 'exit_adapters', 'full_frame_cleanup', 'done']


def need(ok, why):
    if not ok:
        raise ValueError(why)


def span(vs):
    s = {0}
    for v in vs:
        need(type(v) is int and 0 < v < 512, 'nonzero nine-bit frame vector')
        s |= {x ^ v for x in tuple(s)}
    return frozenset(s)


def lin(cols, x):
    y = 0
    for i, a in enumerate(cols):
        if (x >> i) & 1:
            y ^= a
    return y


def warp_table(c):
    operators = {}
    records = []
    for w in c['warps']:
        k, cols = w['op'], w['G_columns']
        need(k > 0 and k not in operators, 'unique positive warp identifier')
        need(len(cols) == 9 and all(type(x) is int and 0 < x < 512 for x in cols), 'nine-bit G columns')
        perm = [lin(cols, x) for x in range(512)]
        need(len(set(perm)) == 512 and perm[0] == 0, 'invertible homogeneous G')
        inverse = [0] * 512
        for x, y in enumerate(perm):
            inverse[y] = x
        # M=I+G^{-T}G^{-1}; compute entries by column inner products.
        icols = [inverse[1 << i] for i in range(9)]
        M = [sum((((icols[i] & icols[j]).bit_count() & 1) ^ (i == j)) << j
                 for j in range(9)) for i in range(9)]
        need(all(((M[i] >> j) & 1) == ((M[j] >> i) & 1) for i in range(9) for j in range(9)), 'symmetric quadratic form')

        def phase(y):
            return (sum(((M[i] >> i) & 1) * ((y >> i) & 1) for i in range(9))
                    + 2 * sum(((M[i] >> j) & 1) * ((y >> i) & 1) * ((y >> j) & 1)
                              for i in range(9) for j in range(i + 1, 9))) % 4

        # Positive and negative K, plus their entrywise conjugates. The latter
        # are the inverse-transpose orientation, not the adjoint orientation.
        images = [(perm[0], phase(perm[0])),
                  (inverse[0], -phase(0) % 4),
                  (perm[0], -phase(perm[0]) % 4),
                  (inverse[0], phase(0))]
        need(all(x == (0, 0) for x in images), 'all signed/oriented warps fix delta0 including phase')
        operators[k] = (perm, inverse)
        records.append({'op': k, 'four_signed_oriented_zero_images': [list(x) for x in images]})
    need(len(operators) == 72, 'all72 source warps')
    return operators, records


def run(source):
    raw = source.read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_SHA, 'exact source container')
    need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == SOURCE_BLOB, 'exact public Git blob')
    payload = gzip.decompress(raw)
    data = json.loads(payload)
    c = data['canonical']
    need(c['h'] == 9 and c['v'] == 112 and len(c['start']) == len(c['final']) == 632, 'actual source geometry')
    need({int(k): v for k, v in c['local_profile'].items()} == PROFILE, 'canonical complete profile')
    spaces = [span(f) for f in c['frames']]
    need(all(len(s) == 1 << len(f) for s, f in zip(spaces, c['frames'])), 'all frame bases independent')
    need(spaces[0] == {0} and len(spaces[1]) == 512, 'zero and full frame conventions')
    operators, warps = warp_table(c)
    for i, q in enumerate(c['ports']):
        need(spaces[c['start'][i]] == {0, q}, 'main source entry line')
        need(c['start'][112 + i] == 0 and c['final'][i] == 1, 'unchanged trivial main boundaries')
        need(spaces[c['final'][112 + i]] == {x for x in range(512) if not ((x & q).bit_count() & 1)}, 'main target exit orthogonal hyperplane')
    results = {}
    for direction in ('forward', 'backward'):
        program = data['programs'][direction]
        enc = json.dumps(program, sort_keys=True, separators=(',', ':')).encode()
        need(sha256(enc).hexdigest() == PROGRAM_SHA[direction], 'orientation-specific canonical program pin')
        cur = {('L', i): f for i, f in enumerate(c['start'])}
        cur['C', 0] = None
        phases, adapters, counts, paid = [], [], Counter(), Counter()
        early_identity_exit_markers = []
        entry_cut = program.index(['phase', 'entry_adapters'])
        exit_cut = program.index(['phase', 'exit_adapters'])
        for ix, e in enumerate(program):
            kind = e[0]
            counts[kind] += 1
            refs = ([tuple(r) for r in e[1][1:3] if isinstance(r, list)] if kind == 'scalar'
                    else [tuple(e[1])] if kind == 'warp'
                    else [('L', e[2])] if kind == 'climb' else [])
            need(not (ix < entry_cut and any(k == 'L' and r < 112 for k, r in refs)),
                 'no X access before nontrivial input adapters')
            need(not (ix > exit_cut and any(k == 'L' and 112 <= r < 224 for k, r in refs)),
                 'no Y access after nontrivial output adapters')
            if kind == 'phase':
                need(len(e) == 2, 'section label has no operator arguments')
                phases.append(e[1])
                need(phases == PHASES[:len(phases)], 'exact section-label chronology')
            elif kind == 'adapter':
                _, mode, role, frame = e
                need(0 <= role < 224, 'only main-role boundary adapters')
                need(mode in ('old_to_new', 'new_to_old'), 'known adapter direction')
                need(phases[-1] == ('entry_adapters' if mode == 'old_to_new' else 'exit_adapters'), 'adapter boundary chronology')
                need(frame == (c['start'] if mode == 'old_to_new' else c['final'])[role], 'exact boundary frame')
                if cur['L', role] != frame:
                    # Retiming postpones some final climbs beyond this inherited
                    # marker. X's old output reference and final gauge are BOTH
                    # the exact full Fourier F: this adapter is literally I.
                    need(mode == 'new_to_old' and role < 112 and frame == 1,
                         'only exact-identity full-X exit marker may precede its final climb')
                    early_identity_exit_markers.append({'event': ix, 'role': role, 'current_frame': cur['L', role]})
                adapters.append((mode, role))
            elif kind in ('climb', 'center'):
                if kind == 'climb':
                    _, label, role, a, b, rank = e
                    target = ('L', role)
                    need(spaces[a] < spaces[b], 'strict ascending borrowed transport')
                else:
                    _, role, a, b, rank = e
                    target = ('C', role)
                    need(role == 0 and phases[-1] == 'centers', 'single owned center reused')
                    need((spaces[b] < spaces[a]) if direction == 'forward' else (spaces[a] < spaces[b]), 'oriented center transport')
                need(cur[target] == a, 'paid transport source gauge')
                need(rank == abs(len(c['frames'][a]) - len(c['frames'][b])), 'paid rank is frame difference')
                cur[target] = b
                paid[rank] += 1
            elif kind == 'warp':
                _, ref, signed, a, b = e
                target = tuple(ref)
                need(target in cur and cur[target] == a, 'warp source gauge')
                need(signed and abs(signed) in operators, 'literal warp identifier')
                perm = operators[abs(signed)][signed < 0]
                need({perm[x] for x in spaces[a]} == spaces[b], 'warp carries actual frames')
                cur[target] = b
            elif kind == 'scalar':
                _, g, f = e
                op, target = g[0], tuple(g[1])
                need(target in cur, 'declared scalar owner')
                if op == 'clear':
                    need(target == ('C', 0), 'owned-only clear')
                    cur[target] = f
                else:
                    need(cur[target] == f, 'scalar target gauge')
                    if op in ('copy', 'add'):
                        source = tuple(g[2])
                        need(cur[source] == f, 'common scalar source gauge')
                        need(source != target, 'distinct source and target')
                        if op == 'copy':
                            need(target == ('C', 0), 'owned-only copy')
                    else:
                        need(op == 'scale', 'known scalar operation')
            else:
                # In particular no residual_adapter is present in this pinned
                # word. A future nontrivial wrapper must not be silently ignored.
                raise ValueError('unhandled event (including residual_adapter): ' + kind)
        need(phases == PHASES, 'all exact section labels')
        need(adapters == [(mode, i) for mode in ('old_to_new', 'new_to_old') for i in range(224)], 'all448 adapters exactly once in order')
        need([cur['L', i] for i in range(632)] == c['final'], 'all final moving frames')
        need(dict(paid) == PROFILE, 'complete oriented paid profile')
        results[direction] = {'program_sha256': PROGRAM_SHA[direction], 'events': len(program),
                              'event_counts': dict(counts), 'paid_profile': dict(sorted(paid.items())),
                              'all_scalar_contacts_and_paid_warp_frames_checked': True,
                              'logical_zero_address_warp_invariant': True,
                              'no_X_before_entry_or_Y_after_exit_adapter': True,
                              'early_identity_full_X_exit_markers': early_identity_exit_markers,
                              'residual_adapter_count': 0}
    return {'status': 'PASS_INDEPENDENT_LOGICAL_ZERO_ADDRESS_AND_FRAMES',
            'source_sha256': SOURCE_SHA, 'source_git_blob': SOURCE_BLOB,
            'payload_sha256': sha256(payload).hexdigest(), 'orientations': results,
            'warp_checks': warps,
            'qualification': 'Adapters and paid transports are gauge-covariant, not necessarily physical-delta0 preserving. See REVIEW.md. No full child physical recipe or rounded implementation replay is asserted.'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    need(not args.out.exists(), 'fresh receipt')
    result = run(args.source)
    result['checker_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'])
