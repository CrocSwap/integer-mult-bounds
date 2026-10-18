#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Construct four coherent handoffs on the pinned PR2312 width-exchange words.

This is a direct circuit transformation, using Python's standard library only.
It moves the twelve block-616 correction gates, replaces four retired helper
roles by the source lenders (1,4,6,12), installs their explicit invertible chart
maps, and derives inverse-reverse cleanup from the changed non-target word.
The source and resulting word content are hash-bound. Hash equality is a
reproduction check; the independent all-column native chain proves correctness.
The input retains PR2312's width exchange (alias 651 re-lent from 530 and
alias 653 dropped), exact frame re-solve and the pivot-518/506 kernels.
Width exchange and its source frame/owner work are credited to Jeremy Kothe
(jeremykothe2), with AI assistance. The helper-donor kernels retain credit:
PR1625 shape by mdumitrean; PR2302 search, exact pricing and frame re-solve
by Jeremy Kothe (jeremykothe2), with AI assistance. This derivative was also
prepared with substantial AI assistance. See GENERATOR-NOTICE.txt for
inherited attribution and licensing.
"""
import argparse
import copy
import gzip
import hashlib
import json
import platform
import zlib
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = Path('research/gmx-t74-borrow43-width-exchange')
SOURCE_COMMIT = 'fb76f799ccf078f51780076ebed3fd26b1db11c0'
SOURCE_MANIFEST = 'c545968fb8cf6e550b82ba631e92fd756484db75e621aee211347749cff55313'
SOURCE_WORDS = {
    'base': '4244149b59b287344b0e91aa50c6fa2a2491ee6c7a76d61cd352684a8182d005',
    'extra': '01d510cc4ba912567f6b02ea50b6b0e741ed231a3608de9c36e7eeccbdaf6cda',
}
TARGET_WORDS = {
    'base': '93c32c9dc8ca18394b7f3afac2cb4fa8582a6cb77399441b5107b396e63ca0f9',
    'extra': 'aae6592eaa4cf8638f21d50c44d09d4f8a6bb079ddcf5e377711a10ee2ddb526',
}
TARGET_SEMANTICS = {
    'base': '3659c066d5cc2413a6f59bae8d5886e05feb8148333516f65365ad5235e14f2a',
    'extra': '9369702d158c34d594481a1789a2bddc029d03007253620cf3834ec60a88b1a5',
}
HIGH = (619, 621, 622, 623)
LOW = (616, 617, 618, 620)
LENDERS = (1, 4, 6, 12)
COMMON5 = (260, 132, 75, 42, 25)
COMMON4 = (260, 132, 75, 51)
# Literal G(e_i) columns of the four new rank-zero K_G handoffs. Each map is
# independently checked below, then physically lowered by the native auditor.
G_COLUMNS = (
    (1, 2, 4, 54, 72, 8, 130, 16, 284),
    (1, 2, 4, 8, 16, 32, 64, 135, 263),
    (1, 2, 4, 54, 72, 8, 130, 16, 284),
    (1, 2, 4, 8, 57, 66, 143, 16, 272),
)
PROFILE = {1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8}
WIDTHS = {4: 33, 5: 9, 7: 38, 8: 114, 9: 240}


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def semantic_sha(value):
    # JSON object keys are strings; normalize integer invoice keys before sorting.
    value = json.loads(json.dumps(value))
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def basis(vectors):
    """Canonical reduced GF(2) row basis, independent of set iteration order."""
    piv = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in piv:
                value ^= piv[bit]
            else:
                piv[bit] = value
                break
    for bit in sorted(piv):
        for higher in piv:
            if higher > bit and (piv[higher] >> bit) & 1:
                piv[higher] ^= piv[bit]
    return tuple(piv[bit] for bit in sorted(piv, reverse=True))


def incident(gate):
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def mapped(columns, vector):
    result = 0
    for bit, column in enumerate(columns):
        if (vector >> bit) & 1:
            result ^= column
    return result


def derive_cleanup(word):
    """PR2226/PR2288 inverse-reverse cleanup, retaining proper-end buffers."""
    v = word['report']['v']
    n = 2 * v + word['report']['R']
    restored = set(map(int, word['helper_final']))
    full = list(basis(1 << bit for bit in range(word['report']['h'])))
    buffer = lambda role: role + n if role in restored else role
    by_position = defaultdict(list)
    for operator, record in enumerate(word['warps'], 1):
        by_position[record[0]].append((record[1], operator))
    forward = list(word['A'])
    for position in range(len(word['B']) + 1):
        forward.extend(['warp', role, operator]
                       for role, operator in by_position[position])
        if position < len(word['B']):
            forward.append(word['B'][position])
    forward += word['restore']
    cleanup = []
    for gate in reversed(forward):
        if gate[0] == 'warp':
            cleanup.append(['warp', buffer(gate[1]), -gate[2], full])
        elif not v <= gate[1] < 2 * v:
            if gate[0] == 'add':
                cleanup.append(['add', buffer(gate[1]), buffer(gate[2]),
                                -gate[3], gate[4], full])
            else:
                cleanup.append(['scale', buffer(gate[1]), gate[3], gate[2], full])
    return cleanup


def paid_profile(word):
    """Recount literal native climbs, cut copies and retained helper widths."""
    v, h, helpers = (word['report'][key] for key in ('v', 'h', 'R'))
    n = 2 * v + helpers
    cur = [(port,) for port in word['ports']] + [()] * (v + helpers)
    for role, frame in word['start_extra'].items():
        cur[int(role)] = basis(frame)
    full = basis(1 << bit for bit in range(h))
    ends = [full] * v + [basis(x for x in range(1, 1 << h)
                    if (x & port).bit_count() % 2 == 0)
                    for port in word['ports']] + [full] * helpers
    for role, frame in word['helper_final'].items():
        ends[int(role)] = basis(frame)
    paid = Counter()

    def climb(role, frame):
        frame = basis(frame)
        require(basis(cur[role] + frame) == frame, 'Nonmonotone frame chain')
        degree = len(frame) - len(cur[role])
        if degree:
            paid[degree] += 1
        cur[role] = frame

    def gate(event):
        for role in incident(event):
            climb(role, event[-1])

    for event in word['A']:
        gate(event)
    levels = {int(t): basis(frame) for t, frame in word['target_levels'].items()}
    require(all(cur[v+t] == levels.get(t, ()) for t in range(v)), 'Cut target frame')
    for role, frame in zip(word['centers'], word['center_frames']):
        frame = basis(frame)
        require(cur[role] == frame, 'Cut producer frame')
        readers = {levels.get(event[1]-v, ()) for event in word['cut']
                   if event[2] == role}
        for reader in sorted(readers, key=lambda x: -len(x)):
            require(basis(reader + frame) == frame, 'Unnested private copy')
            if reader != frame:
                paid[len(frame)-len(reader)] += 1
            frame = reader
    by_position = defaultdict(list)
    for record in word['warps']:
        by_position[record[0]].append(record)
    for position in range(len(word['B']) + 1):
        for _, role, columns, old, new in by_position[position]:
            require(cur[role] == basis(old), 'Handoff source frame')
            require(len(basis(columns)) == h, 'Singular chart map')
            require(basis(mapped(columns, x) for x in old) == basis(new),
                    'Chart map does not carry the measured source frame')
            cur[role] = basis(new)
        if position < len(word['B']):
            gate(word['B'][position])
    for event in word['restore']:
        gate(event)
    live = set(range(n)) - set(word['removed'])
    for role in live:
        climb(role, ends[role])
    widths = Counter(len(ends[role]) - len(basis(word['start_extra'].get(str(role), [])))
                     for role in live if role >= 2 * v)
    return dict(sorted(paid.items())), dict(sorted(widths.items()))


def build(source):
    word = copy.deepcopy(source)
    require(word['report']['v'] == 112 and word['report']['h'] == 9
            and word['report']['R'] == 480, 'Unexpected source geometry')
    roles = set(LOW + HIGH)
    prep = [i for i, event in enumerate(word['B'])
            if set(incident(event)) <= roles]
    # The only internal gates before source acquisition are the twelve M gates.
    first = next(i for i, event in enumerate(word['B'])
                 if event[0] == 'add' and event[1] in roles
                 and event[2] not in roles and len(event[-1]) >= 6)
    prep = [i for i in prep if i < first]
    require(len(prep) == 12 and prep == list(range(prep[0], prep[0]+12)),
            'Expected twelve consecutive block-616 correction gates')
    lo, hi = prep[0], prep[-1] + 1
    require(all(not roles.intersection(incident(event))
                for event in word['B'][hi:first]), 'Block is not idle before relocation')
    require(all(basis(word['B'][i][-1]) == basis(COMMON5) for i in prep),
            'Unexpected correction chart')
    require(all(event[0] == 'add' and event[1] in LOW and event[2] in HIGH
                for event in (word['B'][i] for i in prep)), 'Unexpected correction payload')
    require(all(basis(word['start_extra'][str(role)]) == basis(COMMON5)
                for role in HIGH), 'Unexpected removed helper entrance')
    require(not any(record[0] in range(lo, hi+1) or record[0] == first
                    for record in word['warps']), 'Warp inside relocation boundary')
    replace = dict(zip(HIGH, LENDERS))
    moved = [event[:-1] + [list(COMMON4)] for event in word['B'][lo:hi]]
    word['B'] = word['B'][:lo] + word['B'][hi:first] + moved + word['B'][first:]
    handoff = first - len(moved)
    for event in word['B']:
        for index in range(1, 3 if event[0] == 'add' else 2):
            event[index] = replace.get(event[index], event[index])
    for record in word['warps']:
        if hi <= record[0] < first:
            record[0] -= len(moved)
        # Preserve the already-audited literal basis representatives emitted by
        # the original builder. These replacements span precisely the same U.
        rewrite = {(384, 134, 120, 30): (384, 134, 102, 30),
                   (448, 56, 21, 11): (448, 38, 21, 11)}
        old = tuple(record[3])
        if old in rewrite:
            require(basis(old) == basis(rewrite[old]), 'Basis serialization changed U')
            record[3] = list(rewrite[old])
    # Measure each retired source at the chronological handoff, without trusting
    # a lender chart copied from a generated target artifact.
    cur = [(port,) for port in word['ports']] + [()] * (112 + 480)
    for role, frame in word['start_extra'].items():
        cur[int(role)] = basis(frame)
    for event in source['A']:
        for role in incident(event):
            cur[role] = basis(event[-1])
    old_warps = defaultdict(list)
    for record in source['warps']:
        old_warps[record[0]].append(record)
    for position in range(first):
        for record in old_warps[position]:
            cur[record[1]] = basis(record[4])
        for role in incident(source['B'][position]):
            cur[role] = basis(source['B'][position][-1])
    for role, columns in zip(LENDERS, G_COLUMNS):
        require(len(cur[role]) == 4, 'Retired lender must be rank 4')
        require(max(i for i, event in enumerate(source['B'])
                    if role in incident(event)) < first, 'Source lender still live')
        old_literal = (384, 131, 75, 51) if role == 4 else cur[role]
        new_literal = (384, 132, 75, 51)
        require(basis(old_literal) == cur[role]
                and basis(new_literal) == basis(COMMON4),
                'Literal handoff representative changed its subspace')
        word['warps'].append([handoff, role, list(columns),
                              list(old_literal), list(new_literal)])
    for role in HIGH:
        del word['start_extra'][str(role)]
    word['removed'] = sorted(set(word['removed']).union(HIGH))
    word['base'] = 'PR2312-width-exchange-plus-coherent-joint616'
    profile, widths = paid_profile(word)
    require(profile == PROFILE and widths == WIDTHS, 'Unexpected generated invoice')
    word['report']['local_profile'] = profile
    word['report']['width_inventory'] = widths
    word['cleanup'] = derive_cleanup(word)
    return word, dict(old_correction_interval=[lo, hi], old_first_input=first,
                      relocated_correction_interval=[handoff, handoff+12],
                      removed_roles=list(HIGH), lenders=list(LENDERS))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True,
                        help='Repository root containing the pinned PR2312 package')
    parser.add_argument('--out', '--output', type=Path, required=True,
                        help='Destination for base.json.gz, extra.json.gz and GENERATION.json')
    args = parser.parse_args()
    package = args.source_root.resolve() / PACKAGE
    manifest_bytes = (package / 'MANIFEST.json').read_bytes()
    require(sha(manifest_bytes) == SOURCE_MANIFEST, 'Unpinned upstream manifest')
    manifest = json.loads(manifest_bytes)
    args.out.mkdir(parents=True, exist_ok=True)
    reports = {}
    for kind in ('base', 'extra'):
        relative = f'new/borrow/words/BORROW-WORD-43{kind}.json.gz'
        raw = (package / relative).read_bytes()
        require(sha(raw) == SOURCE_WORDS[kind] == manifest[relative],
                'Unpinned '+kind+' source word')
        word, changes = build(json.loads(gzip.decompress(raw)))
        content = json.dumps(word, separators=(',', ':')).encode()
        canonical_hash = semantic_sha(word)
        require(canonical_hash == TARGET_SEMANTICS[kind],
                'Generated '+kind+' circuit differs from the frozen audited input')
        compressed = bytearray(gzip.compress(content, compresslevel=9, mtime=0))
        compressed[9] = 255  # Normalize the Python 3.11/3.12 gzip OS header byte.
        compressed = bytes(compressed)
        destination = args.out / (kind+'.json.gz')
        destination.write_bytes(compressed)
        reports[kind] = dict(source_word_sha256=sha(raw), output=destination.name,
                             output_sha256=sha(compressed), content_sha256=sha(content),
                             canonical_json_sha256=canonical_hash,
                             frozen_container_sha256=TARGET_WORDS[kind],
                             container_matches_frozen=sha(compressed) == TARGET_WORDS[kind],
                             local_profile=word['report']['local_profile'],
                             width_inventory=word['report']['width_inventory'],
                             changes=changes)
        print('PASS_GENERATED_AUDITED_WORD_SEMANTICS', kind, canonical_hash, flush=True)
    receipt = dict(status='PASS_SOURCE_BOUND_EXACT_WORD_GENERATION',
                   source_commit=SOURCE_COMMIT, source_manifest_sha256=SOURCE_MANIFEST,
                   generator_sha256=sha(Path(__file__).read_bytes()), words=reports,
                   compression_environment=dict(python=platform.python_version(),
                                                zlib=zlib.ZLIB_RUNTIME_VERSION),
                   equality='Canonical JSON of every field; gzip container hashes are metadata',
                   scope='Exact source-bound reproduction of the independently audited words. '
                         'Circuit correctness, physical phases and the global owner invoice '
                         'are established by their separate native and global receipts.')
    (args.out / 'GENERATION.json').write_text(json.dumps(receipt, indent=2)+'\n')


if __name__ == '__main__':
    main()
