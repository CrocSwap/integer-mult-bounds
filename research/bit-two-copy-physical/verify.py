#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Adam Gall with substantial OpenAI Codex assistance.
"""Two private snapshots with actual rational address pullbacks; no supplier admission."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
import math
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'
SELECTED = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
HOST = 'research/community-hyperplane599-audit/pr589/bit589/v9/hosted/GLOBAL-TEMPLATE.json.gz'
GEO = 'research/community-hyperplane599-audit/pr589/bit589/v9/nine/GEOMETRY.json'
PARTITION = ((0, 3), (1,), (2, 4), (5, 7), (6, 8))
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


class Reject(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load(path):
    data = (ROOT / path).read_bytes()
    return json.loads(gzip.decompress(data) if path.endswith('.gz') else data)


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    need(pins['base_commit'] == '564148b82ae9df72163f22106f15e73efca8aff2', 'wrong scientific base')
    for item in pins['files']:
        if item['usage'] == 'input':
            raw = (ROOT / item['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source hash: ' + item['path'])
            blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            need(blob == item['git_blob'], 'source blob: ' + item['path'])
    need({WORD, SELECTED, HOST, GEO} <= {x['path'] for x in pins['files'] if x['usage'] == 'input'}, 'missing consumed input pin')


def projection(rows):
    basis = []
    for row in rows:
        v = tuple(map(Q, row))
        for b in basis:
            c = sum(x*y for x, y in zip(v, b)) / sum(x*x for x in b)
            v = tuple(x-c*y for x, y in zip(v, b))
        if any(v):
            basis.append(v)
    p = tuple(tuple(sum((b[i]*b[j]/sum(x*x for x in b) for b in basis), Q(0))
                    for j in range(8)) for i in range(8))
    return p, len(basis)


class AddressAlgebra:
    """Intern exact 16x16 rational maps and compose real pullbacks, including MOVEs."""
    def __init__(self):
        self.maps = []
        self.ids = {}
        self.identity = self.intern(tuple(int(i == j) for i in range(16) for j in range(16)), 1)

    def intern(self, entries, denominator):
        g = math.gcd(denominator, *entries)
        key = (tuple(x//g for x in entries), denominator//g)
        if key not in self.ids:
            self.ids[key] = len(self.maps)
            self.maps.append(key)
        return self.ids[key]

    def partial_swap(self, p):
        entries = []
        for i in range(16):
            for j in range(16):
                a = p[i % 8][j % 8]
                entries.append(Q(i % 8 == j % 8) - a if i//8 == j//8 else a)
        denominator = math.lcm(*(x.denominator for x in entries))
        need(denominator & (denominator-1) == 0, 'non-dyadic address matrix')
        return self.intern(tuple(int(x*denominator) for x in entries), denominator)

    @lru_cache(None)
    def compose(self, left, right):
        if left == self.identity:
            return right
        if right == self.identity:
            return left
        a, da = self.maps[left]
        b, db = self.maps[right]
        out = [0]*256
        for i in range(16):
            for k in range(16):
                x = a[16*i+k]
                if x:
                    for j in range(16):
                        out[16*i+j] += x*b[16*k+j]
        return self.intern(tuple(out), da*db)

    def serial(self, index):
        a, d = self.maps[index]
        return {'denominator': d, 'rows': [list(a[i:i+16]) for i in range(0, 256, 16)]}

    def pullback(self, row, transform):
        # A term (i,A) is the arbitrary physical input function f_i composed with A.
        # Native address transport T is actual right multiplication A T, not a frame relabel.
        return {(i, self.compose(a, transform)) for i, a in row}


def geometry(word, algebra):
    projections, dims, swaps = [], [], []
    for frame in word['frames']:
        p, dim = projection([word['lines'][j] for j in frame])
        swap = algebra.partial_swap(p)
        need(algebra.compose(swap, swap) == algebra.identity, 'non-involutive frame swap')
        projections.append(p)
        dims.append(dim)
        swaps.append(swap)
    need(dims[0] == 0 and len(projections) == 636, 'unexpected frame convention')
    return projections, dims, swaps


def emit(word, dims, paired):
    n = 2*word['v'] + word['R']
    frames = word['start'][:]
    records = []
    def move(role, frame):
        old = frames[role]
        if old != frame:
            records.append((0, role, old, frame, dims[frame]-dims[old], 0))
            frames[role] = frame
    def gates(section, phase):
        for frame, dst, srcs in word[section]:
            for role in (dst, *srcs):
                move(role, frame)
            for src in srcs:
                records.append((1, dst, src, 1, frame, phase))
    gates('D', 1)
    gates('A', 2)
    scatter_start = len(records)
    scatter_frames = frames[:]
    supports = [{word['v']+t for t, row in enumerate(word['scatter']) if j in row} for j in range(9)]
    partition = PARTITION if paired else tuple((j,) for j in range(9))
    for block in partition:
        for slot, j in enumerate(block):
            center = word['ret'][j]
            records.append((2, center, n+slot, frames[center], 0, dims[frames[center]]))
        if len(block) == 1:
            for target in sorted(supports[block[0]]):
                records.append((1, target, n, 1, 0, 3))
        else:
            a, b = map(supports.__getitem__, block)
            for target in sorted(a-b):
                records.append((1, target, n, 1, 0, 3))
            for target in sorted(b-a):
                records.append((1, target, n+1, 1, 0, 3))
            records.append((1, n, n+1, 1, 0, 3))
            for target in sorted(a & b):
                records.append((1, target, n, 1, 0, 3))
            records.append((1, n, n+1, -1, 0, 3))
        for slot, j in reversed(list(enumerate(block))):
            center = word['ret'][j]
            records.append((3, center, n+slot, frames[center], 0, 0))
    scatter_end = len(records)
    gates('B', 4)
    gates('C', 5)
    for role, frame in enumerate(word['final']):
        move(role, frame)
    return records, (scatter_start, scatter_end), scatter_frames


def reverse(records, dims):
    out = []
    for op, a, b, c, d, e in reversed(records):
        if op == 0:
            out.append((0, a, c, b, d, e))
        elif op == 1:
            out.append((1, a, b, -c, d, e))
        elif op == 2:
            out.append((3, a, b, c, d, 0))
        else:
            out.append((2, a, b, c, d, abs(dims[c]-dims[d])))
    return out


def execute(records, word, dims, swaps, algebra, initial_frames, rev=False,
            blind_erase=False, wrong_copy=None, dirty_slot=False, omit_move_address=False):
    n = 2*word['v']+word['R']
    rows = [{(j, algebra.identity)} for j in range(n)] + [set(), set()]
    frames = initial_frames[:] + [-1, -1]
    if dirty_slot:
        rows[n] = {(n, algebra.identity)}
    live = {}
    paid = Counter()
    counts = Counter()
    norms = [1]*n + [0, 0]
    peak = 1
    peak_slots = 0
    moved_atoms = 0
    for op, a, b, c, d, e in records:
        if op == 0:
            need(a < n and frames[a] == b and a not in live.values(), 'MOVE binding')
            low, high = (c, b) if rev else (b, c)
            need(set(word['frames'][low]) <= set(word['frames'][high]) and dims[high]-dims[low] == d > 0, 'MOVE containment/price')
            transport = algebra.compose(swaps[b], swaps[c])
            if not (omit_move_address and counts['MOVE'] == 0):
                rows[a] = algebra.pullback(rows[a], transport)
            moved_atoms += len(rows[a])
            frames[a] = c
            paid[d] += 1
            counts['MOVE'] += 1
        elif op == 1:
            need(a != b and 0 <= a < n+2 and 0 <= b < n+2 and abs(c) == 1, 'ADD operands')
            need(frames[a] == frames[b] == d, 'ADD unequal native frames')
            need((a < n or a in live) and (b < n or b in live), 'ADD closed temporary')
            need(a not in live.values(), 'ADD changes live center')
            rows[a] ^= rows[b]
            norms[a] += norms[b]
            peak = max(peak, norms[a])
            counts['ADD'] += 1
        elif op == 2:
            need(a < n and n <= b < n+2 and b not in live and not rows[b] and frames[b] == -1, 'COPY occupied destination')
            need(frames[a] == c and d == 0 and e == abs(dims[c]-dims[d]) == 7, 'COPY frame/price')
            transport = algebra.compose(swaps[c], swaps[d]) if wrong_copy is None else wrong_copy
            rows[b] = algebra.pullback(rows[a], transport)
            frames[b] = d
            norms[b] = norms[a]
            live[b] = a
            paid[e] += 1
            counts['COPY'] += 1
            peak_slots = max(peak_slots, len(live))
        elif op == 3:
            need(live.get(b) == a and frames[a] == c and frames[b] == d, 'ERASE binding')
            expected = algebra.pullback(rows[a], algebra.compose(swaps[c], swaps[d]))
            need(blind_erase or rows[b] == expected, 'ERASE physical transported equality')
            rows[b] = set()
            frames[b] = -1
            norms[b] = 0
            del live[b]
            counts['ERASE'] += 1
        else:
            raise Reject('unknown event')
    need(not live and not rows[n] and not rows[n+1], 'private stream not restored')
    return rows[:n], frames[:n], {
        'events': dict(sorted(counts.items())), 'paid_profile': dict(sorted(paid.items())),
        'peak_private_streams': peak_slots, 'positive_row_bound': peak,
        'physical_atom_MOVE_compositions': moved_atoms,
    }


def private_owners(template, word, geo, reserve=None, aliases=False):
    live = template['live']
    reserve = template['private_centre_reserve'] if reserve is None else reserve
    private = (live, live if aliases else live+1)
    need(reserve >= 2 and len(set(private)) == 2 and all(live <= x < live+reserve for x in private), 'private reserve/separation')
    need((live, template['private_centre_reserve'], template['m'], template['stages'], template['replicas']) == (28416, 9, 64, 9, 32), 'wrong selected owner layout')
    # Orthogonality of A_q = [q/2 | U_q] is exact, independent of cover class d.
    for port, g in enumerate(geo['ports']):
        need(g['q'] == word['lines'][port] and g['port'] == port, 'owner geometry label')
        a = [(Q(g['q'][i], 2), *map(Q, g['complement_columns'][i])) for i in range(8)]
        for i in range(8):
            for j in range(8):
                need(sum(row[i]*row[j] for row in a) == int(i == j), 'nonorthogonal owner chart')
    idle = {e['idx']: e for e in template['schedule'] if e['kind'] == 'idle'}
    slots = {}
    for child, cp, offset, width, stage, helper in template['hosting']['slots']:
        event = idle[child]
        old, new = event['source_level'], event['target_level']
        axes = list(range(1 if old == -1 else 8+7*old, 8+7*new))
        chosen = axes[offset:offset+width]
        need(width == 8 and len(chosen) == 8 and len(set(chosen)) == 8, 'host slot width')
        perm = tuple(chosen + [j for j in range(64) if j not in chosen])
        need(sorted(perm) == list(range(64)), 'host chart permutation')
        slots[stage, helper] = (child, cp, offset, perm)
    occurrences = 0
    center_charts = set()
    for call in template['calls']:
        stage, replica, pair = call['stage'], call['replica'], call['pair']
        keys = set()
        need(len(call['owners']) == 661, 'persistent role count')
        for role, (family, route) in enumerate(call['owners']):
            need(0 <= family < live and family not in private, 'private/persistent collision')
            if role < 222:
                side = role//111
                if call['orientation'] == 'reverse':
                    side = 1-side
                need(family == replica*888+(2*pair+side)*111+role%111 and route == ['data', stage, role%111], 'data owner binding')
                key = (family, 'data')
            else:
                child, cp, offset, perm = slots[stage, role-222]
                side, port = divmod(cp, 111)
                host_pair = idle[child]['pair']
                need(host_pair != pair and family == replica*888+(2*host_pair+side)*111+port, 'helper family binding')
                need(route == ['hosted', child, offset, 8], 'helper owner binding')
                key = (family, perm)
                if role in word['ret']:
                    center_charts.add((port, perm))
            need(key not in keys, 'noninjective persistent owner chart')
            keys.add(key)
            occurrences += 1
    need(len(template['calls']) == 288, 'missing stage/replica descriptors')
    return {'live_persistent_families': live, 'reserved_private_families': reserve,
            'allocated_private_families': list(private), 'physical_families_retained': live+reserve,
            'stage_replica_descriptors': len(template['calls']), 'persistent_owner_occurrences': occurrences,
            'retained_center_chart_shapes': len(center_charts), 'unused_private_families': reserve-2,
            'cover_class_scope': 'all d by distinct family tags; no finite cover enumeration'}


def reject(action, label):
    try:
        action()
    except Reject:
        return label
    raise Reject('negative control accepted: ' + label)


def run():
    authenticate()
    word, selected, template, geo = map(load, (WORD, SELECTED, HOST, GEO))
    need((word['v'], word['R'], word['h']) == (111, 439, 8), 'word scope')
    for key in ('lines', 'frames', 'ret', 'scatter', 'start', 'final', 'A'):
        need(word[key] == selected[key], 'changed selected physical interface: ' + key)
    alg = AddressAlgebra()
    projectors, dims, swaps = geometry(word, alg)
    old, old_cut, initial_cut = emit(word, dims, False)
    new, new_cut, new_initial_cut = emit(word, dims, True)
    need(initial_cut == new_initial_cut, 'scatter entry frame changed')
    need(old[:old_cut[0]] == new[:new_cut[0]] and old[old_cut[1]:] == new[new_cut[1]:], 'non-scatter change')
    owner_report = private_owners(template, word, geo)
    reports = {}
    for rev in (False, True):
        start = word['final'] if rev else word['start']
        baseline = reverse(old, dims) if rev else old
        candidate = reverse(new, dims) if rev else new
        before = execute(baseline, word, dims, swaps, alg, start, rev)
        after = execute(candidate, word, dims, swaps, alg, start, rev)
        need(before[:2] == after[:2], 'complete physical function endpoint mismatch')
        need(after[1] == (word['start'] if rev else word['final']), 'physical final frame mismatch')
        need(before[2]['paid_profile'] == after[2]['paid_profile'] == PROFILE, 'changed rank price')
        need(after[2]['events'] == {'ADD': 11380, 'COPY': 9, 'ERASE': 9, 'MOVE': 2911}, 'incomplete candidate bill')
        need(before[2]['events']['ADD'] == 11500 and after[2]['peak_private_streams'] == 2, 'baseline or workspace bill')
        endpoint = [[(j, alg.serial(a)) for j, a in sorted(row)] for row in after[0]]
        if not rev:
            forward_endpoint = after[:2]
        reports['reverse' if rev else 'forward'] = {
            'baseline': before[2], 'two_private': after[2],
            'arbitrary_input_functions': 661, 'exact_physical_endpoints_equal': True,
            'endpoint_sha256': hashlib.sha256(canonical(endpoint)).hexdigest(),
        }
    # Controls at the real scatter frames, with fresh arbitrary physical inputs there.
    block = new[new_cut[0]:new_cut[1]]
    baseline_block = old[old_cut[0]:old_cut[1]]
    block_args = (word, dims, swaps, alg, initial_cut)
    good = execute(block, *block_args)
    need(good[:2] == execute(baseline_block, *block_args)[:2], 'physical scatter substitution')
    controls = []
    omitted = list(block)
    index = next(i for i, rec in enumerate(omitted) if rec[:4] == (1, 661, 662, -1))
    omitted.pop(index)
    controls.append(reject(lambda: execute(omitted, *block_args), 'restoration omitted: transported ERASE rejects'))
    blind = execute(omitted, *block_args, blind_erase=True)
    need(blind[:2] == good[:2], 'blind deletion control must hide the lifecycle fault')
    controls.append('blind deletion leaves identical persistent functions but is illegal')
    full = swaps[next(i for i, d in enumerate(dims) if d == 8)]
    controls.append(reject(lambda: execute(block, *block_args, wrong_copy=full), 'rank-eight swap at rank-seven COPY'))
    other = swaps[initial_cut[word['ret'][1]]]
    controls.append(reject(lambda: execute(block, *block_args, wrong_copy=other), 'different equal-rank COPY operator'))
    controls.append(reject(lambda: execute(block, *block_args, wrong_copy=alg.identity), 'COPY transport erased'))
    controls.append(reject(lambda: execute(block, *block_args, dirty_slot=True), 'dirty private destination'))
    controls.append(reject(lambda: private_owners(template, word, geo, aliases=True), 'private family alias'))
    controls.append(reject(lambda: private_owners(template, word, geo, reserve=1), 'only one available private family'))
    wrong_move = list(new)
    mi = next(i for i, rec in enumerate(wrong_move) if rec[0] == 0)
    row = list(wrong_move[mi]); row[4] += 1; wrong_move[mi] = tuple(row)
    controls.append(reject(lambda: execute(wrong_move, word, dims, swaps, alg, word['start']), 'underbound or overbound MOVE price'))
    def no_move_pullback():
        flawed = execute(new, word, dims, swaps, alg, word['start'], omit_move_address=True)
        need(flawed[:2] == forward_endpoint, 'MOVE address action changes physical endpoint')
    controls.append(reject(no_move_pullback, 'MOVE address erased with unchanged frame labels and price'))
    # Distinguish the actual maps on address columns, rather than on scalar role columns.
    copy_maps = []
    for center in word['ret']:
        frame = initial_cut[center]
        a, den = alg.maps[swaps[frame]]
        b, full_den = alg.maps[full]
        witness = next(j for j in range(16) if any(a[16*i+j]*full_den != b[16*i+j]*den for i in range(16)))
        copy_maps.append({'center': center, 'frame': frame, 'rank': dims[frame],
                          'address_map': alg.serial(swaps[frame]), 'full_swap_distinguishing_basis_column': witness})
    need(len({canonical(x['address_map']) for x in copy_maps}) == 9, 'COPY maps unexpectedly coincide')
    f = reports['forward']['two_private']['positive_row_bound']
    b = reports['reverse']['two_private']['positive_row_bound']
    local = 64*f**3*b**2
    nine = (1 << 18)*f**5*b**4
    need(local < 1 << 104 and nine < 1 << 192, 'inherited finite algebraic precision guard')
    return {'status': 'PASS_BIT_TWO_COPY_PHYSICAL', 'domain': 'exact physical Boolean streams; arbitrary odd-characteristic address field',
            'partition': [list(x) for x in PARTITION], 'owners': owner_report,
            'copy_address_maps': copy_maps, 'local_physical_replays': reports,
            'copy_rank_sum': 63, 'peak_live_copy_rank': 14, 'local_rank_mass': 5129,
            'scatter_ADDs': {'single': 527, 'two_private': 407},
            'rank_profile_unchanged': True, 'no_new_kappa': True,
            'algebraic_guard': {'F': f, 'B': b, 'local_bits': local.bit_length(), 'nine_stage_bits': nine.bit_length(),
                                'compiler_precision_admission': False},
            'raw6_candidate_sha256': hashlib.sha256(b''.join(struct.pack('<6i', *r) for r in new)).hexdigest(),
            'physical_address_matrices_interned': len(alg.maps),
            'semantic_controls': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', type=Path, help='create a new explicit receipt; never overwrite')
    args = parser.parse_args()
    result = run()
    if args.emit:
        with args.emit.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        expected = json.loads((HERE / 'RESULT.json').read_text())
        need(json.loads(json.dumps(result)) == expected, 'canonical receipt mismatch')
    print('PASS_BIT_TWO_COPY_PHYSICAL functions=661 directions=2 native_MOVEs=2911 COPY_rank=63 private=2/9 descriptors=288 controls=%d no_new_kappa' % len(result['semantic_controls']))


if __name__ == '__main__':
    try:
        main()
    except (Reject, OSError, KeyError, TypeError, ValueError) as exc:
        raise SystemExit('REJECT: ' + str(exc))
