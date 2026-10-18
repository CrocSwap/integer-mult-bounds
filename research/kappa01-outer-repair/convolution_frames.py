#!/usr/bin/env python3
"""Exact source-carry / target-read probes for symmetric convolution frames."""
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
BASE = '997e6a9ca7b4f95d50e366f61412fd640d72a88a'
N = 9


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def blob(path):
    return subprocess.check_output(['git', 'show', BASE+':'+path], cwd=ROOT)


def basis(vectors):
    pivots = {}
    for x in vectors:
        while x:
            p = x.bit_length()-1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return list(pivots.values())


def contains(vectors, x):
    return len(basis(list(vectors)+[x])) == len(basis(vectors))


def dot(x, y):
    return (x & y).bit_count() & 1


def radical_dimension(vectors):
    vectors = basis(vectors)
    gram = [sum(dot(a,b) << j for j,b in enumerate(vectors)) for a in vectors]
    return len(vectors)-len(basis(gram))


def symmetric_solution(carry, read):
    positions = [(i,j) for i in range(N) for j in range(i,N)]
    index = {pair:k for k,pair in enumerate(positions)}
    eq = []
    for vectors, value in ((carry, 1), (read, 0)):
        for q in basis(vectors):
            for i in range(N):
                mask = sum(1 << index[tuple(sorted((i,j)))] for j in range(N) if q >> j & 1)
                eq.append(mask | ((value * (q >> i & 1)) << len(positions)))
    pivots = {}
    varmask = (1 << len(positions))-1
    for row in eq:
        while row & varmask:
            p = (row & varmask).bit_length()-1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
        else:
            if row:
                return None
    solution = 0
    for p in sorted(pivots):
        row = pivots[p]
        value = ((row >> len(positions)) ^ ((row & solution).bit_count() & 1)) & 1
        solution |= value << p
    matrix = [0]*N
    for k,(i,j) in enumerate(positions):
        if solution >> k & 1:
            matrix[i] |= 1 << j
            matrix[j] |= 1 << i
    def mv(q):
        return sum(dot(row,q) << i for i,row in enumerate(matrix))
    require(all(mv(q)==q for q in carry), 'source eigenvalue')
    require(all(mv(q)==0 for q in read), 'target eigenvalue')
    return matrix


def reg(address):
    return address[1] + (704 if address[0]=='C' else 0)


def add(a,b,c):
    result = a.copy()
    for key, value in b.items():
        result[key] = result.get(key, 0)+c*value
        if not result[key]:
            del result[key]
    return result


def apply(rows, op, reverse=False):
    kind = op[0]
    d = reg(op[1])
    if kind in ('add','copy'):
        s = reg(op[2])
    if kind=='add':
        c = Fraction(op[3],op[4])
        if reverse:
            rows[s] = add(rows[s],rows[d],c)
        else:
            rows[d] = add(rows[d],rows[s],c)
    elif kind=='scale':
        c = Fraction(op[2],op[3])
        rows[d] = {key:c*value for key,value in rows[d].items() if c*value}
    elif kind=='copy':
        if reverse:
            rows[s] = add(rows[s],rows[d],1)
            rows[d] = {}
        else:
            rows[d] = rows[s].copy()
    elif kind=='clear':
        rows[d] = {}
    else:
        raise RuntimeError(kind)


