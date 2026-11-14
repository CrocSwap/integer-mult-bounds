#!/usr/bin/env python3
"""Source-only support certificate for every subspace of span(e885-e705,e1459)."""
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import math
import time

HERE = Path(__file__).resolve().parent
PIN = 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
RANK_PIN = 'ddad7c43a02b3df025dba8dd31ea866079cf61ddd00c5f6e1af40461798cf207'
NOTICE_PIN = '78e060cbd33ebc4078cabf39e50191a977fb9eb5c41104533079e22da1d9d248'
PRIME = 1000033


def need(ok, label):
    if not ok:
        raise ValueError(label)


def axpy(a, b, coefficient):
    for column, value in b.items():
        updated = a.get(column, Q(0)) + coefficient * value
        if updated:
            a[column] = updated
        else:
            a.pop(column, None)


def rejects(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('negative control accepted: ' + label)


def support_gate(touches, arrivals_at_three, support_885, support_1459):
    expected = [
        (30780, ['ADD', 885, 943, '1/2', 3]),
        (40710, ['MOVE', 885, 3, 189, False]),
        (40711, ['ADD', 885, 705, '-1/2', 189]),
        (41698, ['ADD', 885, 943, '-1/2', 189]),
    ]
    need(touches == expected, 'all885 touches, no donor use or hidden transport')
    need(not arrivals_at_three, 'frame3 has no MOVE arrivals')
    need(support_885 == [(-1, 885, 3), (40710, 885, 189)], 'complete e885 observation support')
    need(support_1459 == [(-1, 1459, 189), (45748, 1459, 127), (52236, 763, 127)],
         'complete e1459 observation support')


def identity(lookup, terms, wanted, coframe):
    row = {}
    for label, coefficient in terms:
        need(label[2] == coframe and label in lookup, 'identity provider exact coframe')
        axpy(row, lookup[label], Q(coefficient))
    need(row == wanted, 'fresh exact circuit identity')


def latest_event(terms, target):
    nonzero = [label[0] for label, coefficient in terms if Q(coefficient)]
    need(nonzero and max(nonzero) == target, 'complete latest nonzero circuit support')
    need(sum(event == target for event in nonzero) == 1, 'unique latest circuit arrival')


def debit_gate(relation_basis, debited):
    """Small exact rank, separately implemented from the history certificate."""
    basis = {}
    for row in relation_basis:
        v = {j: Q(row.get(j, 0)) for j in debited if row.get(j, 0)}
        while v:
            p = max(v)
            if p not in basis:
                q = v[p]
                basis[p] = {j: z/q for j, z in v.items()}
                break
            axpy(v, basis[p], -v[p])
    need(len(basis) == len(relation_basis), 'relation restriction injective on fully debited coordinates')


def verify(source=None):
    start = time.monotonic()
    raw = Path(source or HERE/'inputs/WORD.json.gz').read_bytes()
    need(sha256(raw).hexdigest() == PIN, 'source byte pin')
    rank_path = HERE/'inputs/all_history_independent.py'
    need(sha256(rank_path.read_bytes()).hexdigest() == RANK_PIN, 'credited rank helper byte pin')
    need(sha256((HERE/'inputs/PREDECESSOR-NOTICE').read_bytes()).hexdigest() == NOTICE_PIN,
         'original predecessor notice byte pin')
    spec = importlib.util.spec_from_file_location('credited_column_rank', rank_path)
    rank = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rank)
    need(PRIME >= 2 and all(PRIME % d for d in range(2, math.isqrt(PRIME)+1)), 'certificate prime')
    w = json.loads(gzip.decompress(raw))
    n, owned = w['public'], w['owned_fields']
    need((n, owned, len(w['program'])) == (1501, 68, 76475), 'source domain')
    classes = [rank.framekey(b) for b in w['frames']]
    rows = [{i: Q(1)} for i in range(n)] + [None]*owned
    frames = w['initial'].copy() + [None]*owned
    banks, lookup, moves = defaultdict(list), {}, {}
    touches, arrivals_at_three, support_885, support_1459 = [], [], [], []
    matrix_digest = sha256()

    def observe(event, owner, frame):
        label = (event, owner, frame)
        value = rows[owner].copy()
        need(label not in lookup, 'unique source observation')
        lookup[label] = value
        banks[frame].append((label, value))
        if value.get(885):
            support_885.append(label)
        if value.get(1459):
            support_1459.append(label)
        matrix_digest.update((json.dumps([label, sorted((j, str(q)) for j,q in value.items())],
                                        separators=(',', ':'))+'\n').encode())

    for a, f in enumerate(w['initial']):
        observe(-1, a, f)
    for event, e in enumerate(w['program']):
        if event % 256 == 0:
            need(time.monotonic()-start < 240, 'four-minute bounded source/rank replay')
        op, a = e[:2]
        if a == 885 or (op in ('ADD','COPY') and e[2] == 885):
            touches.append((event, e))
        if op == 'MOVE':
            need(rows[a] is not None and frames[a] == e[2] and e[4] == (a >= n), 'MOVE live owner and source')
            A, B = set(classes[e[2]]), set(classes[e[3]])
            need(A < B if a < n else (A < B or B < A), 'literal nested MOVE grammar')
            r = abs(len(w['frames'][e[3]])-len(w['frames'][e[2]]))
            need(r > 0 and rows[a], 'positive native rank and nonzero unrestricted target')
            moves[event] = {'owner':a, 'source':e[2], 'destination':e[3], 'rank':r}
            frames[a] = e[3]
            if e[3] == 3:
                arrivals_at_three.append(event)
            observe(event, a, e[3])
        elif op == 'INIT':
            need(a >= n and rows[a] is None and frames[a] is None, 'owned fresh INIT')
            rows[a], frames[a] = {}, e[2]
        elif op == 'CLEAR':
            need(a >= n and rows[a] is not None and frames[a] == e[2], 'owned live CLEAR')
            rows[a], frames[a] = None, None
        elif op == 'SCALE':
            need(rows[a] is not None and frames[a] == e[-1] and Q(e[2]), 'nonzero SCALE')
            rows[a] = {j: Q(e[2])*v for j,v in rows[a].items()}
        elif op in ('ADD','COPY'):
            b = e[2]
            need(a != b and rows[a] is not None and rows[b] is not None and frames[a] == frames[b] == e[-1], 'coframed scalar operation')
            if op == 'COPY':
                need(a >= n and not rows[a], 'COPY into owned zero')
            axpy(rows[a], rows[b], Q(e[3]))
        else:
            raise ValueError('unknown opcode')
    need(frames == w['final'] + [None]*owned, 'full endpoints and owned lifetimes')
    need(all(rows[h] == {h:Q(1)} for h in (705,885,1459)),
         'the three original helper targets retain their own arbitrary coordinate')
    need(len(moves) == 6279 and len(lookup) == 7780 and len(banks) == 979, 'complete observation domain')
    need(len({classes[f] for f in banks}) == len(banks), 'no used physical-frame alias merges')
    support_gate(touches, arrivals_at_three, support_885, support_1459)
    need(len(banks[3]) == 1060 and all(t == -1 and row == {a:Q(1)} for (t,a,f),row in banks[3]),
         'frame3 contains only1060 original coordinate units')
    need([w['initial'][a] for a in (705,885,1459)] == [105,3,189], 'helper entrances')
    need({j:abs(len(w['frames'][w['final'][j]])-len(w['frames'][w['initial'][j]])) for j in (705,885,1459)}
         == {705:8,885:8,1459:1}, 'exact original helper target ranks')

    g, h = {885:Q(1),705:Q(-1)}, {1459:Q(1)}
    g_terms = [((40710,885,189),'1'),((40708,705,189),'-1')]
    h_terms = [((45748,1459,127),'1'),((52233,557,127),'-1/4'),((52236,763,127),'-1')]
    need(lookup[-1,1459,189] == h, 'initial h generator')
    need(lookup[40708,705,189] == {705:Q(1),943:Q(1)}, 'exact40708 source row')
    need(lookup[40710,885,189] == {885:Q(1),943:Q(1)}, 'exact40710 target row')
    identity(lookup, g_terms, g, 189)
    identity(lookup, h_terms, h, 127)
    latest_event(g_terms,40710)
    latest_event(h_terms,52236)
    need(moves[40710]['rank'] == 8 and moves[52236]['rank'] == 1, 'cache target prices')
    inverses, total_rank = {}, 0
    for f, bank in sorted(banks.items()):
        need(time.monotonic()-start < 240, 'four-minute bounded source/rank replay')
        columns = defaultdict(dict)
        for i, (_,row) in enumerate(bank):
            for j,q in row.items():
                value = rank.rational_mod(q, PRIME, inverses)
                if value:
                    columns[j][i] = value
        certificate = rank.column_rank_certificate(columns, len(bank), PRIME)
        need(certificate['rank'] == len(bank), 'modular rank reaches literal row-count upper bound')
        total_rank += certificate['rank']
    need(total_rank == 7780, 'all original observations independent over Q')

    controls = []
    changed = raw[:-1] + bytes([raw[-1] ^ 1])
    controls.append(rejects(lambda:need(sha256(changed).hexdigest() == PIN, 'source byte pin'), 'mutated source bytes'))
    controls.append(rejects(lambda:support_gate(touches+[(60000,['ADD',700,885,'1',189])],[],support_885,support_1459), 'added885 donor'))
    controls.append(rejects(lambda:support_gate(touches,[1],support_885,support_1459), 'new frame3 arrival'))
    controls.append(rejects(lambda:support_gate(touches,[],support_885,support_1459[:-1]), 'omitted1459 observation'))
    bad = h_terms.copy(); bad[1] = (bad[1][0],'1/4')
    controls.append(rejects(lambda:identity(lookup,bad,h,127), 'wrong circuit sign'))
    bad = h_terms.copy(); bad[0] = ((45748,1459,189),'1')
    controls.append(rejects(lambda:identity(lookup,bad,h,127), 'wrong physical coframe'))
    controls.append(rejects(lambda:latest_event(h_terms[:-1],52236), 'omitted latest circuit member'))
    controls.append(rejects(lambda:latest_event(h_terms,45748), 'incorrect latest event'))
    debit_gate([g],{705});debit_gate([g],{885});debit_gate([h],{1459})
    debit_gate([g,h],{705,1459});debit_gate([g,h],{885,1459})
    controls.append(rejects(lambda:debit_gate([g],{1459}), 'lambda-zero cannot use cheap1459 debit'))
    controls.append(rejects(lambda:debit_gate([g,h],{705,885}), 'full plane must debit1459'))
    controls.append(rejects(lambda:debit_gate([g,h],{1459}), 'full plane also needs a rank8 debit'))
    # Universal nonzero-lambda determinant is lambda; this is not sampled here.
    return {
        'status':'PASS_COMPLETE_TWO_DIMENSIONAL_PUBLIC_RELATION_CLASSIFICATION',
        'source_sha256':PIN, 'rank_helper_sha256':RANK_PIN,
        'events':76475, 'MOVE_arrivals':6279, 'observations':7780, 'physical_coframes':979,
        'full_rational_row_rank':total_rank, 'certificate_prime':PRIME,
        'source_observation_digest':matrix_digest.hexdigest(),
        'e885_observations':support_885, 'e1459_observations':support_1459,
        'frame3_original_units':1060, 'frame3_arrivals':0,
        'g_circuit':g_terms, 'h_circuit':h_terms,
        'classification':[
            {'annihilator':'0','nonzero_cache_events':[],'zero_MOVE_events':[],'least_debit_ranks':[]},
            {'annihilator':'span(g)','nonzero_cache_events':[40710],'zero_MOVE_events':[],'least_debit_ranks':[8]},
            {'annihilator':'span(g+lambda*h), lambda!=0','nonzero_cache_events':[40710],'zero_MOVE_events':[],'least_debit_ranks':[1]},
            {'annihilator':'span(h)','nonzero_cache_events':[52236],'zero_MOVE_events':[],'least_debit_ranks':[1]},
            {'annihilator':'span(g,h)','nonzero_cache_events':[40710,52236],'zero_MOVE_events':[],'least_debit_ranks':[1,8]},
        ],
        'executed_failure_controls':controls,
        'proof_scope':'All scalar subspaces over R or C by exact support isolation and unique circuits; no finite parameter search. Physical preparation requires the additional explicit unavailable1459 access and billed transport premises in PROOF.md. No new kappa.'
    }


if __name__ == '__main__':
    print(json.dumps(verify(),indent=2,sort_keys=True))
