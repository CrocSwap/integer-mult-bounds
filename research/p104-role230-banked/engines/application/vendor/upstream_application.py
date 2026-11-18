#!/usr/bin/env python3
"""Exact-source caller geometry, occurrence allocation and rational BIT frames.

No contributor scientific module is imported. Complex phase-polynomial
method credited to the retained fragment physical audit; here coefficients
of the full degree-two polynomial are constructed instead of probing it.
OpenAI Codex assistance for Douglas Colkitt. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = (ROOT / path).read_bytes()
    pin = next(p for p in json.loads((HERE / 'SOURCES.json').read_text())['files']
               if p['path'] == path)
    need(sha256(raw).hexdigest() == pin['sha256'], 'source bytes: ' + path)
    return json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def bits(n):
    result = []
    while n:
        a = n & -n
        result.append(a)
        n ^= a
    return result


def dot(a, b):
    return (a & b).bit_count() % 2


def terms(items):
    c = Counter()
    for v, a in items:
        c[v] += a
    return {v: a % 4 for v, a in c.items() if v and a % 4}


def sub(a, b):
    return terms(list(a.items()) + [(v, -c) for v, c in b.items()])


def polynomial(t):
    # parity(sum x_i) = sum x_i - 2 sum_{i<j} x_i*x_j mod 4.
    result = Counter()
    for v, c in t.items():
        axes = bits(v)
        for i, a in enumerate(axes):
            result[(a,)] += c
            for b in axes[i+1:]:
                result[(a, b)] -= 2*c
    return {k: v % 4 for k, v in result.items() if v % 4}


def translation(t):
    p = polynomial(t)
    need(all(len(k) == 1 and v == 2 for k, v in p.items()), 'pure translation, full phase')
    return sum(k[0] for k in p)


def route(q, basis, stage):
    native = [q] + basis
    need(len(native) == 9 and all(0 < v < 512 for v in native), 'nine central directions')
    need(all(dot(a, b) == (i == j) for i, a in enumerate(native)
             for j, b in enumerate(native)), 'orthonormal central basis')
    fresh = [1 << (9+8*(stage-1)+j) for j in range(8)]
    mask = 511 | sum(fresh)

    def transform(v):
        out = v & ~mask
        if dot(v & 511, q):
            out ^= q
        for b, a in zip(basis, fresh):
            if dot(v & 511, b):
                out ^= a
            if v & a:
                out ^= b
        return out

    images = [transform(1 << i) for i in range(153)]
    need(all(transform(v) == 1 << i for i, v in enumerate(images)), 'complete route inverse')
    need(transform(q) == q, 'central direction preserved')
    need(all(images[i] == 1 << i for i in range(153) if not (mask & (1 << i))),
         'every external spectator coordinate fixed')
    return transform


def boundary(before, after, transform, omit_translation=False):
    moved = terms((transform(v), c) for v, c in before.items())
    shift = translation(sub(after, moved))
    need(not polynomial(sub(after, terms(list(moved.items())+[(0 if omit_translation else shift, 2)]))),
         'forward contact includes its phase')
    inverse = terms((transform(v), c) for v, c in after.items())
    inverse = terms(list(inverse.items()) + [(transform(shift), 2)])
    need(not polynomial(sub(before, inverse)), 'inverse contact restores full operator')
    return shift


def complex_application(word, caller, receipt, phase_recipes):
    need(caller['ambient_rank'] == 153 and caller['stages'] == 18, 'actual complex ambient')
    need([e[1] for e in caller['events'] if e[0]=='J']==list(range(1,19)), 'fresh chronological native stages')
    by_q = {r['q']: r['idle_children'][0]['orthogonal_axes'][:8]
            for r in phase_recipes['recipes']}
    Dports = word['hosted']['Dports']
    second = dict(zip(Dports, zip(word['hosted']['X2'], word['hosted']['Y2'])))
    need(caller['types']['A']['ports'] == Dports, 'hosted type partition')
    need(sorted(Dports + caller['types']['B']['ports']) == list(range(104)), 'complete disjoint ports')
    main = set(word['live']) | {x+112 for x in word['live']}
    main |= set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    helpers = sorted(set(range(word['public'])) - main)
    need(len(main) == 400 and len(helpers) == 1080, 'actual public inventory')
    for pi, (x2, y2) in second.items():
        x = word['live'][pi]
        need(all(word[k][a] == word[k][b] for k in ('initial', 'final')
                 for a, b in ((x, x2), (x+112, y2))), 'second plane identical boundary frames')
    need((word['hosted']['alpha'], word['hosted']['beta'],
          word['hosted']['alpha2'], word['hosted']['beta2']) == ('-1', '1/2', '-1', '0'),
         'literal hosted scalar endpoints')
    for pi, q in enumerate(word['ports']):
        x = word['live'][pi]
        need(word['frames'][word['initial'][x]] == [q]
             and word['frames'][word['initial'][x+112]] == [], 'main incoming frames')
        need(word['frames'][word['final'][x]] == [1 << j for j in range(9)], 'full X frame')
        ybasis = word['frames'][word['final'][x+112]]
        need(len(ybasis) == 8 and all(dot(q, b) == 0 for b in ybasis), 'Y complement frame')

    P, T = Counter(), Counter()
    owners = {('main', pi, d['offset']+r) for d in caller['types'].values()
              for pi in d['ports'] for r in range(d['roles'])}
    need(len(owners) == 3952, 'root productive fields')
    native_moves = [(i, e) for i, e in enumerate(word['program']) if e[0] == 'MOVE']
    occurrences = []
    phase_records = []
    stage_order = []
    lambda_uses = query_uses = idle_uses = 0
    for ci, e in enumerate(caller['events']):
        if e[0] == 'J':
            _, stage, plane_a, plane_b = e
            stage_order.append(stage)
            need(len(set(plane_a)) == 4 and all(0 <= r < 38 for r in plane_a), 'A owners')
            need(len(set(plane_b[:2])) == 2 and all(38 <= r < 76 for r in plane_b[:2]), 'B owners')
            need(plane_b[2:] == ['-1', '1/2'], 'B native contact coefficients')
            mapping = {}
            for pi, x in enumerate(word['live']):
                pair = plane_a[:2] if pi in second else plane_b[:2]
                mapping[x] = ('main', pi, pair[0]); mapping[x+112] = ('main', pi, pair[1])
                if pi in second:
                    x2, y2 = second[pi]
                    mapping[x2] = ('main', pi, plane_a[2]); mapping[y2] = ('main', pi, plane_a[3])
            for r in helpers:
                owner = ('helper', ci, r)
                need(owner not in owners, 'fresh helper input')
                owners.add(owner); mapping[r] = owner
                rank = len(word['frames'][word['final'][r]])-len(word['frames'][word['initial'][r]])
                need(rank > 0, 'positive complete helper job')
                T[rank] += 1
            need(len(mapping) == len(set(mapping.values())) == word['public'], 'injective native inputs')
            for r in range(word['public'], word['public']+word['owned_fields']):
                mapping[r] = ('owned', ci, r-word['public'])
            need(len(set(mapping.values())) == word['public']+51, 'owned/public separation')
            for ni, move in native_moves:
                _, r, start, end, owned = move
                rank = abs(len(word['frames'][end])-len(word['frames'][start]))
                need(owned == (r >= word['public']) and rank > 0, 'actual paid owner class')
                P[rank] += 1
                occurrences.append([ci, ni, list(mapping[r]), rank, start, end])
            for pi, q in enumerate(word['ports']):
                transform = route(q, by_q[q], stage)
                before_axes = [1 << j for j in range(9+8*(stage-1))]
                after_axes = [1 << j for j in range(9+8*stage)]
                spectator = [1 << j for j in range(9, 9+8*stage)]
                x0 = terms((a, 1) for a in before_axes)
                y0 = terms(list(x0.items())+[(q, -1)])
                x1 = terms((a, 1) for a in after_axes)
                y1 = terms(list(x1.items())+[(q, -1)])
                nx0 = terms([(a, 1) for a in spectator]+[(q, 1)])
                ny0 = terms((a, 1) for a in spectator)
                nx1 = terms((a, 1) for a in spectator+[1 << j for j in range(9)])
                ny1 = terms(list(nx1.items())+[(q, -1)])
                shifts = [boundary(a, b, transform) for a, b in
                          ((x0, nx0), (y0, ny0), (nx1, x1), (ny1, y1))]
                body = terms((1 << j, 1) for j in range(9+8*(stage-1), 9+8*stage))
                for actual, expected in ((sub(x1,x0),body), (sub(y1,y0),body),
                         (sub(y1,x0),terms(list(body.items())+[(q,-1)])),
                         (sub(x1,y0),terms(list(body.items())+[(q,1)]))):
                    need(not polynomial(sub(actual,expected)), 'all four contact operators')
                need(polynomial(sub(terms([(q,1)]),terms([(q,-1)]))), 'wrong query orientation rejected')
                phase_records.append([ci,pi,shifts,2 if pi in second else 1])
        else:
            ty, op, r, *a = e
            kind = caller['types'][ty]
            used = [r] + ([a[0]] if op in ('ADD','SWAP','QUERY') else [])
            need(all(kind['offset'] <= x < kind['offset']+kind['roles'] for x in used), 'caller owners stay in type')
            need(len(used) == len(set(used)), 'distinct scalar/query owners')
            if op in ('QUERY','IDLE_ONE'):
                if op == 'QUERY':
                    need(a[1] in (-1,1), 'signed completed query')
                    rank = 1; query_uses += len(kind['ports'])
                else:
                    selected = a[0]
                    need(selected and len(selected)==len(set(selected))
                         and all(1 <= s <= 18 for s in selected), 'whole idle stage axes')
                    rank = 8*len(selected); idle_uses += len(kind['ports'])
                for pi in kind['ports']:
                    owner = ['query_scratch',ci,pi] if op == 'QUERY' else ['main',pi,r]
                    occurrences.append([ci,op,owner,rank]); P[rank] += 1
            elif op == 'LAMBDA':
                need(a[0] in (-1,1), 'global normalizer sign')
                lambda_uses += len(kind['ports'])
    need(stage_order == list(range(1,19)), 'fresh chronological native stages')
    for kind in caller['types'].values():
        for diagonal in kind['diagonal']:
            qp, zero, *selection = diagonal
            need(qp in (-1,0,1) and zero == 0 and len(selection)==18
                 and set(selection)<={0,1} and any(selection), 'positive nonempty root endpoint')
            rank = abs(qp)+8*sum(selection)
            for pi in kind['ports']:
                q = word['ports'][pi]
                axes = [1 << (9+8*j+k) for j,yes in enumerate(selection) if yes for k in range(8)]
                actual = terms([(q,qp)]+[(a,1) for a in axes])
                target = terms((a,1) for a in ([q] if qp else [])+axes)
                need(translation(sub(target,actual)) == (q if qp == -1 else 0), 'whole output correction')
                T[rank] += 1
    for name, actual in [('P',P),('T',T)]:
        need(actual == Counter({int(k):v for k,v in receipt['invoice'][name].items()}), 'independent '+name+' invoice')
    need(sum(T.values()) == len(owners), 'every productive target is one actual owner')
    need(len(occurrences) == sum(P.values()), 'every paid position retained in order')
    return dict(ambient=153, native_calls=18, native_public=1480, fresh_helpers=19440,
        productive_fields=len(owners), paid_positions=len(occurrences),
        complete_paid_position_digest=digest(occurrences),
        native_contact_boundaries=sum(4*r[3] for r in phase_records),
        phase_record_digest=digest(phase_records), nonzero_boundary_translations=sum(sum(bool(x) for x in r[2])*r[3] for r in phase_records),
        reserved_native_banks=18*51, reserved_serial_query_lambda_bank=1,
        query_uses=query_uses, idle_uses=idle_uses, lambda_uses=lambda_uses,
        paid=dict(sorted(P.items())), targets=dict(sorted(T.items())),
        rank_surplus=sum(r*T[r] for r in T)-sum(r*P[r] for r in P))


def inverse(matrix):
    n = len(matrix)
    a = [[Q(x) for x in row]+[Q(i==j) for j in range(n)] for i,row in enumerate(matrix)]
    det = Q(1)
    for j in range(n):
        pivot = next((i for i in range(j,n) if a[i][j]),None)
        need(pivot is not None, 'rational basis invertible')
        if pivot != j:
            a[j],a[pivot] = a[pivot],a[j]; det = -det
        v = a[j][j]; det *= v; a[j] = [x/v for x in a[j]]
        for i in range(n):
            if i != j:
                v = a[i][j]
                a[i] = [x-v*y for x,y in zip(a[i],a[j])]
    return [row[n:] for row in a], det


def bit_application(word, caller, receipt):
    ff = word['frames']; determinants=[]; denominator_witnesses=set()
    for label, frame in ff.items():
        B,A = frame['B'],frame['A']; d = frame['dim']
        need(len(B)==d and len(A)==8-d and all(len(v)==8 for v in B+A), 'rational frame dimensions')
        need(all(sum(Q(x)*Q(y) for x,y in zip(b,a))==0 for b in B for a in A), 'complement annihilation')
        inv, det = inverse(list(zip(*(B+A))))
        determinants.append([label,str(det)])
        denominator_witnesses.add(abs(det.numerator)); denominator_witnesses.add(det.denominator)
        for row in inv:
            denominator_witnesses.update(x.denominator for x in row)
        for row in B+A:
            denominator_witnesses.update(Q(x).denominator for x in row)
    charts=[]
    for port in range(111):
        head=ff[str(word['start'][port])]; body=ff[str(word['final'][port+111])]
        need(head['dim']==1 and body['dim']==7, 'actual main head/body ranks')
        u=head['B'][0]
        need(all(sum(Q(x)*Q(y) for x,y in zip(u,v))==0 for v in body['B']), 'main complement')
        inv,det=inverse(list(zip(*([u]+body['B']))))
        charts.append([port,str(det)])
        denominator_witnesses.update([abs(det.numerator),det.denominator])
        for row in inv:denominator_witnesses.update(x.denominator for x in row)
    P,T=Counter(),Counter(); positions=[]; names={('main',pi,r) for pi in range(111) for r in range(38)}
    calls=[]
    for ci,e in enumerate(caller['events']):
        op=e[0]
        if op=='LOCAL':
            _,stage,src,dst=e; calls.append(stage)
            mapping={i:('main',i,src) for i in range(111)}
            mapping.update({i+111:('main',i,dst) for i in range(111)})
            for r in range(222,word['public']):
                owner=('helper',ci,r); need(owner not in names,'fresh BIT helper');names.add(owner);mapping[r]=owner
                T[abs(ff[str(word['start'][r])]['dim']-ff[str(word['final'][r])]['dim'])]+=1
            need(len(mapping)==len(set(mapping.values()))==659,'injective BIT occurrence')
            for r in range(659,659+word['owned_fields']):mapping[r]=('owned',ci,r-659)
            for ni,move in enumerate(word['program']):
                if move[0]=='MOVE':
                    _,r,a,b=move;rank=abs(ff[str(a)]['dim']-ff[str(b)]['dim'])
                    P[rank]+=1;positions.append([ci,ni,list(mapping[r]),rank,a,b])
        elif op=='QUERY':
            need(e[1]!=e[2] and 0<=min(e[1:])<=max(e[1:])<38,'BIT query owners')
            for pi in range(111):P[1]+=1;positions.append([ci,op,['query_scratch',ci,pi],1])
        elif op=='IDLE_ONE':
            _,owner,ss=e;need(ss and len(ss)==len(set(ss)) and all(1<=s<=18 for s in ss),'BIT idle axes')
            for pi in range(111):P[7*len(ss)]+=1;positions.append([ci,op,['main',pi,owner],7*len(ss)])
    need(calls==[s for s in range(1,19) for _ in range(2)],'paired native chronology')
    for d in caller['diagonal']:
        need(d['q']==1 and d['stages'] and len(d['stages'])==len(set(d['stages'])),'BIT positive endpoint')
        T[1+7*len(d['stages'])]+=111
    need(P==Counter({int(k):v for k,v in receipt['paid'].items()}) and
         T==Counter({int(k):v for k,v in receipt['targets'].items()}),'complete BIT invoice')
    need(sum(T.values())==len(names)==19950,'BIT owner count')
    return dict(ambient=134, rational_frames=len(ff), rational_main_charts=len(charts),
        rational_determinants_digest=digest(determinants),
        finite_prime_exclusion_witness_count=len(denominator_witnesses),
        finite_prime_exclusion_witness_digest=digest(sorted(denominator_witnesses)),
        native_calls=len(calls), fresh_helpers=36*437, productive_fields=len(names),
        paid_positions=len(positions), complete_paid_position_digest=digest(positions),
        reserved_native_banks=36*word['owned_fields'], reserved_serial_query_bank=1,
        rank_surplus=sum(r*T[r] for r in T)-sum(r*P[r] for r in P))


def main():
    p='research/shared-wire-split-composition/'
    w,c,r=read(p+'data/final.json.gz'),read(p+'data/caller.json'),read(p+'FULL-RESULT.json')
    phases=read('research/p104-two-chain-shared-native/retained/runtime/DATA-PHASES.json')
    complex_result=complex_application(w,c,r,phases)
    p='research/paired-query-only-bit/'
    bw,bc,br=read(p+'retained/inputs/BIT-NATIVE-WORD.json.gz'),read(p+'EFREE-CALLER.json.gz'),read(p+'EFREE-RESULT.json')
    bit_result=bit_application(bw,bc,br)
    controls={}
    def reject(name, action):
        try:action()
        except ValueError as error:controls[name]=str(error)
        else:raise ValueError('negative control accepted: '+name)
    alias=deepcopy(c);joint=next(e for e in alias['events'] if e[0]=='J');joint[2][2]=joint[2][0]
    reject('same_frame_main_alias',lambda:complex_application(w,alias,r,phases))
    reordered=deepcopy(c);joint=next(e for e in reordered['events'] if e[0]=='J');joint[1]=2
    reject('wrong_stage',lambda:complex_application(w,reordered,r,phases))
    bad_bit=deepcopy(bw);bad_bit['frames']['0']['A'][1]=bad_bit['frames']['0']['A'][0][:]
    reject('singular_BIT_spectator_basis',lambda:bit_application(bad_bit,bc,br))
    q=w['ports'][0];basis=next(x for x in phases['recipes'] if x['q']==q)['idle_children'][0]['orthogonal_axes'][:8]
    reject('singular_complex_route',lambda:route(q,basis[:-1]+basis[:1],1))
    transform=route(q,basis,1)
    before=terms((1<<j,1) for j in range(9))
    after=terms([(1<<j,1) for j in range(9,17)]+[(q,1)])
    reject('omitted_contact_translation',lambda:boundary(before,after,transform,True))
    print(json.dumps(dict(status='PASS_CURRENT_SOURCE_APPLICATION_MAPS',complex=complex_result,
        bit=bit_result,negative_controls=controls,scope='Exact finite geometry and owner/job binding; universal-width and '
        'complete compiler/precision/cost implications are written separately. Existing full '
        'native/caller endpoint and chart replays reused by source hash.'),indent=2))


if __name__=='__main__':main()
