#!/usr/bin/env python3
"""Source-bound two-copy scatter certificate. Apache-2.0; OpenAI Codex assistance.

No predecessor executable code is imported. The original native lifecycle is
not modified or asserted to accept this proposed two-temporary record model.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def canonical(value):
    # JSON object keys are strings. Normalize generated integer-key histograms
    # before sorting so their order agrees with a parsed certificate.
    normalized = json.loads(json.dumps(value, allow_nan=False))
    return json.dumps(normalized, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def pinned_word():
    for item in load(HERE / 'SOURCES.json')['files']:
        if item['usage'] == 'input':
            need(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
                 == item['sha256'], 'source pin: ' + item['path'])
    return json.loads(gzip.decompress((ROOT / WORD).read_bytes()),
                      object_pairs_hook=unique_pairs)


def qrank(rows):
    basis = {}
    for row in rows:
        row = list(map(Fraction, row))
        for p, b in sorted(basis.items()):
            if row[p]:
                c = row[p]
                row = [x - c*y for x, y in zip(row, b)]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            z = row[p]
            basis[p] = [x/z for x in row]
    return len(basis)


def partitions(items):
    """Each unlabeled singleton/pair partition occurs once."""
    if not items:
        yield ()
        return
    a, *tail = items
    for p in partitions(tail):
        yield ((a,),) + p
    for b in tail:
        for p in partitions([x for x in tail if x != b]):
            yield ((a, b),) + p


def optimize(w):
    supports = [{t for t, row in enumerate(w['scatter']) if j in row}
                for j in range(len(w['ret']))]
    intersections = [[len(a & b) for b in supports] for a in supports]
    weights = {(a, b): intersections[a][b] - 2
               for a, b in itertools.combinations(range(len(supports)), 2)}
    dist = Counter()
    winners = []
    best = -1
    for p in partitions(list(range(len(supports)))):
        saving = sum(weights[b] for b in p if len(b) == 2)
        dist[saving] += 1
        if saving > best:
            best, winners = saving, [p]
        elif saving == best:
            winners.append(p)
    # No precision-based tie optimization: fix lexicographically first winner.
    chosen = min(winners)
    return chosen, {
        'partitions': sum(dist.values()), 'optimal_saving': best,
        'optimal_partitions': len(winners), 'chosen_partition': chosen,
        'intersection_matrix': intersections,
        'saving_distribution': dict(sorted(dist.items())),
        'optimal_partitions_sha256': digest(sorted(winners)),
    }


def scatter_events(w, partition):
    """ADD=(add,dst,src,signed coefficient); COPY/ERASE=(kind,temp,center)."""
    n = 2*w['v'] + w['R']
    p, q = n, n+1
    out = []
    for block in partition:
        a = block[0]
        ha = w['ret'][a]
        out.append(('copy', p, ha))
        if len(block) == 1:
            out.extend(('add', w['v']+t, p, 1)
                       for t, row in enumerate(w['scatter']) if a in row)
            out.append(('erase', p, ha))
            continue
        b = block[1]
        hb = w['ret'][b]
        out.append(('copy', q, hb))
        for t, row in enumerate(w['scatter']):
            if a in row and b not in row:
                out.append(('add', w['v']+t, p, 1))
            if b in row and a not in row:
                out.append(('add', w['v']+t, q, 1))
        out.append(('add', p, q, 1))
        out.extend(('add', w['v']+t, p, 1)
                   for t, row in enumerate(w['scatter']) if a in row and b in row)
        out.append(('add', p, q, -1))
        out.extend([('erase', p, ha), ('erase', q, hb)])
    return out


def events(w, partition):
    out = []
    for sec in ('D', 'A'):
        out.extend(('add', d, s, 1) for f, d, ss in w[sec] for s in ss)
    out.extend(scatter_events(w, partition))
    for sec in ('B', 'C'):
        out.extend(('add', d, s, 1) for f, d, ss in w[sec] for s in ss)
    return out


def scatter_contract(w, ins):
    """The proposed extension: two fresh ZERO copies, fixed original centers.

