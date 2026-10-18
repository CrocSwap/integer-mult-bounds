#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact dependencies and witnesses for the arbitrary-count equal-price theorem.

No predecessor executable is imported. See README.md for the unrestricted-word
argument: these finite checks do not themselves quantify over all words.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
INPUT_PATH = 'research/universal-connector-boundary/CERTIFICATE.json'
INPUT_SHA = 'e733746ba3e5151c829b4e8728bfff5ae3ed24d8d203eb77c735d20758e8266a'
PATH_FOUR = (0, 4, 5, 1, 3, 7, 6, 14, 28, 16, 0)
# Split PR1370's compound edge 12 into singleton edges 4 and 8.
PATH_TWO = (0, 4, 5, 1, 3, 7, 6, 14, 28, 24, 16, 0)
PATH_TWELVE = (0, 16, 8, 31, 5, 4, 6, 2, 3, 1, 0)
PAIRS_HIST = {16:42, 19:120, 21:180, 22:56, 23:45, 24:220, 26:110, 28:150, 31:22}
NINE_HIST = {22:60, 23:60, 24:810, 26:660, 28:750, 29:260}
EXPECTED_COUNTS = {'four_x':(10,62,4), 'twelve_x':(10,62,12),
                   'extra_source':(12,62,0), 'extra_output':(10,64,0), 'two_x':(11,62,2)}


def need(test, message):
    if not test:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key: '+key)
        result[key] = value
    return result


