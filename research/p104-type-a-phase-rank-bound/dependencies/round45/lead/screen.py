"""Exact local Type A J correction for one QUERY replaced by an ADD."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import runpy
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
PINS = {
    'round30/complex/audit.py': '67b006627fd4e07c349f48f31e6d541c62804416bdc85f664a3607dd1b386efb',
    'round30/complex/source/inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'round30/complex/source/inputs/EARLY-RESULT.json': '691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7',
    'round30/complex/source/inputs/WORD.json.gz': '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756',
    'round30/complex/source/powers.py': 'c0c460b464d7c836fb887010b57119be322aae686736b86820aae3544d380bee',
    'reference/check_odd_caller_exact_grid.py': 'abd5a5fd011b71e5b382cbc058855594d4f2fe7b049f375506675c0303180f54',
}


def authenticate(root):
    roots = {'round30': root, 'reference': Path(__file__).resolve().parent / 'references'}
    files = {}
    for key, digest in PINS.items():
        label, rel = key.split('/', 1)
        path = roots[label] / rel
        raw = path.read_bytes()
        assert sha256(raw).hexdigest() == digest, ('changed input', key)
        files[key] = path, raw
    return files


def decode(raw):
    def unique(pairs):
        result = dict(pairs)
        assert len(result) == len(pairs), 'duplicate JSON key'
        return result
    return json.loads(raw, object_pairs_hook=unique)


def save(out, name, receipt):
    tmp = out / (name + '.tmp')
    tmp.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    tmp.replace(out / name)


def elementary(caller, q):
    q = Q(q)
    assert q in (1, -1)
    a = caller['types']['A']
    n = a['roles']
    assert n == 36 and a['offset'] == 0
    assert a['alpha2'] == '-1' and a['beta2'] == '0'
    alpha = Q(a['alpha2'])
    blocks = []
    for clock, event in enumerate(caller['events']):
        ops = ()
        if event[0] == 'J':
            _, _, (u, v, x, y), _ = event
            assert len({u,v,x,y}) == 4 and all(0 <= r < n for r in (u,v,x,y))
            ops = (('ADD', v, u, 1/q), ('ADD', x, y, alpha*q))
        elif event[0] == 'A':
            _, op, r, *args = event
            assert 0 <= r < n
            if op in ('ADD', 'QUERY', 'SWAP'):
                s = args[0]
                assert s != r and 0 <= s < n
                if op == 'SWAP':
                    ops = ((op, r, s, Q(1)),)
                else:
                    value = Q(args[1]) if op == 'ADD' else q**args[1]
                    ops = (('ADD', r, s, value),)
            elif op == 'SCALE':
                value = Q(args[0])
                assert value
                ops = ((op, r, r, value),)
            else:
                assert op in ('LAMBDA', 'IDLE_ONE') and q**2 == 1
        if ops:
            blocks.append((clock, ops))
    return blocks


def transform(vector, operations, *, row=False, inverse=False):
    for op, d, s, q in operations:
        if op == 'SWAP':
            vector[d], vector[s] = vector[s], vector[d]
        elif op == 'SCALE':
            vector[d] *= 1/q if inverse else q
        else:
            assert op == 'ADD'
            if row:
                s, d = d, s
            if vector[s]:
                vector[d] += (-q if inverse else q) * vector[s]
    return vector


def unit(n, index):
    return [Q(i == index) for i in range(n)]


def correction(n, d, s, j_ops, between, query_before):
    left, right = unit(n, d), unit(n, s)
    if query_before:
        transform(left, between)
        transform(left, j_ops)
        transform(right, between, row=True, inverse=True)
    else:
        transform(left, reversed(between), inverse=True)
        transform(right, reversed(between), row=True)
        transform(right, reversed(j_ops), row=True)
    assert any(left) and any(right)
    return left, right


def corrected(vector, j_ops, left, right):
    coefficient = -2 * sum(a*b for a,b in zip(right, vector, strict=True))
    return [v + coefficient*x for v,x in zip(transform(vector.copy(), j_ops), left, strict=True)]


def controls():
    n, d, s = 5, 1, 0
    old = (('ADD', d, s, Q(-1)),)
    new = (('ADD', d, s, Q(1)),)
    j = (('ADD', 1, 0, Q(-1)), ('ADD', 2, 3, Q(1)))
    mid = (('ADD', 2, 1, Q(2, 3)), ('SCALE', 0, 0, Q(-2)))
    for before in (False, True):
        l, r = correction(n, d, s, j, mid, before)
        assert not l[4] and not r[4]
        for k in range(n):
            v = unit(n, k)
            if before:
                expected = transform(v.copy(), old + mid + j)
                observed = corrected(transform(v.copy(), new + mid), j, l, r)
            else:
                expected = transform(v.copy(), j + mid + old)
                observed = transform(corrected(v.copy(), j, l, r), mid + new)
            assert observed == expected
    _, right = correction(n, d, s, j, (('SWAP', 0, 4, Q(1)),), True)
    left, _ = correction(n, d, s, j, (('SWAP', 1, 4, Q(1)),), True)
    assert right[4] and left[4]
    return ['query_before_and_after_exact_basis_recomposition', 'wrong_layout_outside_read',
            'wrong_layout_outside_write']


def run(root, out, cap, seconds, started):
    control = controls()
    data = authenticate(root)
    c = decode(data['round30/complex/source/inputs/CALLER.json'][1])
    early = decode(data['round30/complex/source/inputs/EARLY-RESULT.json'][1])
    audit = runpy.run_path(str(data['round30/complex/audit.py'][0]))
    power = runpy.run_path(str(data['round30/complex/source/powers.py'][0]))['power']
    _, _, _, edges, _, _, copies, paid, productive, _ = audit['read_model']()
    assert audit['HEAD'] == HEAD and copies == 17 and len(edges) == 137891
    k = Q(early['price']['independent_raw_bracket'][1])
    a = c['types']['A']
    ports = len(set(a['ports']))
    assert ports == len(a['ports']) == 96
    queries = [(t, e[2:]) for t,e in enumerate(c['events']) if e[:2] == ['A', 'QUERY']]
    stages = [(t, e[1], e[2]) for t,e in enumerate(c['events']) if e[0] == 'J']
    assert len(queries) == 4 and [s for _,s,_ in stages] == list(range(1,18))
    assert all(exponent % 2 for _, (_, _, exponent) in queries)
    stock = [(p,j) for (p,_),(j,_,_) in product(queries,stages)]
    assert len(stock) == len(set(stock)) == 68
    tariff = cache(lambda rank: power(rank, k))

    def price(hist):
        lo = hi = Q(0)
        for rank, count in hist.items():
            a, b = tariff(rank)
            lo += count * (a if count >= 0 else b)
            hi += count * (b if count >= 0 else a)
        return list(map(str,(lo,hi)))

    net = productive.copy()
    net.subtract(paid)
    old_margin = price(net)
    assert Q(old_margin[1]) < 0
    delta = {1: ports}
    edited = net.copy()
    edited.update(delta)
    save(out, 'PRICE.json', dict(head=HEAD, pins=PINS, crossing_upper=str(k), native_copies=copies,
         type_a_ports=ports, original_paid=dict(paid), original_productive=dict(productive),
         old_margin_interval=old_margin, credit_paid_rank_one_per_alternative=ports,
         optimistic_saving_interval_per_alternative=price(delta),
         optimistic_complete_margin_interval_per_alternative=price(edited),
         alternatives=[dict(query_clock=p, j_clock=j) for p,j in stock],
         grant='All new costs free for the upper. Each alternative removes one QUERY. Credits cannot be summed across alternatives.'))

    n = a['roles']
    assert len(a['diagonal']) == n and all(e[:2] == [-1,0] and len(e)==copies+2 for e in a['diagonal'])
    by_phase = {q: elementary(c, q) for q in (-1,1)}
    block_at = {q:dict(blocks) for q,blocks in by_phase.items()}
    for q, blocks in by_phase.items():
        ops = tuple(op for _, part in blocks for op in part)
        for i in range(n):
            expected = [q*x for x in unit(n,i)]
            assert transform(unit(n,i),ops) == expected, ('incumbent endpoint',q,i)
    deadline = started + seconds - 2
    result, survivors = [], []
    for (p,(d,s,exponent)),(j,stage,active) in product(queries,stages):
        if len(result) == cap or monotonic() >= deadline:
            break
        assert block_at[1][p] == (('ADD', d, s, Q(1)),)
        assert block_at[-1][p] == (('ADD', d, s, Q(-1)),)
        middle = tuple(op for clock,part in by_phase[-1] if min(p,j) < clock < max(p,j) for op in part)
        j_ops = block_at[-1][j]
        left,right = correction(n,d,s,j_ops,middle,p<j)
        exterior_reads = [i for i,x in enumerate(right) if x and i not in active]
        exterior_writes = [i for i,x in enumerate(left) if x and i not in active]
        row = dict(query_clock=p,j_clock=j,stage=stage,active_roles=active,query_exponent=exponent,
                   outside_reads=exterior_reads,outside_writes=exterior_writes)
        if not exterior_reads and not exterior_writes:
            mat_minus = [corrected(unit(n,i),j_ops,left,right) for i in active]
            mat_plus = [transform(unit(n,i),block_at[1][j]) for i in active]
            row['candidate_phase_blocks'] = {'minus':[[str(v[i]) for v in mat_minus] for i in active],
                                             'plus':[[str(v[i]) for v in mat_plus] for i in active]}
            survivors.append([p,j])
        result.append(row)
    tested = {(r['query_clock'],r['j_clock']) for r in result}
    pending = [pair for pair in stock if pair not in tested]
    assert len(result)+len(pending)==68
    save(out, 'SUPPORT.json', dict(head=HEAD,pins=PINS,controls=control,
         price_sha256=sha256((out/'PRICE.json').read_bytes()).hexdigest(),
         baseline_endpoint_checked_at_q=[1,-1],body_specialization=1,checked=len(result),
         unvisited=pending,support_survivors=survivors,rows=result,
         status='support_only' if survivors else 'capped' if pending else 'all_alternatives_excluded',
         pending_candidate_checks=['positive fully charged margin', 'signed arbitrary-body provider and adjoint',
                                    'physical locality, setup, ownership and dirty restoration',
                                    'precision, tape, caller and complete independent replay']))


def main():
    p=ArgumentParser()
    p.add_argument('round30',type=Path,nargs='?')
    p.add_argument('out',type=Path,nargs='?')
    p.add_argument('--cap',type=int,default=68,choices=range(1,69),metavar='1..68')
    p.add_argument('--seconds',type=int,default=45,choices=range(3,46),metavar='3..45')
    p.add_argument('--controls-only',action='store_true')
    a=p.parse_args()
    if a.controls_only:
        print(json.dumps(controls()))
        return
    if a.round30 is None or a.out is None:
        p.error('Round 30 root and fresh output directory required')
    a.out.mkdir()

    def timeout(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM,timeout)
    alarm(a.seconds)
    try:
        run(a.round30,a.out,a.cap,a.seconds,monotonic())
    except TimeoutError:
        save(a.out,'TIMEOUT.json',dict(head=HEAD,status='hard_timeout', unverified=68,
                                     price_saved=(a.out/'PRICE.json').exists()))
        raise SystemExit(2)
    finally:
        alarm(0)


if __name__=='__main__':
    main()
