#!/usr/bin/env python3
"""Offline reconciliation of the archived PR485 composition prices.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
No supplier engine, optimizer, or historical discovery script is imported.
The eleven-stage recipe follows the credited PR445/472/493 lineage.
This checks frozen local words and aggregate arithmetic, not physical hosting.
"""
import argparse
import copy
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from hashlib import sha1, sha256
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = Path('research/experiment-log/negative-searches/pr485-composition')
TAGS = ('baseline112', 'promoted-0', 'promoted-1', 'promoted-2', 'promoted-3')
SCALE = 1 << 160
TERMS = 128


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lower=0):
    return type(value) is int and value >= lower


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def histogram(value):
    require(isinstance(value, dict), 'histogram object')
    out = {}
    for rank, count in value.items():
        require(isinstance(rank, str) and rank.isdigit() and str(int(rank)) == rank,
                'canonical rank key')
        require(int(rank) > 0 and integer(count, 1), 'positive histogram entry')
        out[int(rank)] = count
    return Counter(out)


def primitive(row):
    common = 0
    for value in row:
        common = gcd(common, value)
    if common:
        common *= 1 if next(x for x in row if x) > 0 else -1
        return tuple(x // common for x in row)
    return tuple(row)


def reduce_row(row, basis):
    row = tuple(row)
    for pivot, vector in basis:
        if row[pivot]:
            row = primitive(tuple(vector[pivot] * x - row[pivot] * y
                                  for x, y in zip(row, vector)))
    return row


def echelon(rows):
    """Fraction-free rational row space; no finite-field rank shortcut."""
    basis = []
    for original in rows:
        row = reduce_row(original, basis)
        if any(row):
            pivot = next(i for i, x in enumerate(row) if x)
            basis.append((pivot, primitive(row)))
            basis.sort()
    return tuple(basis)


@lru_cache(maxsize=8)
def frame_geometry(lines, frames):
    require(len(lines) == 120 and all(len(row) == 8 for row in lines), 'root dimensions')
    require(all(type(x) is int for row in lines for x in row), 'integer root coordinates')
    require(all(any(row) for row in lines), 'nonzero roots')
    dims, masks = [], []
    for frame in frames:
        require(len(set(frame)) == len(frame) and
                all(integer(i) and i < 120 for i in frame), 'frame root indices')
        basis = echelon(lines[i] for i in frame)
        mask = sum(1 << i for i, row in enumerate(lines) if not any(reduce_row(row, basis)))
        dims.append(len(basis))
        masks.append(mask)
    return tuple(dims), tuple(masks)


def local_replay(word):
    require((word['format'], word['h'], word['v'], word['R'], word['coords'], word['form']) ==
            ('bitE8/1', 8, 120, 715, 'ham', '<x,y>/2'), 'word format and dimensions')
    dims, masks = frame_geometry(tuple(map(tuple, word['lines'])), tuple(map(tuple, word['frames'])))
    n, v, full = 955, 120, (1 << 120) - 1
    for key in ('start', 'final'):
        require(len(word[key]) == n and all(integer(f) and f < len(masks) for f in word[key]),
                'boundary frame indices')
    current = [masks[f] for f in word['start']]
    dimensions = [dims[f] for f in word['start']]
    require(all(current[i] == sum(1 << j for j, row in enumerate(word['lines'])
                                 if not any(reduce_row(row, echelon([word['lines'][i]]))))
                for i in range(v)), 'input line frames')
    require(not any(current[v:2*v]), 'target zero entrances')
    values = [1 << i for i in range(n)]  # every arbitrary dirty input simultaneously
    supports = [1 << i if i < v else 0 for i in range(n)]  # positive integer x-support
    paid = Counter()
    additions = visits = 0

    def visit(register, frame):
        nonlocal visits
        require(integer(register) and register < n, 'register index')
        require(not current[register] & ~masks[frame], 'non-nested frame transition')
        delta = dims[frame] - dimensions[register]
        if delta:
            require(delta > 0, 'positive frame increment')
            paid[delta] += 1
            visits += 1
        current[register], dimensions[register] = masks[frame], dims[frame]

    def gates(phase):
        nonlocal additions
        for frame, destination, sources in word[phase]:
            require(integer(frame) and frame < len(masks), 'gate frame index')
            require(integer(destination, v) and destination < n and destination not in sources,
                    'gate destination')
            require(len(set(sources)) == len(sources), 'distinct gate sources')
            # Empty-source records still move the destination's frame.
            for register in [destination] + sources:
                visit(register, frame)
            for source in sources:
                if source < v or source >= 2*v:
                    require(not supports[source] & ~masks[frame], 'integer operand support')
                require(not (destination >= 2*v and v <= source < 2*v),
                        'target-to-helper outside this replay contract')
                values[destination] ^= values[source]
                supports[destination] |= supports[source]
                additions += 1
            if destination >= 2*v:
                require(not supports[destination] & ~masks[frame], 'integer helper support')

    gates('D')
    require(current == [masks[f] for f in word['start']], 'compensation changes a frame')
    gates('A')
    require(not any(current[v:2*v]), 'scatter at nonzero target frame')
    retained = word['ret']
    require(len(retained) == 9 and len(set(retained)) == 9 and
            all(integer(q, 2*v) and q < n for q in retained), 'retained total indices')
    require(len(word['scatter']) == v, 'scatter target count')
    for q in retained:
        require(dimensions[q] > 0, 'nonzero copied total')
        paid[dimensions[q]] += 1
    for t, row in enumerate(word['scatter']):
        require(len(set(row)) == len(row) and all(integer(k) and k < 9 for k in row), 'scatter indices')
        for k in row:
            values[v+t] ^= values[retained[k]]
            supports[v+t] |= supports[retained[k]]
    gates('B')
    gates('C')
    for i, frame in enumerate(word['final']):
        visit(i, frame)
    require(all(current[i] == full for i in list(range(v)) + list(range(2*v, n))), 'full final frames')
    for t, line in enumerate(word['lines']):
        perpendicular = sum(1 << j for j, row in enumerate(word['lines'])
                            if sum(x*y for x, y in zip(line, row)) == 0)
        require(current[v+t] == perpendicular, 'target perpendicular cap')
    expected = [(1 << i) ^ ((1 << (i-v)) if v <= i < 2*v else 0) for i in range(n)]
    require(values == expected, 'arbitrary-dirty scalar map')
    widths = [8-dims[f] for f in word['start'][2*v:]]
    require(all(width > 0 for width in widths), 'positive residual widths')
    return {'profile': paid, 'widths': widths, 'columns': n, 'frames': len(dims),
            'additions': additions, 'frame_moves': visits, 'copy_calls': len(retained)}


def selection_provenance(original, selection, word, row):
    """Bind the archived donor list and promotion log to the literal entrances.

    Does not reconstruct the full constructor or certify how the deleted ADDs
    were discovered; local_replay checks the resulting frozen word separately.
    """
    entries = copy.deepcopy(original)
    by_pivot = {entry[1]: entry for entry in entries}
    require(len(entries) == len(by_pivot) == 112, 'distinct original pivots')
    for move in selection['moves']:
        require(move['pivot'] in by_pivot, 'promotion pivot')
        entry = by_pivot[move['pivot']]
        require(entry[0] == move['old'] and set(move['old']) < set(move['new']),
                'promotion log does not extend entrance')
        entry[0] = move['new']
    require(entries == selection['entries'], 'promotion log/selection mismatch')
    dims, _ = frame_geometry(tuple(map(tuple, word['lines'])), tuple(map(tuple, word['frames'])))
    donors = set()
    entrance_rank = 0
    for entrance, pivot, sources in entries:
        require(integer(pivot, 240) and pivot < 955 and
                all(integer(s, 240) and s < 955 for s in sources), 'selection register')
        require(entrance == word['frames'][word['start'][pivot]], 'selected entrance/word mismatch')
        entrance_rank += dims[word['start'][pivot]]
        donors.update(sources)
    nonzero_entrances = {i for i in range(240, 955) if dims[word['start'][i]]}
    require(nonzero_entrances == set(by_pivot), 'unrecorded helper entrance')
    require((row['pivots'], row['entrance_rank'], row['donors']) ==
            (112, entrance_rank, len(donors)), 'selection counts/ledger mismatch')
    return {'pivots': 112, 'entrance_rank': entrance_rank, 'donors': len(donors),
            'recorded_promotions': len(selection['moves'])}


def idle_windows():
    """Reconstruct the K=5 paired-chain timeline; backward-scan each idle window."""
    timeline = [('local', 0, 0)]
    levels = [0, -1, -1, -1, -1]
    idle_index = 0
    for pair in range(5):
        for reverse in (True, False):
            stage = 2*pair + (1 if reverse else 2)
            require(levels[pair] == stage-1, 'paired-chain levels')
            timeline.append(('local', stage, pair))
            levels[pair] = stage
            advances = []
            if pair < 4:
                other = pair+1
                advances.append((other, 7*(stage-levels[other])))
                levels[other] = stage
            else:
                if not reverse:
                    advances = [(j, 7*(10-levels[j])) for j in range(5)]
                    levels = [10]*5
            for other, rank in advances:
                timeline.append(('idle', idle_index, other, rank))
                idle_index += 1
            if pair < 4:
                timeline.append(('bridge', pair, pair+1))
    windows = {}
    for pos, event in enumerate(timeline):
        if event[0] != 'idle':
            continue
        _, index, owner, capacity = event
        stages = []
        for prior in reversed(timeline[:pos]):
            if (prior[0] == 'local' and prior[2] == owner) or (
                    prior[0] == 'bridge' and owner in prior[1:]):
                break
            if prior[0] == 'local':
                stages.append(prior[1])
        if capacity > 0 and stages:
            windows[index] = (owner, capacity, tuple(sorted(stages)))
        else:
            require(capacity == 0, 'positive unhosted idle term')
    require(len(windows) == 12, 'twelve positive idle windows')
    return windows


def aggregate(local, selection, replicas):
    require(integer(replicas, 1), 'positive replica count')
    require(set(selection) == {'bit'}, 'bit selection')
    selection = selection['bit']
    windows = idle_windows()
    widths = Counter(local['widths'])
    slots, demand, supplied, used = Counter(), Counter(), Counter(), Counter()
    paid = Counter({r: count*11*replicas for r, count in local['profile'].items()})
    pattern_keys, stage_keys = set(), set()
    for index, pattern, count in selection['patterns']:
        require(integer(index) and index in windows and integer(count, 1), 'pattern index/count')
        require(all(integer(w, 1) and w in widths for w in pattern), 'pattern widths')
        key = (index, tuple(sorted(pattern)))
        require(key not in pattern_keys, 'duplicate pattern')
        pattern_keys.add(key)
        residual = windows[index][1] - sum(pattern)
        require(residual >= 0, 'pattern exceeds capacity')
        slots[index] += count
        for width in pattern:
            demand[index, width] += count
        if residual:
            paid[residual] += count
    for index, width, stage, count in selection['stages']:
        require(integer(index) and index in windows and integer(stage) and
                stage in windows[index][2], 'stage outside idle window')
        require(integer(width, 1) and width in widths and integer(count, 1), 'stage width/count')
        key = (index, width, stage)
        require(key not in stage_keys, 'duplicate stage allocation')
        stage_keys.add(key)
        supplied[index, width] += count
        used[stage, width] += count
    require(slots == Counter({i: 240*replicas for i in windows}), 'copy conservation')
    require(demand == supplied, 'pattern/width conservation')
    require(used == Counter({(s, w): count*replicas for s in range(11)
                             for w, count in widths.items()}), 'stage/width conservation')
    mass = sum(rank*count for rank, count in paid.items())
    require(78*1200*replicas - mass == 408*replicas, 'aggregate rank deficit')
    return paid


def ceil_div(a, b):
    return -(-a // b)


@lru_cache(maxsize=256)
def unit_power(base, saving):
    """Enclose base**saving by a positive binomial series, 1 <= base <= 2."""
    require(Fraction(1) <= base <= 2 and 0 < saving < 1, 'binomial domain')
    t = 1 - 1/base
    lo = hi = total_lo = total_hi = SCALE
    for n in range(1, TERMS+1):
        numerator = (saving.numerator + (n-1)*saving.denominator)*t.numerator
        denominator = saving.denominator*n*t.denominator
        lo = lo*numerator // denominator
        hi = ceil_div(hi*numerator, denominator)
        total_lo += lo
        total_hi += hi
    numerator = (saving.numerator + TERMS*saving.denominator)*t.numerator
    denominator = saving.denominator*(TERMS+1)*t.denominator
    next_upper = ceil_div(hi*numerator, denominator)
    # All later term ratios are <= t <= 1/2 because 0 < saving < 1.
    tail = ceil_div(next_upper*t.denominator, t.denominator-t.numerator)
    return total_lo, total_hi+tail


def power_bounds(base, saving):
    k = 0
    while base > 2:
        base /= 2
        k += 1
    lo, hi = unit_power(base, saving)
    two_lo, two_hi = unit_power(Fraction(2), saving)
    for _ in range(k):
        lo = lo*two_lo // SCALE
        hi = ceil_div(hi*two_hi, SCALE)
    return Fraction(lo, SCALE), Fraction(hi, SCALE)


def moment_bounds(profile, replicas, saving, fallback=True):
    m, stock = 78, 1200*replicas
    lo = hi = Fraction(0)
    for rank, count in profile.items():
        require(integer(rank, 1) and rank < m and integer(count, 1), 'proper paid child')
        a, b = power_bounds(Fraction(m, rank), saving)
        coefficient = Fraction(rank*count, m*stock)
        lo += coefficient*a
        hi += coefficient*b
    if fallback:
        a, b = power_bounds(Fraction(m), saving)
        coefficient = Fraction(32*m*sum(profile.values()), 10**16*stock)
        lo += coefficient*a
        hi += coefficient*b
    return lo, hi


def check_price(local, selection, result):
    replicas = result['replicas']
    paid = aggregate(local, selection, replicas)
    require(paid == histogram(result['profile']), 'archived aggregate profile differs')
    lower, upper = Fraction(result['bit_lower']), Fraction(result['bit_upper'])
    require(upper-lower == Fraction(1, 10**24), 'adjacent endpoint grid')
    lower_bounds = moment_bounds(paid, replicas, lower)
    upper_bounds = moment_bounds(paid, replicas, upper)
    require(lower_bounds[1] < 1 < upper_bounds[0], 'moment endpoint signs')
    projection = lower/(1+lower)
    # This is a historical float report; the reconstructed result stays rational.
    require(abs(Fraction(str(result['projected_kappa']))-projection) < Fraction(1, 10**18),
            'projected arithmetic differs')
    require(projection < Fraction(1296611982495107, 10**18), 'historical no-gain comparison')
    return {'replicas': replicas, 'profile': dict(sorted(paid.items())),
            'rank_mass': sum(r*c for r, c in paid.items()), 'deficit': 408*replicas,
            'bit_lower': str(lower), 'bit_upper': str(upper),
            'lower_endpoint_margin': str(1-lower_bounds[1]),
            'upper_endpoint_margin': str(upper_bounds[0]-1),
            'projected_kappa_exact': str(projection), 'below_archived_comparator': True}


def check_sources(root, manifest):
    root = root.resolve()
    require(manifest['files'], 'empty source inventory')
    for name, digest in manifest['files'].items():
        path = (root / name).resolve()
        require(root in path.parents and path.is_file(), 'missing or escaped source: '+name)
        require(sha256(path.read_bytes()).hexdigest() == digest, 'source bytes changed: '+name)


def reconcile(root=ROOT):
    manifest = read_json(HERE/'SOURCE.json')
    check_sources(root, manifest)
    archive = root/ARCHIVE
    source_index = read_json(archive/'source485-package-index.json')
    require(source_index['commit'] == manifest['archive_pr485_source_commit'], 'historical PR485 commit')
    source_rows = [r for r in source_index['files'] if
                   r['path'] == 'research/e8-r715-kernel-cap/data/kernel-selection.json']
    require(len(source_rows) == 1, 'historical kernel selection inventory')
    kernel_raw = (archive/'PR485-KERNEL-SELECTION.json').read_bytes()
    blob = sha1(b'blob '+str(len(kernel_raw)).encode('ascii')+b'\0'+kernel_raw).hexdigest()
    require(source_rows[0]['sha'] == blob and source_rows[0]['size'] == len(kernel_raw),
            'historical kernel selection Git blob')
    original = json.loads(kernel_raw)
    ledger = read_json(archive/'local/LEDGER.json')
    prices = read_json(archive/'pricing/COMPLETE.json')
    require([row['tag'] for row in ledger] == list(TAGS), 'complete ordered local ledger')
    require(read_json(archive/'local/COMPLETE.json') == {'status': 'FINISHED', 'cases': 5},
            'local completion')
    require(prices['status'] == 'FINISHED' and [row['tag'] for row in prices['cases']] == list(TAGS),
            'complete ordered price ledger')
    seen, cases, aliases = {}, {}, {}
    for row, price_row in zip(ledger, prices['cases']):
        tag = row['tag']
        raw = (archive/'local'/tag/'WORD.json').read_bytes()
        digest = sha256(raw).hexdigest()
        require(digest == row['word_sha256'], 'word digest differs from local ledger')
        require(row == read_json(archive/'local'/tag/'RESULT.json'), 'local result/ledger mismatch')
        word = json.loads(raw)
        provenance = selection_provenance(original, read_json(archive/'local'/tag/'SELECTION.json'), word, row)
        if digest in seen:
            alias_target = seen[digest]
            require(price_row == {'tag': tag, 'status': 'IDENTICAL_WORD_REUSES_EXACT_PRICE',
                                  'same_as': alias_target}, 'unjustified duplicate price reuse')
            require(histogram(row['profile']) == cases[alias_target]['local']['profile'],
                    'duplicate local profile differs')
            aliases[tag] = alias_target
            continue
        seen[digest] = tag
        local = local_replay(word)
        require(local['profile'] == histogram(row['profile']), 'local paid profile differs')
        local_path = archive/'pricing'/(tag+'-LOCAL.json')
        priced_local = read_json(local_path)
        require(local['profile'] == histogram(priced_local['profile']) and
                local['widths'] == priced_local['widths'], 'word-to-price input mismatch')
        result = read_json(archive/'pricing'/tag/'RESULT.json')
        require(result['source_local_sha256'] == sha256(local_path.read_bytes()).hexdigest(),
                'price source digest')
        require(price_row == {key: tag if key == 'tag' else result[key]
                              for key in ('tag', 'status', 'replicas', 'projected_kappa', 'bit_lower')},
                'price completion/result mismatch')
        price = check_price(local, read_json(archive/'pricing'/tag/'SELECTION.json'), result)
        cases[tag] = {'word_sha256': digest, 'selection': provenance,
                      'local': {**local, 'widths': dict(sorted(Counter(local['widths']).items()))},
                      'price': price}
    require(len(cases) == 2 and len(aliases) == 3, 'five variants/two distinct words')
    return {'status': 'PASS_PR485_ARCHIVED_AGGREGATE_PRICES',
            'base_commit': manifest['base_commit'], 'assignment_seed': 98,
            'historical_selection_git_blob': blob,
            'cases': cases, 'duplicate_price_reuse': aliases,
            'windows': idle_windows(), 'arithmetic': {'method': 'positive binomial series',
                'terms': TERMS, 'outward_dyadic_bits': 160, 'fallback_probability': '1/10000000000000000'},
            'scope': 'Two frozen local words and aggregate prices only. No physical owner expansion, native/global replay, precision invoice, outer assembly, optimizer rerun, or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--write-receipt', type=Path, help='write a fresh receipt; never overwrite')
    args = parser.parse_args()
    result = reconcile(args.root)
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.write_receipt:
        with args.write_receipt.open('x', encoding='utf-8') as handle:
            handle.write(text)
    else:
        require(json.loads(text) == read_json(HERE/'EXPECTED.json'), 'committed receipt differs')
    print('PASS_PR485_ARCHIVED_AGGREGATE_PRICES variants=5 words=2 reuses=3 replicas=21,84 columns=955')


if __name__ == '__main__':
    main()
