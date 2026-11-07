#!/usr/bin/env python3
"""Exact source-bound two-coefficient obstruction. Standard library only.

Jerry Chen / @CubeJerry with substantial OpenAI assistance; Apache-2.0.
Native event meanings and source word are credited in NOTICE. This verifier
implements the response calculation directly, without predecessor imports.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(dst, src, coefficient=Q(1)):
    for column, value in src.items():
        result = dst.get(column, Q(0)) + coefficient * value
        if result:
            dst[column] = result
        else:
            dst.pop(column, None)


def source(event):
    return event[1] if event[0] == 'SCALE' else event[2]


def coefficient(event):
    return Q(event[2] if event[0] == 'SCALE' else event[3])


def scalar_event(event):
    return event[0] in ('ADD', 'COPY', 'SCALE')


def rows_step(rows, event):
    op, dst = event[:2]
    if op == 'ADD':
        add(rows[dst], rows[event[2]], coefficient(event))
    elif op == 'COPY':
        rows[dst] = {j: coefficient(event) * x for j, x in rows[event[2]].items() if coefficient(event) * x}
    elif op == 'SCALE':
        rows[dst] = {j: coefficient(event) * x for j, x in rows[dst].items() if coefficient(event) * x}
    elif op in ('INIT', 'CLEAR'):
        rows[dst] = {}
    else:
        need(op == 'MOVE', ('unknown event', event))


def literal(program, public, owned=0, record_prefix=False):
    rows = [{i: Q(1)} if i < public else {} for i in range(public + owned)]
    prefix = {}
    for index, event in enumerate(program):
        if record_prefix and scalar_event(event):
            prefix[index] = dict(rows[source(event)])
        rows_step(rows, event)
    return rows[:public], prefix


def responses(program, public, owned):
    effects = [{i: Q(1)} if i < public else {} for i in range(public + owned)]
    suffix = {}
    for index in range(len(program) - 1, -1, -1):
        event = program[index]
        op, dst = event[:2]
        if scalar_event(event):
            suffix[index] = dict(effects[dst])
        if op == 'ADD':
            add(effects[event[2]], effects[dst], coefficient(event))
        elif op == 'COPY':
            add(effects[event[2]], effects[dst], coefficient(event))
            effects[dst] = {}
        elif op == 'SCALE':
            effects[dst] = {j: coefficient(event) * x for j, x in effects[dst].items() if coefficient(event) * x}
        elif op in ('INIT', 'CLEAR'):
            effects[dst] = {}
    return suffix


def source_check(word):
    public = word['public']
    frames = []
    for basis in word['frames']:
        span = {0}
        for vector in basis:
            span |= {x ^ vector for x in list(span)}
        need(len(span) == 1 << len(basis), 'dependent frame basis')
        need(all(0 <= x < 512 for x in span), 'frame outside binary dimension nine')
        frames.append(frozenset(span))
    dimension = [len(basis) for basis in word['frames']]
    current = {r: word['initial'][r] for r in range(public)}
    rows = [{r: Q(1)} if r < public else {} for r in range(public + word['owned_fields'])]
    for index, event in enumerate(word['program']):
        op, dst = event[:2]
        if op == 'MOVE':
            a, b, own = event[2:]
            need(current.get(dst) == a and own == (dst >= public), ('MOVE source/ownership', index))
            need(frames[b] < frames[a] if own else frames[a] < frames[b], ('MOVE direction', index))
            current[dst] = b
        elif op == 'INIT':
            need(dst >= public and current.get(dst) is None, ('INIT lifetime', index))
            current[dst] = event[2]
        elif op == 'CLEAR':
            need(dst >= public and current.get(dst) == event[2], ('CLEAR lifetime', index))
            current[dst] = None
        else:
            need(scalar_event(event), ('scalar operation', index))
            registers = [dst] if op == 'SCALE' else [dst, event[2]]
            need(len(set(registers)) == len(registers), ('aliased event', index))
            need(all(current.get(r) == event[-1] for r in registers), ('co-rest', index))
            value = coefficient(event)
            need(value != 0 and value.denominator & (value.denominator - 1) == 0, ('nonzero dyadic scalar', index))
            if op == 'SCALE':
                numerator = abs(value.numerator)
                need(numerator & (numerator - 1) == 0, ('SCALE unit', index))
            if op == 'COPY':
                need(dst >= public and not rows[dst], ('COPY zero', index))
        rows_step(rows, event)
    need(all(current[r] == word['final'][r] for r in range(public)), 'public final frames')
    need(all(current.get(r) is None for r in range(public, len(rows))), 'unclosed owned lifetime')
    expected = [{r: Q(1)} for r in range(public)]
    for port in word['live']:
        expected[port + 112][port] = Q(1)
    need(rows[:public] == expected, 'source public endpoint')
    K = {r for r in range(public) if dimension[word['initial'][r]] == 0}
    R = {r for r in range(public) if dimension[word['final'][r]] == 9}
    return expected, dimension, K, R


def visits(program, dimension):
    prior, contacts, scales = {}, defaultdict(list), defaultdict(list)
    answer = defaultdict(list)
    for index, event in enumerate(program):
        op, role = event[:2]
        if op == 'MOVE':
            if role in prior and len(contacts[role]) == 1:
                gate = contacts[role][0]
                first = program[prior[role]]
                ranks = [abs(dimension[first[3]] - dimension[first[2]]), abs(dimension[event[3]] - dimension[event[2]])]
                if program[gate][0] == 'ADD' and all(ranks):
                    answer[gate].append({'role': role, 'first': prior[role], 'second': index,
                                         'scales': scales[role][:], 'ranks': ranks})
            prior[role], contacts[role], scales[role] = index, [], []
        elif op in ('INIT', 'CLEAR'):
            prior.pop(role, None)
            contacts[role], scales[role] = [], []
        elif op == 'SCALE':
            scales[role].append(index)
        else:
            for r in (role, event[2]):
                contacts[r].append(index)
    return dict(answer)


def direction(vector, allowed):
    entries = sorted((r, value) for r, value in vector.items() if r in allowed)
    if not entries:
        return None, Q(0)
    scale = entries[0][1]
    return tuple((r, value / scale) for r, value in entries), scale


def complete_filter(deleted, gates, prefix, suffix, Rbar, Kbar):
    both, only_u, only_v = defaultdict(list), defaultdict(list), defaultdict(list)
    signatures, factors = {}, {}
    for gate in gates:
        u, a = direction(suffix[gate], Rbar)
        v, b = direction(prefix[gate], Kbar)
        signatures[gate], factors[gate] = (u, v), (a, b)
        if u is not None and v is not None:
            both[u, v].append(gate)
        elif u is not None:
            only_u[u].append(gate)
        elif v is not None:
            only_v[v].append(gate)
    pairs = set()
    kinds = Counter()
    for gate in deleted:
        u, v = signatures[gate]
        need(u is not None and v is not None, ('deletion has zero boundary derivative', gate))
        for other in both[u, v]:
            if other != gate:
                pairs.add((gate, other))
        pairs.update((gate, other) for other in only_u[u] if other > gate)
        pairs.update((gate, other) for other in only_v[v] if other < gate)
    for deleted_gate, other in pairs:
        u, v = signatures[other]
        kinds['both_nonzero' if u is not None and v is not None else 'zero_original_boundary_derivative'] += 1
    return sorted(pairs), factors, dict(kinds)


def transfers(program, pairs):
    requested = defaultdict(set)
    for deleted, other in pairs:
        a, b = sorted((deleted, other))
        requested[a].add(b)
    answer = {}
    for a, later in requested.items():
        column = {program[a][1]: Q(1)}
        for index in range(a + 1, max(later) + 1):
            event = program[index]
            if index in later:
                answer[a, index] = column.get(source(event), Q(0))
            op, dst = event[:2]
            if op == 'ADD':
                value = column.get(dst, Q(0)) + coefficient(event) * column.get(event[2], Q(0))
            elif op == 'COPY':
                value = coefficient(event) * column.get(event[2], Q(0))
            elif op == 'SCALE':
                value = coefficient(event) * column.get(dst, Q(0))
            elif op in ('INIT', 'CLEAR'):
                value = Q(0)
            else:
                continue
            if value:
                column[dst] = value
            else:
                column.pop(dst, None)
    return answer


def dot(row, column):
    return sum((value * column.get(i, Q(0)) for i, value in row.items()), Q(0))


def inverse_endpoint_column(column, ports):
    answer = dict(column)
    for port in ports:
        value = answer.get(port + 112, Q(0)) - answer.get(port, Q(0))
        if value:
            answer[port + 112] = value
        else:
            answer.pop(port + 112, None)
    return answer


def solve_pair(program, deleted, other, factors, transfer):
    a, b = sorted((deleted, other))
    au, av = factors[a]
    bu, bv = factors[b]
    tau = transfer[a, b]
    if deleted == a:
        alpha = -coefficient(program[a])
        denominator = bu * bv + alpha * tau * bu * av
        numerator = -alpha * au * av
        need(numerator != 0, 'zero right side for deleted first event')
        if not denominator:
            return None
        beta = numerator / denominator
        replacement = coefficient(program[b]) + beta
    else:
        beta = -coefficient(program[b])
        denominator = au * av + beta * tau * bu * av
        numerator = -beta * bu * bv
        need(numerator != 0, 'zero right side for deleted second event')
        if not denominator:
            return None
        alpha = numerator / denominator
        replacement = coefficient(program[a]) + alpha
    need(alpha * au * av + beta * bu * bv + alpha * beta * tau * bu * av == 0, 'pair boundary equation')
    return a, b, alpha, beta, tau, replacement


def null_witness(solution, prefix, suffix, ports):
    a, b, alpha, beta, tau, replacement = solution
    u1 = inverse_endpoint_column({i: alpha * x for i, x in suffix[a].items()}, ports)
    u2 = inverse_endpoint_column({i: beta * x for i, x in suffix[b].items()}, ports)
    v1, v2 = prefix[a], dict(prefix[b])
    add(v2, v1, alpha * tau)
    B = [[1 + dot(v1, u1), dot(v1, u2)], [dot(v2, u1), 1 + dot(v2, u2)]]
    need(B[0][0] * B[1][1] - B[0][1] * B[1][0] == 0, 'a nonsingular candidate survives')
    row = B[0] if any(B[0]) else B[1]
    z = [-row[1], row[0]] if any(row) else [Q(1), Q(0)]
    need(all(dot(dict(enumerate(r)), dict(enumerate(z))) == 0 for r in B), '2x2 kernel')
    witness = {}
    add(witness, u1, z[0])
    add(witness, u2, z[1])
    need(witness, 'null witness must be nonzero')
    return witness


def altered(program, deleted, other, replacement):
    answer = []
    for index, event in enumerate(program):
        if index == deleted:
            continue
        event = list(event)
        if index == other:
            event[2 if event[0] == 'SCALE' else 3] = str(replacement)
        answer.append(event)
    return answer


def check_null(rows, witness):
    need(witness and all(dot(row, witness) == 0 for row in rows), 'literal nonzero null witness')


def control_error(action):
    try:
        action()
    except ValueError:
        return True
    raise ValueError('negative control unexpectedly accepted')


def controls():
    # A deletion really can be repaired by another coefficient in a different word.
    program = [['ADD', 1, 0, '1'], ['ADD', 1, 0, '2']]
    original, prefix = literal(program, 2, record_prefix=True)
    suffix = responses(program, 2, 0)
    pairs, factors, _ = complete_filter([0], [0, 1], prefix, suffix, {1}, {0})
    need(pairs == [(0, 1)], 'parallel ADD positive filter')
    solution = solve_pair(program, 0, 1, factors, transfers(program, pairs))
    need(solution is not None and solution[-1] == 3, 'parallel ADD positive coefficient')
    need(literal(altered(program, 0, 1, solution[-1]), 2)[0] == original, 'parallel ADD positive endpoint')

    # A zero original derivative can compensate through the mixed term.
    # Coordinates: x=0, output=1, helpers=2,3. K={1,2,3}; R={0,2,3}.
    program = [['ADD',1,2,'-2'], ['ADD',1,3,'1'], ['ADD',2,0,'1'],
               ['ADD',3,0,'1'], ['ADD',1,2,'1'], ['ADD',2,3,'-1'],
               ['ADD',1,2,'1'], ['ADD',2,3,'1'], ['ADD',2,0,'-1'], ['ADD',3,0,'-1']]
    original, prefix = literal(program, 4, record_prefix=True)
    expected = [{0:Q(1)}, {1:Q(1),0:Q(1)}, {2:Q(1)}, {3:Q(1)}]
    need(original == expected, 'zero-derivative control source')
    suffix = responses(program, 4, 0)
    pairs, factors, _ = complete_filter([2], list(range(10)), prefix, suffix, {1}, {0})
    need((2,6) in pairs and direction(prefix[6], {0})[0] is None, 'zero-derivative compensator included')
    solution = solve_pair(program,2,6,factors,transfers(program,pairs))
    need(solution is not None and solution[-1] == -1, 'zero-derivative compensator coefficient')
    changed = altered(program,2,6,solution[-1])
    # Supported pre-hub and post-hub repairs, with fixed operands throughout.
    repaired = [['ADD',1,2,'2'], ['ADD',1,3,'-2']] + changed + [['ADD',2,0,'1']]
    need(literal(repaired,4)[0] == original, 'zero-derivative hub repair')

    # Reverse-transpose exercises an earlier zero-output compensator.
    reverse = [[e[0], e[2], e[1], e[3]] for e in reversed(program)]
    reverse_A, reverse_prefix = literal(reverse, 4, record_prefix=True)
    reverse_suffix = responses(reverse, 4, 0)
    reverse_pairs, reverse_factors, _ = complete_filter(
        [7], list(range(10)), reverse_prefix, reverse_suffix, {0}, {1})
    need((7,3) in reverse_pairs and direction(reverse_suffix[3], {0})[0] is None,
         'early zero-output compensator included')
    reverse_solution = solve_pair(reverse,7,3,reverse_factors,transfers(reverse,reverse_pairs))
    need(reverse_solution is not None and reverse_solution[-1] == -1, 'early compensator coefficient')
    reverse_changed = altered(reverse,7,3,reverse_solution[-1])
    reverse_repaired = [['ADD',0,2,'1']] + reverse_changed + [['ADD',3,1,'-2'], ['ADD',2,1,'2']]
    need(literal(reverse_repaired,4)[0] == reverse_A, 'early zero-output supported hub repair')

    # COPY overwrites a nonzero owned row; CLEAR erases a nonzero row.
    program = [['INIT',3,0], ['ADD',3,1,'3'], ['COPY',3,0,'2'], ['ADD',1,3,'3'],
               ['SCALE',1,'-2'], ['ADD',2,1,'1/2'], ['CLEAR',3,0]]
    original, prefix = literal(program,3,1,record_prefix=True)
    suffix = responses(program,3,1)
    need(not suffix[1], 'COPY overwrite annihilates earlier owned signal')
    pairs = [(1,2),(1,3),(2,3),(2,4),(2,5),(3,5)]
    tau = transfers(program,pairs)
    for a,b in pairs:
        for alpha,beta in ((Q(1),Q(-2)),(Q(-3,2),Q(1,4))):
            changed = [list(event) for event in program]
            for index,change in ((a,alpha),(b,beta)):
                event=changed[index]
                event[2 if event[0]=='SCALE'else 3]=str(coefficient(event)+change)
            actual=literal(changed,3,1)[0]
            predicted=[dict(row)for row in original]
            for u,v,c in ((suffix[a],prefix[a],alpha),(suffix[b],prefix[b],beta),
                          (suffix[b],prefix[a],alpha*beta*tau[a,b])):
                for i,value in u.items():add(predicted[i],v,c*value)
            need(actual==predicted,'two-event identity control')
    control_error(lambda: check_null([{0:Q(1)}], {0:Q(1)}))
    return {'parallel_add_repair':True,'zero_derivative_compensator_repair':True,
            'early_zero_output_compensator_repair':True,
            'nonzero_owned_overwrite_identity_cases':12,'null_vector_mutation_rejected':True}


def load_word():
    pins = json.loads((HERE/'retained/SOURCE-PINS.json').read_text())
    need(len(pins) == 1, 'one retained executable input')
    pin = pins[0]
    raw = (HERE/pin['local']).read_bytes()
    need(len(raw) == pin['bytes'], 'source byte length')
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256')
    need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'source Git blob')
    word = json.loads(gzip.decompress(raw))
    payload = {k:v for k,v in word.items()if k!='verifier_profile'}
    digest = hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(digest == pin['native_payload_sha256'], 'source native payload')
    control_error(lambda: need(hashlib.sha256(raw+b'x').hexdigest() == pin['sha256'], 'mutated source'))
    return word, digest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,help='Optional report outside the package; no output file by default.')
    args=parser.parse_args()
    started=time.monotonic()
    word,payload=load_word()
    A,dimension,K,R=source_check(word)
    public,program=word['public'],word['program']
    domain=visits(program,dimension)
    need((len(domain),sum(map(len,domain.values())))==(1278,1466),'visit domain census')
    replayed,prefix=literal(program,public,word['owned_fields'],True)
    need(replayed==A,'baseline response endpoint')
    suffix=responses(program,public,word['owned_fields'])
    gates=[i for i,e in enumerate(program)if scalar_event(e)]
    Rbar,Kbar=set(range(public))-R,set(range(public))-K
    pairs,factors,kinds=complete_filter(domain,gates,prefix,suffix,Rbar,Kbar)
    need(len(pairs)==172,'complete direction pair count')
    tau=transfers(program,pairs)
    impossible=0;exceptions=[]
    for deleted,other in pairs:
        solution=solve_pair(program,deleted,other,factors,tau)
        if solution is None:
            impossible+=1
            continue
        witness=null_witness(solution,prefix,suffix,word['live'])
        rows,_=literal(altered(program,deleted,other,solution[-1]),public,word['owned_fields'])
        need(all({j:v for j,v in rows[i].items()if j in Kbar}=={j:v for j,v in A[i].items()if j in Kbar}for i in Rbar),
             'candidate literal invariant boundary block')
        check_null(rows,witness)
        # Mutate a coordinate with a nonzero output column, to leave the kernel.
        coordinate = next(j for j in range(public) if any(row.get(j, Q(0)) for row in rows))
        damaged = dict(witness)
        damaged[coordinate] = damaged.get(coordinate, Q(0)) + 1
        control_error(lambda: check_null(rows, damaged))
        exceptions.append({'deleted_event':deleted,'compensator_event':other,'new_coefficient':str(solution[-1]),
                           'null_vector':{str(i):str(x)for i,x in sorted(witness.items())}})
    need((impossible,len(exceptions))==(157,15),'inconsistent/singular partition')
    result={'claim':'source-bound obstruction; no kappa','native_payload_sha256':payload,
            'public':public,'events':len(program),'scalar_events':len(gates),'K':len(K),'R':len(R),
            'visits':sum(map(len,domain.values())),'distinct_deleted_ADDs':len(domain),
            'visit_domain_sha256':hashlib.sha256(json.dumps(domain,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'compatible_pairs_sha256':hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest(),
            'direction_compatible_pairs':len(pairs),'pair_kinds':kinds,
            'inconsistent_boundary_equations':impossible,'singular_candidates':exceptions,
            'actual_null_vector_mutations_rejected':len(exceptions),'controls':controls()}
    need(result == json.loads((HERE/'CERTIFICATE.json').read_text()), 'frozen certificate differs from exact reconstruction')
    if args.output:
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS_P104_CONTACT_COEFFICIENT_RIGIDITY',json.dumps({
        'visits':1466,'deleted_ADDs':1278,'scalar_compensators':len(gates),
        'compatible_pairs':172,'inconsistent':157,'literal_singular':15,
        'controls':result['controls'],'seconds':round(time.monotonic()-started,3)},sort_keys=True))


if __name__=='__main__':
    main()
