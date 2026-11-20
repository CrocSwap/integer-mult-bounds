"""Independent selected-BIT endpoint, port and cold-entry controls.

Only frozen JSON data are read. No implementation or contributor checker is
imported. Written for Jerry Chen / CubeJerry with OpenAI assistance.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import gzip
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(root, path, digest):
    raw = (root / path).read_bytes()
    need(sha256(raw).hexdigest() == digest, 'source pin: ' + path)
    return json.loads(gzip.decompress(raw))


def reverse_endpoint(word, omit=None):
    """Simultaneous pullback of all output coordinate functionals."""
    n = word['public']
    forms = {i: 1 << i for i in range(n)}
    charts = dict(enumerate(word['final']))
    init_count = clear_count = 0
    for k in range(len(word['program']) - 1, -1, -1):
        event = word['program'][k]
        op, r = event[:2]
        if op == 'CLEAR':
            need(r >= n and r not in forms, 'reverse CLEAR boundary')
            forms[r] = 0
            charts[r] = event[2]
            clear_count += 1
        elif op == 'INIT':
            need(r >= n and charts[r] == event[2], 'reverse INIT chart')
            # Forward INIT inserts zero, so its entire cotangent is discarded.
            del forms[r], charts[r]
            init_count += 1
        elif op == 'MOVE':
            _, r, start, finish = event
            need(charts[r] == finish, 'reverse MOVE continuity')
            charts[r] = start
        elif op == 'ADD':
            _, r, s, chart = event
            need(r != s and charts[r] == charts[s] == chart, 'reverse common ADD chart')
            if k != omit:
                forms[s] ^= forms[r]
        elif op == 'SWAP':
            _, r, s = event
            forms[r], forms[s] = forms[s], forms[r]
            charts[r], charts[s] = charts[s], charts[r]
        else:
            raise ValueError('unknown source operation')
    need(set(forms) == set(range(n)), 'complete reverse owner domain')
    need([charts[i] for i in range(n)] == word['start'], 'full reverse chart return')
    expected = [(1 << i) ^ ((1 << (i + 111)) if i < 111 else 0) for i in range(n)]
    need([forms[i] for i in range(n)] == expected, 'selected transpose endpoint')
    return {'public': n, 'coefficient_positions': n*n, 'events': len(word['program']),
            'off_diagonal_entries': 111, 'independent_helper_returns': n-222,
            'private_init': init_count, 'private_clear': clear_count,
            'transpose_digest': sha256(json.dumps(expected).encode()).hexdigest()}


def determinant(rows):
    a = [list(map(F, row)) for row in rows]
    answer = F(1)
    for c in range(len(a)):
        pivot = next((r for r in range(c, len(a)) if a[r][c]), None)
        need(pivot is not None, 'singular full port basis')
        if pivot != c:
            a[c], a[pivot] = a[pivot], a[c]
            answer = -answer
        p = a[c][c]
        answer *= p
        for r in range(c+1, len(a)):
            multiplier = a[r][c] / p
            a[r] = [x - multiplier*y for x, y in zip(a[r], a[c])]
    return answer


def ports(word, newer):
    need(word['frames'] == newer['frames'], 'entire rational frame equality')
    need(word['start'][:222] == newer['start'][:222] and
         word['final'][:222] == newer['final'][:222], 'entire coupled boundary equality')
    frames = word['frames']
    determinants = []
    for i in range(111):
        hx = frames[str(word['start'][i])]
        fx = frames[str(word['final'][i])]
        hy = frames[str(word['start'][111+i])]
        fy = frames[str(word['final'][111+i])]
        need([r['dim'] for r in (hx, fx, hy, fy)] == [1,8,0,7], 'actual four port ranks')
        u = list(map(F, hx['B'][0]))
        body = [list(map(F, row)) for row in fy['B']]
        norm = sum(x*x for x in u)
        need(norm != 0 and all(sum(x*y for x,y in zip(u,v)) == 0 for v in body),
             'head/body are orthogonal complementary subspaces')
        determinants.append(str(determinant([u] + body)))
        # P_head=u*u^t/(u.u). The source body spans its kernel, so the
        # self-adjoint body projector is I-P_head; no orthonormal body claim.
        p = [[x*y/norm for y in u] for x in u]
        for v in body:
            need(all(sum(a*b for a,b in zip(row,v)) == 0 for row in p), 'body fixed by kernel')
        need([sum(a*b for a,b in zip(row,u)) for row in p] == u, 'actual head fixed')
    return {'equal_frames': len(frames), 'main_quartets': len(determinants),
            'basis_determinants_digest': sha256(json.dumps(determinants).encode()).hexdigest(),
            'proof_endpoint': 'X=D(body)X; Y=D(body)(Y+D(head)X); common port S preserves head and sends body to stage.'}


def reverse_caller(caller, wrong_query=False):
    # Use explicit exponent tuples, never packed lanes or specialized bodies.
    zero = (0,) * 19
    forms = [{zero: 1 << i} for i in range(38)]

    def shifted(row, head=0, bodies=()):
        answer = {}
        for mon, mask in row.items():
            powers = list(mon)
            powers[0] ^= head
            for stage in bodies:
                powers[stage] += 1
            answer[tuple(powers)] = mask
        return answer

    def add(row, other):
        answer = dict(row)
        for mon, mask in other.items():
            answer[mon] = answer.get(mon, 0) ^ mask
            if not answer[mon]:
                del answer[mon]
        return answer

    changed = False
    for event in reversed(caller['events']):
        op = event[0]
        if op == 'LOCAL':
            _, stage, src, dst = event
            dest = shifted(forms[dst], bodies=(stage,))
            forms[src] = add(shifted(forms[src], bodies=(stage,)), shifted(dest,head=1))
            forms[dst] = dest
        elif op in ('ADD','QUERY'):
            _, dst, src = event
            head = int(op == 'QUERY')
            if op == 'QUERY' and wrong_query and not changed:
                head, changed = 0, True
            forms[src] = add(forms[src], shifted(forms[dst],head=head))
        elif op == 'SWAP':
            _, a, b = event
            forms[a], forms[b] = forms[b], forms[a]
        elif op == 'IDLE_ONE':
            _, role, stages = event
            forms[role] = shifted(forms[role], bodies=stages)
        else:
            raise ValueError('unknown caller operation')
    expected = []
    for i, diagonal in enumerate(caller['diagonal']):
        mon = [0]*19
        mon[0] = diagonal['q'] % 2
        for stage in diagonal['stages']:
            mon[stage] += 1
        need(mon[0] == 1 and sum(mon[1:]) > 0, 'positive actual caller output')
        expected.append({tuple(mon): 1 << i})
    need(forms == expected, 'selected free-polynomial transpose caller')
    return {'roles':38, 'coefficient_positions':1444, 'events':len(caller['events']),
            'body_variables':18, 'representation':'explicit 19-integer exponent tuples',
            'q_relation':'q^2=1 only', 'body_relations':'none', 'independent_endpoints':38}


def cylinders():
    L, H, D, T = 4, 3, 3, 2
    W = L*H
    P = T*W**D
    assignments = 0
    for depth in range(D+1):
        groups = defaultdict(dict)
        for root in range(P):
            u, ancestor = root, 0
            lows = []
            for j in range(depth):
                u, digit = divmod(u, W)
                low, high = divmod(digit, H)
                lows.append(low)
                ancestor += high * H**j
            b = u*H**depth + ancestor
            groups[tuple(lows)][b] = root
        for lows, rows in groups.items():
            need(set(rows) == set(range(P//L**depth)), 'whole child volume is V/L^depth')
            by_ancestor = defaultdict(set)
            for b, root in rows.items():
                u, ancestor = divmod(b, H**depth)
                by_ancestor[ancestor].add(u)
                restored = b
                for j in range(depth-1, -1, -1):
                    upper, old_a = divmod(restored, H**j)
                    old_u, high = divmod(upper, H)
                    restored = (old_u*W+lows[j]*H+high)*H**j+old_a
                need(restored == root, 'full independent inverse reconstruction')
                assignments += 1
            need(set(by_ancestor) == set(range(H**depth)), 'all ancestor histories retained')
            need(all(v == set(range(T*W**(D-depth))) for v in by_ancestor.values()),
                 'complete fresh cylinder conditional on each ancestor')
    need(P//L != P//W, 'H>1 catches false child-volume divisor')
    return {'L':L, 'H':H, 'D':D, 'T':T, 'root_rows':P,
            'round_trip_assignments':assignments, 'correct_first_child':P//L,
            'false_discarded_high_child':P//W, 'control_rejected':True}


def cold():
    q, prefix, gap, suffix = 3, 2, 3, 5
    total = 0
    bad_detected = False
    for e in (1,2,3):
        Q = q**e
        addresses = list(product(range(prefix),range(Q),range(gap),range(Q),range(suffix)))
        data = list(addresses)  # Each payload identifies its own original address.
        for position in range(e):
            power = q**position
            buckets = [[] for _ in range(q*q)]
            for address, payload in zip(addresses, data):
                a, b = (address[1]//power)%q, (address[3]//power)%q
                buckets[a*q+b].append(payload)
            cursor = [0]*(q*q)
            output = []
            for address in addresses:
                a, b = (address[1]//power)%q, (address[3]//power)%q
                key = b*q+a
                output.append(buckets[key][cursor[key]])
                cursor[key] += 1
            need(all(cursor[k] == len(buckets[k]) for k in range(q*q)), 'complete bucket retirement')
            if e == 1:
                wrong = [item for bucket in buckets for item in bucket]
                bad_detected = wrong != output
            data = output
            total += len(data)
        need(data == [(p,y,g,x,s) for p,x,g,y,s in addresses], 'complete cold swap with exterior fields')
    need(bad_detected, 'wrong bucket concatenation is observable')
    return {'radix':q, 'widths':[1,2,3], 'prefix':prefix, 'gap':gap, 'suffix':suffix,
            'digit_pass_payload_visits':total, 'wrong_merge_order_control_rejected':True}


def budget():
    C, rho, debit = F('0.0038525298'), F(1,250), F(1,10**10)
    rates = [F(0),F('0.0034'),F('0.0038507'),F('0.00385248')]
    stages = []
    for previous, target in zip(rates, rates[1:]):
        envelope = (1-rho)*C+rho*previous
        need(target < envelope and target < rho and target < 1-rho, 'all three strict root terms')
        stages.append({'previous':str(previous), 'target':str(target),
                       'envelope':str(envelope), 'gap':str(envelope-target)})
    need(F(296630000000000)*debit == 29663, 'correct repaired H_B')
    need(1+F(64,2**45) < 2, 'inflation fits one bit of 29663-bit slack')
    return {'stages':stages, 'cover_log2_slack':29663, 'cover_inflation_below':2}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', required=True, type=Path)
    args = parser.parse_args()
    word = load(args.inputs, 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz',
                '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78')
    newer = load(args.inputs, 'research/grade14-native-realization/retained/data/binary.json.gz',
                 'd28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9')
    caller = load(args.inputs, 'research/paired-query-only-bit/EFREE-CALLER.json.gz',
                  '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b')
    endpoint = reverse_endpoint(word)
    caller_endpoint = reverse_caller(caller)
    first_add = next(i for i,e in enumerate(word['program']) if e[0] == 'ADD')
    try:
        reverse_endpoint(word, first_add)
    except ValueError as err:
        need(str(err) == 'selected transpose endpoint', 'control should fail endpoint, not syntax')
    else:
        raise ValueError('missing native ADD was not detected')
    try:
        reverse_caller(caller, wrong_query=True)
    except ValueError as err:
        need(str(err) == 'selected free-polynomial transpose caller', 'QUERY control endpoint')
    else:
        raise ValueError('QUERY changed to ADD was not detected')
    result = {'status':'PASS_SELECTED_BINARY_COMPLEMENTARY_REVIEW', 'reverse_endpoint':endpoint,
              'reverse_caller':caller_endpoint, 'QUERY_to_ADD_control_rejected':True,
              'port_transfer':ports(word,newer), 'fresh_cylinders':cylinders(),
              'cold_digit_exchange':cold(), 'exact_budget':budget(),
              'omitted_native_ADD_control':{'event':first_add,'rejected':True},
              'scope':'Selected binary algebra and finite controls; separate written source-contract and all-size review.'}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
