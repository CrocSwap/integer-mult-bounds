#!/usr/bin/env python3
"""Exact query identity, literal child lowering and full dirty-array invoice.

No constructor or predecessor implementation is imported. Substantial OpenAI
Codex assistance; Apache-2.0. See NOTICE.md for attribution and scope.
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
BASE = 'bbc600db2fc15007b7c914f4f2b2ed55fa909c87'
H = [[1,1,1,1], [1,-1,1,-1], [1,1,-1,-1], [1,-1,-1,1]]
ROLES = 12


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def inverse(word):
    return [[*g[:-1], -g[-1]] for g in reversed(word)]


def queries(word):
    q = [0]*4
    dirt = [0]*4
    rows = [[0]*4 for _ in range(4)]
    counts = {'A':[0]*4, 'B':[0]*4}
    for kind, i, sign in word:
        need(kind in counts and type(i) is int and 0 <= i < 4 and
             type(sign) is int and sign in (-1,1), 'query domain')
        counts[kind][i] += 1
        if kind == 'B':
            q[i] += sign
        else:
            dirt[i] += sign
            for j in range(4):
                rows[i][j] += sign*q[j]
    need(q == [0]*4, 'connector restoration')
    need(dirt == [0]*4, 'output dirt cancellation')
    need(rows == H, 'signed Hadamard identity')
    return counts


def star_words():
    source, output = [], []
    for j in range(4):
        source += [['A',i,-H[i][j]] for i in range(4)]
        source += [['B',j,1]]
        source += [['A',i,H[i][j]] for i in range(4)]
        source += [['B',j,-1]]
    for i in range(4):
        output += [['A',i,-1]]
        output += [['B',j,H[i][j]] for j in range(4)]
        output += [['A',i,1]]
        output += [['B',j,-H[i][j]] for j in reversed(range(4))]
    return source, output


def factor_lists():
    result = {'B':[], 'A':[]}
    next_id = 0
    for kind, lengths in [('B',[1,2,3,4]), ('A',[2,3,4,5])]:
        for length in lengths:
            result[kind].append(list(range(next_id,next_id+length)))
            next_id += length
    return result, next_id


def product(factors, source, target, scratch):
    need(source != target and source not in scratch and target not in scratch,
         'product role alias')
    if len(factors) == 1:
        return [[factors[0], source, target, 1]]
    need(scratch, 'missing product workspace')
    middle, rest = scratch[0], scratch[1:]
    cut = len(factors)//2
    right = product(factors[:cut], source, middle, rest)
    left = product(factors[cut:], middle, target, rest)
    return right + left + inverse(right) + inverse(left)


def lower(word, factors):
    result = []
    for kind, i, sign in word:
        source, target = (i,8) if kind == 'B' else (8,4+i)
        child = product(factors[kind][i], source, target, [9,10,11])
        result += child if sign == 1 else inverse(child)
    return result


def formal(leaves, factors, restore=False):
    initial = [{(r,()):1} for r in range(ROLES)]
    state = copy.deepcopy(initial)
    peak = 1
    for f, source, target, sign in leaves:
        need(0 <= source < ROLES and 0 <= target < ROLES and source != target,
             'leaf role domain')
        for (origin, monomial), coefficient in list(state[source].items()):
            key = origin, (f,*monomial)
            state[target][key] = state[target].get(key,0)+sign*coefficient
            if not state[target][key]:
                del state[target][key]
        peak = max(peak,len(state[target]))
    expected = copy.deepcopy(initial)
    if not restore:
        for i in range(4):
            for j in range(4):
                operator = tuple(reversed(factors['B'][j]+factors['A'][i]))
                expected[4+i][(j,operator)] = H[i][j]
    need(state == expected, 'noncommutative dirty-column endpoint')
    return peak


def matrices(count, length):
    return [[[((f+2)*(i+1)-(j+1)*(f%3+1))*(-1 if (f+i+j)%3 == 0 else 1)
              for j in range(length)] for i in range(length)] for f in range(count)]


def apply(matrix, vector):
    return [sum(a*b for a,b in zip(row,vector)) for row in matrix]


def dense(leaves, factors, count, length):
    mats = matrices(count,length)
    initial = [[(-1 if (r+j)%2 else 1)*(7*r+3*j+2)
                for j in range(length)] for r in range(ROLES)]
    state = copy.deepcopy(initial)
    for matrix in mats:
        need(len(matrix) == length, 'coefficient matrix height')
        for row in matrix:
            need(len(row) == length and all(type(v) is int for v in row),
                 'coefficient row preflight')
            for values in state:
                need(row is not values, 'coefficient/data alias')
    for r in range(ROLES):
        for s in range(r):
            need(state[r] is not state[s], 'data role alias')
    head = travel = maximum = 0
    negatives = 0
    def visit(position):
        nonlocal head, travel
        travel += abs(head-position)
        head = position
    def observe(value):
        nonlocal maximum
        maximum = max(maximum,abs(value).bit_length()+1)
    for row in state:
        for value in row: observe(value)
    for matrix in mats:
        for row in matrix:
            for value in row: observe(value)
    for factor, source, target, sign in leaves:
        for i in range(length):
            total = 0
            for j in range(length):
                visit(ROLES*length+factor*length*length+i*length+j)
                visit(source*length+j)
                term = mats[factor][i][j]*state[source][j]
                total += term
                observe(term); observe(total)
            visit(target*length+i)
            state[target][i] += sign*total
            observe(state[target][i])
            negatives += sign < 0
        visit(0)
    expected = copy.deepcopy(initial)
    for i in range(4):
        for j in range(4):
            value = list(initial[j])
            for factor in factors['B'][j]+factors['A'][i]:
                value = apply(mats[factor],value)
            expected[4+i] = [a+H[i][j]*b for a,b in zip(expected[4+i],value)]
    need(state == expected, 'dense dirty-state endpoint')
    n = len(leaves)
    return {'dimension':length, 'leaf_calls':n, 'coefficient_reads':n*length**2,
            'source_reads':n*length**2, 'target_reads':n*length, 'target_writes':n*length,
            'multiplications':n*length**2, 'additions':n*length*(length+1),
            'sign_negations':negatives, 'tape_travel_word_slots':travel,
            'head_return_after_each_leaf':True, 'trace_signed_word_bits':maximum,
            'dirty_data_words':ROLES*length, 'immutable_coefficient_words':count*length**2,
            'matrix_row_preflight_checks':count*length,
            'data_role_alias_checks':ROLES*(ROLES-1)//2,
            'coefficient_role_alias_checks':count*length*ROLES,
            'leaf_instruction_bits':n*(2*(ROLES-1).bit_length()+(count-1).bit_length()+1),
            'workspace':'four borrowed dirty rows (connector plus three child rows); constant scalar accumulator and paid loop/descriptor state'}


def verify(output=None):
    pins = load(HERE/'SOURCES.json')
    need(pins['base_commit'] == BASE, 'base pin')
    for path, digest in pins['package_sha256'].items():
        need(hashlib.sha256((HERE/path).read_bytes()).hexdigest() == digest,
             'predecessor pin: '+path)
    construction = load(HERE/'CONSTRUCTION.json')
    need(construction['base_commit'] == BASE and construction['assignment_seed'] == 55
         and construction['matrix'] == H, 'construction binding')
    need(construction['format']=='signed-hadamard-batch-seed55/1' and
         construction['B_lengths']==[1,2,3,4] and construction['A_lengths']==[2,3,4,5],
         'product interface binding')
    word = construction['word']
    need(construction['query_calls']==len(word)==22, 'query invoice')
    need([[i,s] for kind,i,s in word if kind=='B']==construction['source_path'],
         'source path binding')
    counts = queries(word)
    need(counts == {'A':[4,4,4,2], 'B':[2,2,2,2]}, 'candidate call profile')
    factors, count = factor_lists()
    source_star, output_star = star_words()
    schedules = {'candidate':word, 'source_stars':source_star, 'output_stars':output_star}
    receipts = {}
    if output:
        output.mkdir(parents=True,exist_ok=False)
    for name, schedule in schedules.items():
        profile = queries(schedule)
        leaves = lower(schedule,factors)
        peak = formal(leaves,factors)
        formal(leaves+inverse(leaves),factors,restore=True)
        if output:
            (output/(name+'-leaves.json')).write_text(json.dumps(leaves)+'\n')
        receipts[name] = {'queries':len(schedule), 'query_profile':profile,
                         'leaf_calls':len(leaves), 'noncommutative_symbolic_peak_terms':peak,
                         'primitive_word_sha256':hashlib.sha256(json.dumps(leaves,separators=(',',':')).encode()).hexdigest(),
                         'leaf_multiplicities':{str(k):v for k,v in sorted(Counter(g[0] for g in leaves).items())},
                         'dense':[dense(leaves,factors,count,length) for length in (2,3)]}
    need(receipts['candidate']['leaf_calls'] == construction['leaf_calls'] == 238,
         'candidate child cost')
    need((receipts['source_stars']['leaf_calls'], receipts['output_stars']['leaf_calls'])
         == (526,364), 'star child costs')
    rejected = []
    def reject(name, action):
        try: action()
        except ValueError: rejected.append(name)
        else: raise ValueError('negative control accepted: '+name)
    bad = copy.deepcopy(word); bad.pop(0)
    reject('omitted_output_dirt_read',lambda:queries(bad))
    bad = copy.deepcopy(word); next(g for g in bad if g[0]=='B')[2] *= -1
    reject('wrong_source_sign',lambda:queries(bad))
    bad = copy.deepcopy(word); bad[-1] = ['B',1,1]
    reject('unrestored_connector',lambda:queries(bad))
    bad = copy.deepcopy(word); bad[0][2] = True
    reject('Boolean_query_sign',lambda:queries(bad))
    leaves = lower(word,factors)
    reject('omitted_product_uncompute',lambda:formal(leaves[:-1],factors))
    bad_factors = copy.deepcopy(factors); bad_factors['A'][3].reverse()
    reject('reversed_noncommuting_factors',lambda:formal(lower(word,bad_factors),factors))
    reject('insufficient_child_scratch',lambda:product(factors['A'][3],8,7,[9,10]))
    reject('connector_in_child_scratch',lambda:product(factors['A'][3],8,7,[8,9,10]))
    prices = {'B':[1,1,1,1],'A':[1000,1000,1000,1]}
    priced = {name:sum(sum(n*c for n,c in zip(info['query_profile'][kind],prices[kind]))
                          for kind in ('A','B')) for name,info in receipts.items()}
    need(priced['candidate'] > priced['output_stars'], 'nonuniform price scope control')
    return {'status':'PASS_SIGNED_HADAMARD_BATCH','base_commit':BASE,'assignment_seed':55,
            'construction_sha256':hashlib.sha256((HERE/'CONSTRUCTION.json').read_bytes()).hexdigest(),
            'matrix':H,'factor_lists':factors,'live_data_roles':ROLES,
            'schedules':receipts,'controls_rejected':rejected,
            'nonuniform_price_control':{'complete_child_prices':prices,'child_costs':priced,
                                       'conclusion':'Candidate need not beat output stars for every positive child price.'},
            'search':construction['search'],'optimality_claim':False,'new_kappa_claim':False,
            'scope':'Exact linear restored query interfaces; fixed signed Hadamard batch, not a selected supplier or a full multiplication theorem.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate',action='store_true')
    parser.add_argument('--replay-search',action='store_true')
    parser.add_argument('--output',type=Path,help='fresh directory for literal primitive programs')
    args = parser.parse_args()
    if args.output: need(not args.output.exists(),'output already exists')
    if args.replay_search:
        with tempfile.TemporaryDirectory(prefix='hadamard-search-') as work:
            rebuilt = Path(work)/'construction.json'
            subprocess.run([sys.executable,'-I','-B',str(HERE/'build.py'),'--output',str(rebuilt)],check=True)
            need(load(rebuilt)==load(HERE/'CONSTRUCTION.json'),'search replay mismatch')
    result = verify(args.output)
    path = HERE/'CERTIFICATE.json'
    if args.write_certificate:
        with path.open('x') as stream:
            json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
    else: need(result==load(path),'certificate mismatch')
    print('PASS_SIGNED_HADAMARD_BATCH queries=22_vs_40 leaf_calls=238_vs_364_vs_526 '
          'dirty_arrays=4 controls=8 no_new_kappa')