def main():
    archive = blob('research/community-frontier1042-audit/selected-replay.tar.gz')
    require(hashlib.sha256(archive).hexdigest()=='22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754','archive pin')
    with tarfile.open(fileobj=io.BytesIO(archive)) as t:
        raw = t.extractfile('slots/local/CANONICAL-WORD.json.gz').read()
    require(hashlib.sha256(raw).hexdigest()=='16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219','word pin')
    word = json.loads(gzip.decompress(raw))
    native_raw = blob('research/involutive-walsh-lift/evidence/WALSH-RETARGET-NATIVE.json.gz')
    require(hashlib.sha256(native_raw).hexdigest()=='5bfd2c228533e0d20d62b867ef9c1b57c235399478232e1beee875d6838051db','native program pin')
    native = json.loads(gzip.decompress(native_raw))
    p = native['programs']['forward']
    frames = word['frames']
    labels = word['ports']
    require(len(set(labels))==112 and all(dot(q,q) for q in labels), 'distinct norm-one source labels')
    native_code = blob('research/involutive-walsh-lift/native.py')
    require(hashlib.sha256(native_code).hexdigest()=='8134106fb8a9ee8b065c51d950b41ef31ff3486a9d4da71f33c6a406ee054698','native Clifford checker pin')
    namespace = {}
    exec(compile(native_code, 'pinned-native.py', 'exec', optimize=0), namespace)
    native_tableau = namespace['tableau'](namespace['frame']([30],N))
    require(native_tableau[1]==(28,14,0), 'actual frame30 fails translation commutation')
    frame_radicals = Counter(radical_dimension(f) for f in frames)
    degenerate_climbs = sum(e[0]=='climb' and (radical_dimension(frames[e[3]]) or radical_dimension(frames[e[4]]))>0 for e in p)
    start = p.index(['phase','A'])
    end = p.index(['phase','exit_adapters'])
    # Inspect every helper state immediately after a native frame transition,
    # plus the helper entrances. These are scalar-coordinate sensitivities.
    checkpoints = {start: [(r,word['start'][r]) for r in range(224,704)]}
    for i in range(start+1,end):
        e = p[i]
        if e[0]=='climb' and e[2]>=224:
            checkpoints[i] = [(e[2],e[4])]
    rows = [{} for _ in range(712)]
    for j in range(112):
        rows[112+j] = {j:Fraction(1)}
    readers = {}
    for i in range(len(p)-1,-1,-1):
        if i in checkpoints:
            for r,f in checkpoints[i]:
                readers[i,r] = rows[r].copy()
        if p[i][0]=='scalar':
            apply(rows,p[i][1],True)
    require(all(rows[j]=={j:Fraction(1)} and rows[112+j]=={j:Fraction(1)} for j in range(112)), 'complete target scalar Jacobian')
    require(all(not rows[j] for j in range(224,712)), 'dirty helper sensitivity cancels')
    rows = [{} for _ in range(712)]
    for j in range(112):
        rows[j] = {j:Fraction(1)}
    counts = Counter()
    records = []
    for i,e in enumerate(p):
        if e[0]=='scalar':
            apply(rows,e[1])
        if i not in checkpoints:
            continue
        for r,f in checkpoints[i]:
            carry_ports = list(rows[r])
            read_ports = list(readers[i,r])
            carry = basis(labels[j] for j in carry_ports)
            read = basis(labels[j] for j in read_ports)
            solution = symmetric_solution(carry,read)
            orthogonal = all(not dot(c,q) for c in carry for q in read)
            intersection = len(carry)+len(read)-len(basis(carry+read))
            fits_source = all(contains(frames[f],q) for q in carry)
            fits_target = all(not dot(q,u) for q in read for u in frames[f])
            require((solution is not None)==(orthogonal and intersection==0), 'symmetric feasibility iff compatibility')
            key = (solution is not None,orthogonal,intersection>0,fits_source,fits_target)
            counts[str(key)] += 1
            if (i,r) in ((13759,445),(9466,228),(15459,283)):
                records.append(dict(event=i,role=r,frame=f,frame_basis=frames[f],
                    event_contents=e,next_event=p[i+1],timing='after event, before next event; zero-based program indices',
                    carry_basis=carry,read_basis=read,carry_ports=carry_ports,read_ports=read_ports,
                    carry_coefficients=[dict(port=j,label=labels[j],coefficient=str(rows[r][j])) for j in sorted(rows[r])],
                    read_coefficients=[dict(port=j,label=labels[j],coefficient=str(readers[i,r][j])) for j in sorted(readers[i,r])],
                    carry_radical_dimension=radical_dimension(carry),frame_radical_dimension=radical_dimension(frames[f]),
                    orthogonal=orthogonal,intersection_dimension=intersection,
                    canonical_contains_carry=fits_source,canonical_orthogonal_to_read=fits_target,
                    symmetric_matrix=solution))
    require(all(rows[j]=={j:Fraction(1)} and rows[112+j]=={j:Fraction(1)} for j in range(112)), 'complete source scalar Jacobian')
    require(all(not rows[j] for j in range(224,712)), 'source material cleaned from helpers')
    require(len(records)==3, 'three fixed witnesses')
    negative = next(r for r in records if r['role']==445)
    require(set(negative['carry_ports'])=={46,20} and set(negative['read_ports'])=={25,2}, 'negative support witness')
    require(labels[46]^labels[20]==labels[25]^labels[2]==45, 'shared nonzero carry-reader vector')
    positive = next(r for r in records if r['role']==283)
    require(positive['carry_radical_dimension']>0 and positive['symmetric_matrix'] is not None, 'degenerate carry still admits a symmetric frame')
    # Exhaust all 16 binary subspaces in dimension three and all 256 pairs.
    spaces = {}
    for subset in range(128):
        b = basis(q for q in range(1,8) if subset >> (q-1) & 1)
        key = tuple(q for q in range(8) if contains(b,q))
        spaces[key] = b
    require(len(spaces)==16, 'complete F2^3 subspace census')
    for carry in spaces.values():
        for read in spaces.values():
            expected = all(not dot(c,r) for c in carry for r in read) and len(basis(carry+read))==len(carry)+len(read)
            require((symmetric_solution(carry,read) is not None)==expected, 'small exhaustive solver control')
    out=dict(status='POINTWISE CONTENT-CONSTRAINT AUDIT; NO UNIVERSAL COMPLEX-CIRCUIT OBSTRUCTION',
             source_commit=BASE,checkpoint_count=sum(map(len,checkpoints.values())),
             counts_key=['symmetric_solution_exists','orthogonal','nonzero_intersection','canonical_contains_carry','canonical_orthogonal_to_read'],
             counts=dict(counts),records=records,
             frame_radical_dimensions=dict(frame_radicals),degenerate_persistent_climb_occurrences=degenerate_climbs,
             original_frame30_X2_conjugate=dict(X=28,Z=14,phase_mod4=0),
             controls=dict(full_prefix_and_suffix_scalar_jacobians='exact Fraction replay',small_subspace_pairs=256),
             limits=['Scalar Jacobian labels become necessary constraints only within the stated fixed carry/read model.',
                     'Pointwise feasibility alone gives no common frame at gates, transition budget, exact phase lift, or supplier.',
                     'Independent changes of scalar schedule, content representation, nonconvolution operations, and arbitrary complex circuits remain open.'])
    (Path(__file__).resolve().parent/'CONVOLUTION-RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(dict(counts))
    for record in records:
        print('witness', record['event'],record['role'],'carry',record['carry_basis'],'read',record['read_basis'],'feasible',record['symmetric_matrix'] is not None)
    print('PASS pinned scalar replay, 2886 helper checkpoints, symmetric constraints, and 256 independent small-pair controls')


if __name__=='__main__':
    main()