def read_json(data):
    return json.loads(data, object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def same(actual, expected, label):
    need(canonical(actual) == canonical(expected), label+' mismatch')


def load_input(package=HERE):
    path = package.parent.parent / INPUT_PATH
    need(path.is_file() and not path.is_symlink(), 'input must be a regular nonsymlink file')
    data = path.read_bytes()
    need(sha256(data).hexdigest() == INPUT_SHA, 'retained input changed')
    return read_json(data)


def differences(points):
    return {a ^ b for a in points for b in points}


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            index = value.bit_length()-1
            if index not in pivots:
                pivots[index] = value
                break
            value ^= pivots[index]
    return len(pivots)


def pairing_words(prefix=(), counts=()):
    if len(prefix) == 10:
        yield prefix
        return
    for j, count in enumerate(counts):
        if count == 1:
            yield from pairing_words(prefix+(j,), counts[:j]+(2,)+counts[j+1:])
    if len(counts) < 5:
        yield from pairing_words(prefix+(len(counts),), counts+(1,))


def pairing_census():
    histogram = Counter()
    records = []
    for word in pairing_words():
        q = 0
        points = [0]
        for j in word:
            q ^= 1 << j
            points.append(q)
        need(q == 0, 'pairing did not restore')
        coverage = sorted(differences(points))
        histogram[len(coverage)] += 1
        records.append([list(word), coverage])
    same(dict(histogram), PAIRS_HIST, 'pairing histogram')
    need(len(records) == 945, 'pairing census cardinality')
    return {'count':len(records), 'histogram':dict(sorted(histogram.items())),
            'max_coverage':max(histogram), 'records_sha256':sha256(canonical(records).encode()).hexdigest()}


def nine_point_census():
    fixed = (0,1,2,4,8,16)
    remaining = sorted(set(range(32))-set(fixed))
    histogram = Counter()
    records = []
    for extra in combinations(remaining, 3):
        points = sorted(fixed+extra)
        cover = sorted(differences(points))
        histogram[len(cover)] += 1
        records.append([points,cover])
    same(dict(histogram), NINE_HIST, 'nine-point histogram')
    need(len(records) == 2600, 'nine-point census cardinality')
    return {'count':len(records), 'histogram':dict(sorted(histogram.items())),
            'max_coverage':max(histogram), 'records_sha256':sha256(canonical(records).encode()).hexdigest()}


def source_projection(word):
    rows = [1 << j for j in range(5)]
    for s,t in word:
        need(type(s) is int and type(t) is int and 0 <= s < 5 and 0 <= t < 5 and s != t,
             'invalid elementary source XOR')
        rows[t] ^= rows[s]
    return rows


def shear_census():
    gates = [(s,t) for s in range(5) for t in range(5) if s != t]
    identities = []
    for length in range(4):
        restoring = [w for w in product(gates,repeat=length)
                     if source_projection(w) == [1<<j for j in range(5)]]
        identities.append(len(restoring))
        if length == 2:
            need(all(w[0] == w[1] for w in restoring), 'nonidentical two-X identity')
    same(identities, [1,0,20,0], 'source-restoration census')
    return {'count':sum(20**j for j in range(4)), 'identity_by_length':identities}


def multiplicity_reduction():
    """Corroborate PR1370's written two-X reduction, not interleaving search.

    Rename donor=0,target=1. c is all query-label counts and p counts target
    queries between the two identical XORs. Rank/parity are necessary only.
    """
    survivors = []
    checked = 0
    for c in product(range(11), repeat=5):
        if sum(c) != 10:
            continue
        for p in range(c[1]+1):
            checked += 1
            parity = 0
            directions = []
            for j,n in enumerate(c):
                if j == 1:
                    directions.extend([2]*(n-p)+[3]*p)
                else:
                    directions.extend([1<<j]*n)
            for d in directions:
                parity ^= d
            if parity or rank(directions) != 5:
                continue
            counts = Counter(directions)
            need(len(counts) == 5 and set(counts.values()) == {2},
                 'two-X full-rank ten-query reduction failed')
            survivors.append([list(c),p,sorted(counts)])
    need(bool(survivors), 'missing positive multiplicity cases')
    return {'necessary_cases_checked':checked, 'survivors':survivors}


def minimum_reads(t):
    need(type(t) is int and t >= 0, 'query count is not a nonnegative integer')
    # t=0 actually cannot realize any target; the weak bound 124 remains valid.
    return 124-2*min(31,t*(t-1)//2)


def arithmetic_reduction():
    small = [[t, minimum_reads(t), t+minimum_reads(t)] for t in range(9)]
    need(min(row[2] for row in small) == 76, 'small-query capacity cut')
    # All n<=72 are finite here because r>=62. t=9,r=62 is excluded by
    # the nine-point cover proof. No claim to exhaustive circuit enumeration.
    possible = []
    for t in range(11):
        for r in range(62,73,2):
            if t+r <= 72 and r >= minimum_reads(t):
                if t == 9 and r == 62:
                    continue
                possible.append([t,r])
    same(possible, [[10,62]], 'at-most-72 reduction')
    # 73c+2x is exactly the midpoint of the attainable endpoints. The two
    # exact residual identities certify dominance on the whole positive cone,
    # not merely the rational test values used by test_verify.py.
    midpoint_doubled = [2*73,2*2]
    endpoint_sum = [72+74,4+0]
    same(midpoint_doubled,endpoint_sum,'midpoint coefficient identity')
    return {'t_at_most_eight':small, 'at_most_72_survivors':possible,
            'lower_faces':[[72,4],[73,2],[74,0]],
            'midpoint_doubled_coefficients':midpoint_doubled,
            'switch_x_over_c':[1,2]}


def best_price(c,x):
    need(type(c) in (int,Fraction) and type(x) in (int,Fraction) and c>0 and x>0,
         'positive exact tariff required')
    return min(72*c+4*x,74*c)


def path_word(path):
    need(len(path) >= 2 and path[0] == path[-1] == 0, 'path must close at zero')
    need(all(type(q) is int and 0<=q<32 for q in path), 'invalid path point')
    points = path[:-1]  # closing zero is not a new coefficient point
    reads = [[] for _ in points]
    for mask in range(1,32):
        candidates = [(a,b) for a in range(len(points)) for b in range(a+1,len(points))
                      if points[a]^points[b] == mask]
        need(bool(candidates), 'missing paired-readout mask')
        a,b = candidates[0]
        reads[a].append(('R',mask)); reads[b].append(('R',mask))
    word = []
    for index,(before,after) in enumerate(zip(path,path[1:])):
        word.extend(reads[index])
        active = [j for j in range(5) if ((before^after)>>j)&1]
        need(bool(active), 'zero query edge')
        target = active[0]
        changes = [('X',s,target) for s in active[1:]]
        word.extend(changes); word.append(('Q',target)); word.extend(reversed(changes))
    return word


def retained_word(schedule):
    need(schedule['sources'] == 5 and schedule['rows'] == list(range(1,32)), 'retained interface')
    result = []
    for kind,j in schedule['word']:
        need(type(j) is int, 'retained index type')
        if kind == 'B':
            result.append(('Q',j))
        elif kind == 'A':
            result.append(('R',j+1))
        else:
            raise ValueError('retained alphabet')
    return result


def check_gate(gate):
    need(isinstance(gate,(list,tuple)) and len(gate) in (2,3), 'malformed gate')
    kind = gate[0]
    if kind in ('Q','R'):
        need(len(gate)==2 and type(gate[1]) is int and
             (0<=gate[1]<5 if kind=='Q' else 1<=gate[1]<32), 'invalid Q/R')
    elif kind == 'X':
        need(len(gate)==3 and all(type(v) is int and 0<=v<5 for v in gate[1:])
             and gate[1]!=gate[2], 'invalid X')
    else:
        raise ValueError('unsupported operation')


def tally(word):
    counts = Counter()
    for gate in word:
        check_gate(gate); counts[gate[0]] += 1
    return tuple(counts[k] for k in ('Q','R','X'))


def apply_leaf(state, source, target, operator):
    need(source != target and 0<=source<len(state) and 0<=target<len(state), 'aliased/invalid rows')
    image = {(operator+term,i) for term,i in state[source]}
    state[target].symmetric_difference_update(image)


def echo(source,target,factors,depth=0):
    if len(factors) == 1:
        return [(source,target,(factors[0],))], 0
    cut = len(factors)//2
    work = 37+depth
    need(work not in (source,target) and work<40,'private scratch alias/range')
    right,nr = echo(source,work,factors[:cut],depth+1)
    left,nl = echo(work,target,factors[cut:],depth+1)
    return right+left+list(reversed(right))+list(reversed(left)), 1+2*nr+2*nl


def lower(word):
    leaves = []
    nodes = 0
    for gate in word:
        check_gate(gate)
        kind,j = gate[:2]
        if kind == 'X':
            leaves.append((j,gate[2],()))
        else:
            source,target = (j,5) if kind == 'Q' else (5,5+j)
            name = 'B' if kind == 'Q' else 'A'+str(j)
            local,n = echo(source,target,tuple(name+'.'+str(k) for k in range(5)))
            leaves.extend(local); nodes += n
    return leaves,nodes


def expected_state(expanded=False):
    state = [{((),i)} for i in range(40 if expanded else 37)]
    for m in range(1,32):
        if expanded:
            operator = tuple('A'+str(m)+'.'+str(k) for k in reversed(range(5))) + tuple('B.'+str(k) for k in reversed(range(5)))
        else:
            operator = ('A'+str(m),'B')
        for j in range(5):
            if (m>>j)&1:
                state[5+m].add((operator,j))
    return state


def replay(word, expanded=False, leaves_override=None):
    if expanded:
        leaves,_ = lower(word)
        if leaves_override is not None:
            leaves = leaves_override
        state = [{((),i)} for i in range(40)]
        for source,target,operator in leaves:
            apply_leaf(state,source,target,operator)
    else:
        state = [{((),i)} for i in range(37)]
        for gate in word:
            check_gate(gate)
            if gate[0]=='Q': apply_leaf(state,gate[1],5,('B',))
            elif gate[0]=='R': apply_leaf(state,5,5+gate[1],('A'+str(gate[1]),))
            else: apply_leaf(state,gate[1],gate[2],())
    need(state == expected_state(expanded), 'dirty-input map/restoration failed')
    return state


def witness_receipt(word):
    t,r,s = tally(word)
    replay(word); replay(word,expanded=True)
    leaves,nodes = lower(word)
    need(len(leaves) == 28*(t+r)+s and nodes == 9*(t+r), 'recursive invoice')
    root_calls = t+r+s
    return {'counts':[t,r,s], 'root_word':[list(g) for g in word],
            'map_leaves':28*(t+r), 'source_xors':s, 'internal_nodes':nodes,
            'root_instructions':root_calls, 'borrowed_dirty_rows':4,
            'unit_tariff':28*(t+r)+s+nodes+root_calls}


def build_result(package=HERE):
    inherited = load_input(package)
    words = {'four_x':path_word(PATH_FOUR), 'twelve_x':path_word(PATH_TWELVE)}
    for name in ('extra_source','extra_output'):
        words[name] = retained_word(inherited['schedules']['five_'+name])
    words['two_x'] = path_word(PATH_TWO)
    witnesses = {name:witness_receipt(word) for name,word in words.items()}
    for name,expected in EXPECTED_COUNTS.items():
        same(witnesses[name]['counts'],list(expected),name+' counts')
    same([witnesses[name]['unit_tariff'] for name in words], [2744,2760,2812,2812,2778], 'fixture prices')
    return {'schema_version':1, 'input_sha256':INPUT_SHA,
            'nine_points':nine_point_census(), 'pairings':pairing_census(),
            'source_projections':shear_census(), 'two_x_multiplicities':multiplicity_reduction(),
            'arithmetic':arithmetic_reduction(), 'witnesses':witnesses,
            'theorem':'min(72*c+4*x,74*c), c>0, x>0; equal complete Q/R prices only'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=HERE)
    parser.add_argument('--write-receipt',type=Path,
                        help='explicit external JSON destination; normal verification is read-only')
    args = parser.parse_args()
    package = args.package.resolve()
    result = build_result(package)
    if args.write_receipt:
        output = args.write_receipt.resolve()
        need(output.suffix == '.json' and not output.is_relative_to(package.parent.parent),
             'receipt regeneration must use an external JSON path')
        output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('WROTE',output)
    else:
        receipt = package/'RESULT.json'
        need(receipt.is_file() and not receipt.is_symlink(), 'missing/invalid RESULT.json')
        same(result,read_json(receipt.read_bytes()),'RESULT.json')
    print('PASS_MUTABLE_SOURCE_UNIFORM_TARIFF')
    print('2600 normalized sets; 945 pairings; 8421 source projections; five exact dirty-map witnesses')


if __name__ == '__main__':
    main()