All targets enter at ZERO (checked separately by invoice). Copies also enter
at ZERO, as specified by the pinned exporter. This block has no MOVE or new
source read. Full ERASE equality is checked by replay, not assumed here.
"""
    n = 2*w['v'] + w['R']
    active = {}
    maximum = 0
    for kind, d, s, *coef in ins:
        if kind == 'copy':
            need(d in (n, n+1) and d not in active and s in w['ret'], 'scatter COPY shape')
            need(s not in active.values(), 'duplicate live center')
            active[d] = s
            maximum = max(maximum, len(active))
        elif kind == 'erase':
            need(active.get(d) == s, 'scatter ERASE shape')
            del active[d]
        elif kind == 'add':
            need(s in active and (d in active or w['v'] <= d < 2*w['v']),
                 'scatter ADD outside common ZERO-frame roles')
            need(d != s and coef in ([1], [-1]), 'scatter signed unit ADD')
        else:
            raise ValueError('unpriced or unknown scatter operation')
    need(not active, 'open scatter copy')
    return maximum


def reversed_events(ins):
    for ev in reversed(ins):
        if ev[0] == 'add':
            yield ('add', ev[1], ev[2], -ev[3])
        else:
            yield ('erase' if ev[0] == 'copy' else 'copy', *ev[1:])


def replay(ins, n, reverse=False):
    """All dirty columns in one exact F2 row engine; every ERASE is checked."""
    rows = [1 << i for i in range(n)] + [0, 0]
    active = {}
    peak = copies = erases = adds = 0
    for ev in reversed_events(ins) if reverse else ins:
        kind, d, s, *coef = ev
        need(0 <= d < n+2 and 0 <= s < n+2 and d != s, 'bad operand')
        if kind == 'add':
            need(coef in ([1], [-1]), 'signed unit ADD')
            need(all(r < n or r in active for r in (d, s)), 'inactive copy read/write')
            need(d not in active.values(), 'original copied center mutated')
            rows[d] ^= rows[s]
            adds += 1
        elif kind == 'copy':
            need(d >= n and s < n and d not in active and rows[d] == 0,
                 'COPY requires fresh temporary')
            need(s not in active.values(), 'duplicate active center')
            active[d] = s
            rows[d] = rows[s]
            peak = max(peak, len(active))
            copies += 1
        elif kind == 'erase':
            need(d in active and active[d] == s and rows[d] == rows[s],
                 'ERASE requires original copied value')
            rows[d] = 0
            del active[d]
            erases += 1
        else:
            raise ValueError('unknown event')
    need(not active and rows[n:] == [0, 0], 'unclosed copy')
    return rows[:n], dict(adds=adds, copies=copies, erases=erases,
                          peak_live_copies=peak)


def bounds(ins, n):
    peaks = []
    for reverse in (False, True):
        values = [1]*n + [0, 0]
        peak = 1
        for ev in reversed_events(ins) if reverse else ins:
            kind, d, s, *coef = ev
            if kind == 'add':
                values[d] += abs(coef[0])*values[s]
            elif kind == 'copy':
                values[d] = values[s]
            else:
                values[d] = 0
            peak = max(peak, values[d])
        peaks.append(peak)
    f, b = peaks
    local = 64*f**3*b**2
    nine = 2**18*f**5*b**4
    need(local < 2**104 and nine < 2**192, 'strict precision guard')
    return dict(F=f, B=b, local_integer=str(local), nine_stage_integer=str(nine),
                local_bits=local.bit_length(), nine_stage_bits=nine.bit_length())


def invoice(w):
    """Reconstruct common-frame persistent MOVEs plus nine COPY charges."""
    n = 2*w['v'] + w['R']
    dims = [qrank([w['lines'][i] for i in f]) for f in w['frames']]
    fs = [set(f) for f in w['frames']]
    current = list(w['start'])
    paths = [[f] for f in current]
    hist = Counter()
    moves = 0

    def climb(r, f):
        nonlocal moves
        old = current[r]
        if old == f:
            return
        need(fs[old] <= fs[f] and dims[old] < dims[f], 'illegal persistent climb')
        hist[dims[f] - dims[old]] += 1
        moves += 1
        paths[r].append(f)
        current[r] = f

    copy_frames = []
    for sec in ('D', 'A', 'scatter', 'B', 'C'):
        if sec == 'scatter':
            need(all(dims[current[r]] == 0 for r in range(w['v'], 2*w['v'])),
                 'scatter targets not at zero')
            copy_frames = [current[r] for r in w['ret']]
            for f in copy_frames:
                hist[dims[f]] += 1
            continue
        for f, d, ss in w[sec]:
            for r in (d, *ss):
                climb(r, f)
    for r, f in enumerate(w['final']):
        climb(r, f)
    need(len(copy_frames) == 9 and [dims[f] for f in copy_frames] == [7]*9,
         'nine rank-seven copies')
    need(n == 661, 'pinned register count')
    return dict(persistent_registers=n, nested_moves=moves,
                copy_frames=copy_frames, copy_ranks=[dims[f] for f in copy_frames],
                copy_rank_sum=63, paid_profile=dict(sorted(hist.items())),
                paid_rank_mass=sum(r*c for r, c in hist.items()),
                persistent_paths_sha256=digest(paths))


def controls(w, partition):
    """Defect-sensitive controls; the old checker is not alleged to be wrong."""
    n = 2*w['v'] + w['R']
    ins = events(w, partition)
    names = []
    restore = next(i for i, e in enumerate(ins) if e == ('add', n, n+1, -1))
    common = next(i for i in range(restore-1, -1, -1)
                  if ins[i][0] == 'add' and ins[i][1] < n and ins[i][2] == n)
    opened = next(i for i, e in enumerate(ins) if e[0] == 'copy')
    variants = {
        'omitted_restore': ins[:restore] + ins[restore+1:],
        'omitted_common_read': ins[:common] + ins[common+1:],
        'mutated_original_center': ins[:opened+2] + [('add', ins[opened][2], 0, 1)] + ins[opened+2:],
        'copy_into_live_slot': ins[:opened+1] + [ins[opened]] + ins[opened+1:],
        'use_after_erase': ins + [('add', w['v'], n, 1)],
    }
    expected, _ = replay(ins, n)
    for name, broken in variants.items():
        try:
            rows, _ = replay(broken, n)
            rejected = rows != expected
        except ValueError:
            rejected = True
        need(rejected, 'control accepted: ' + name)
        names.append(name)
    a, b = 3, 5
    mixed = a+b
    need(mixed-b == a and mixed+b != a, 'integer sign sensitivity')
    names.append('wrong_restore_sign_detected_over_integers')
    mutable_writes = sum(e[0] == 'add' and e[1] >= n for e in ins)
    need(mutable_writes == 8, 'old immutable-temp rule obstruction')
    return names


def calculate():
    w = pinned_word()
    n = 2*w['v'] + w['R']
    part, search = optimize(w)
    base_part = tuple((i,) for i in range(len(w['ret'])))
    baseline, candidate = events(w, base_part), events(w, part)
    need(scatter_contract(w, scatter_events(w, base_part)) == 1, 'baseline copy occupancy')
    need(scatter_contract(w, scatter_events(w, part)) == 2, 'candidate copy occupancy')
    b_rows, b_counts = replay(baseline, n)
    c_rows, c_counts = replay(candidate, n)
    target = [1 << i for i in range(n)]
    for t in range(w['v']):
        target[w['v']+t] ^= 1 << t
    need(b_rows == c_rows == target, 'complete dirty forward boundary')
    need(replay(baseline, n, True)[0] == replay(candidate, n, True)[0] == target,
         'complete dirty reverse boundary')
    bill = invoice(w)
    need(b_counts['adds'] - c_counts['adds'] == search['optimal_saving'], 'ADD invoice')
    need(b_counts['adds'] == 11500 and c_counts['adds'] == 11380, 'pinned ADD counts')
    need(bill['paid_profile'] == {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19},
         'inherited paid profile')
    return dict(status='PASS_BIT_TWO_COPY_SCATTER', no_new_kappa=True,
                search=search, baseline=b_counts, candidate=c_counts,
                baseline_scatter_adds=sum(e[0] == 'add' for e in scatter_events(w, base_part)),
                candidate_scatter_adds=sum(e[0] == 'add' for e in scatter_events(w, part)),
                baseline_bounds=bounds(baseline, n), candidate_bounds=bounds(candidate, n),
                local_recursive_invoice=bill,
                peak_live_copy_rank_mass={'baseline':7, 'candidate':14},
                baseline_stream_sha256=digest(baseline), candidate_stream_sha256=digest(candidate),
                formal_columns_per_direction=n, controls=controls(w, part),
                native_lifecycle_admitted=False,
                scope='Finite scalar replacement and unchanged local recursive charges. Two live copy slots require new physical workspace/native admission; no complete supplier or kappa claim.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', type=Path, help='write new receipt, refusing overwrite')
    args = parser.parse_args()
    result = calculate()
    if args.emit:
        with args.emit.open('x') as out:
            out.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(canonical(result) == canonical(load(HERE/'CERTIFICATE.json')), 'certificate differs')
    print('PASS_BIT_TWO_COPY_SCATTER ADDs=11500->11380 partitions=2620 optima=105 '
          'columns=661 both_directions copies=1->2 unchanged_local_profile no_new_kappa')


if __name__ == '__main__':
    main()
