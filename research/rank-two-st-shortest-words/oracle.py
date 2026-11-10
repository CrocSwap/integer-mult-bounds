"""Complete 3+1 join by faithful regular action, independently of formal2+2.

No author or primary program is imported/executed. Projectors come from
normalized image lines and dual functionals; calls act on literal address pairs.
ToikY with substantial OpenAI Codex assistance. Apache-2.0. Credit the retained
Petalas6449 and Brian4765 proofs, Richardson1989 and Gall's cut lineage.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
from itertools import permutations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = '19a9013a27305a7822fa98b70175cc45caa2ca99ffb0b4620a063338253406f4'
PERMS = tuple(permutations(range(4)))
INDEX = {p:i for i,p in enumerate(PERMS)}
IDENTITY = (0,1,2,3)
SIMPLE = ((1,0,2,3),(0,2,1,3),(0,1,3,2))
ZERO = (0,0,0,0)
UNIT = (1,0,0,1)


def need(ok,message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def decode(raw):
    def unique(items):
        out = {}
        for key,value in items:
            need(key not in out,'duplicate JSON receipt key')
            out[key] = value
        return out
    def bad(value):
        raise ValueError('noninteger/nonfinite receipt number '+value)
    return json.loads(raw,object_pairs_hook=unique,parse_float=bad,parse_constant=bad)


def authenticate():
    raw = (HERE/'SOURCE-PINS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == MANIFEST,'source manifest SHA256')
    manifest = decode(raw)
    need(type(manifest['schema_version']) is int and manifest['schema_version'] == 1,'source schema')
    need(len(manifest['files']) == 3,'three inert source proofs')
    seen = set()
    for row in manifest['files']:
        path = row['local_path']
        need(path.startswith('inputs/') and '..' not in path and path not in seen,'source path')
        seen.add(path)
        data = (HERE/path).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'],'source SHA256 '+path)
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'],'source Git blob '+path)


def compose(a,b):
    return tuple(a[b[i]] for i in range(4))


LEFT = tuple(tuple(INDEX[compose(r,g)] for g in PERMS) for r in SIMPLE)
TARGET = INDEX[compose(SIMPLE[0],SIMPLE[1])]
TARGET_STATE = ((TARGET,1,0,0,1),)
IDENTITY_STATE = ((INDEX[IDENTITY],1,0,0,1),)


def multiply2(A,B,q):
    a,b,c,d = A
    e,f,g,h = B
    return ((a*e+b*g)%q,(a*f+b*h)%q,(c*e+d*g)%q,(c*f+d*h)%q)


def complement(N,q):
    return tuple((a-b)%q for a,b in zip(UNIT,N))


def projectors(q):
    out = set()
    for a in range(q):
        for b in range(q):
            # u=(1,a), v=(1-ab,b), so v*u=1.
            v = (1-a*b)%q
            out.add((v,b,(a*v)%q,(a*b)%q))
    for b in range(q):
        # u=(0,1), v=(b,1).
        out.add((0,0,b,1))
    answer = sorted(out,key=lambda N:sum(x*q**i for i,x in enumerate(N)))
    need(len(answer) == q*(q+1),'complete line-functional projector count')
    need(all(N != ZERO and multiply2(N,N,q) == N and (N[0]*N[3]-N[1]*N[2])%q == 0 for N in answer),'literal rank-one idempotents')
    return answer


def act(state,label,N,q):
    """Act on both scalar identity columns using paired regular addresses."""
    old = {row[0]:row[1:] for row in state}
    route = LEFT[label]
    addresses = set(old)
    addresses.update(route[g] for g in old)
    out = []
    for a in sorted(addresses):
        b = route[a]
        if a > b:
            continue
        X,Y = old.get(a,ZERO),old.get(b,ZERO)
        difference = tuple((y-x)%q for x,y in zip(X,Y))
        shifted = multiply2(N,difference,q)
        first = tuple((x+d)%q for x,d in zip(X,shifted))
        second = tuple((y-d)%q for y,d in zip(Y,shifted))
        if any(first):
            out.append((a,)+first)
        if any(second):
            out.append((b,)+second)
    return tuple(sorted(out))


def family_sets(projector_list,q):
    m = len(projector_list)
    index = {N:i for i,N in enumerate(projector_list)}
    other = [index[complement(N,q)] for N in projector_list]
    A = {(i,other[i],m+j,m+other[j]) for i in range(m) for j in range(m)}
    B = {(i,m+i,other[i],m+other[i]) for i in range(m)}
    need(not A&B,'label strings distinguish the two proposed families')
    return A,B


def scan(q):
    projector_list = projectors(q)
    m = len(projector_list)
    gates = [(r,N) for r in range(3) for N in projector_list]
    single = {act(IDENTITY_STATE,r,N,q):i for i,(r,N) in enumerate(gates)}
    need(len(single) == len(gates),'distinct actual regular-action gates')
    hits = []
    triples = 0
    for i,(r1,N1) in enumerate(gates):
        first = act(TARGET_STATE,r1,N1,q)
        for j,(r2,N2) in enumerate(gates):
            second = act(first,r2,N2,q)
            for k,(r3,N3) in enumerate(gates):
                remaining = act(second,r3,N3,q)
                triples += 1
                if remaining in single:
                    hits.append((i,j,k,single[remaining]))
    hits.sort()
    actual = set(hits)
    need(len(actual) == len(hits),'every ordered four-call word retained once')
    A,B = family_sets(projector_list,q)
    extra,missing = sorted(actual-(A|B)),sorted((A|B)-actual)
    need(not extra and not missing,'COMPLETE_CLASSIFICATION_FALSIFIED '+canonical({'q':q,'extra':extra[:3],'missing':missing[:3]}))
    histogram = Counter(''.join('stu'[g//m] for g in word) for word in hits)
    raw = (canonical(hits)+'\n').encode()
    return {'q':q,'projectors':m,'projector_matrices':[list(N) for N in projector_list],
            'gates':len(gates),'triple_states_checked':triples,'full_words_covered':len(gates)**4,
            'hits':[list(word) for word in hits],'hit_sha256':hashlib.sha256(raw).hexdigest(),
            'hit_label_histogram':dict(sorted(histogram.items())),
            'family_counts':{'A':len(A),'B':len(B)},'classification':'all actual hits equal both proposed families'}


def written(word,projector_list,q):
    m = len(projector_list)
    state = IDENTITY_STATE
    for gate in reversed(word):
        state = act(state,gate//m,projector_list[gate%m],q)
    return state


def difference_witness(state,q):
    actual = {row[0]:row[1:] for row in state}
    target = {row[0]:row[1:] for row in TARGET_STATE}
    for group in sorted(set(actual)|set(target)):
        diff = [(a-b)%q for a,b in zip(actual.get(group,ZERO),target.get(group,ZERO))]
        if any(diff):
            return {'permutation':list(PERMS[group]),'matrix_coefficient':diff}
    raise ValueError('counterfactual word still equals the target')


def semantic_controls():
    q = 3
    Ps = projectors(q)
    m = len(Ps)
    index = {N:i for i,N in enumerate(Ps)}
    P,Q = (1,0,0,0),(1,1,0,0)
    need(multiply2(P,Q,q) != multiply2(Q,P,q),'genuinely noncommuting named projectors')
    p,pc,qq,qc = [index[N] for N in (P,complement(P,q),Q,complement(Q,q))]
    word = (p,pc,m+qq,m+qc)
    need(written(word,Ps,q) == TARGET_STATE,'actual noncommuting familyA positive')
    variants = [('reverse-written-order',tuple(reversed(word))),('omit-last-call',word[:-1]),
                ('duplicate-instead-of-complement',(p,p,m+qq,m+qc)),
                ('substitute-u-label',(p,pc,2*m+qq,2*m+qc))]
    return [{'name':name,'word':list(other),'nonzero_formal_witness':difference_witness(written(other,Ps,q),q)}
            for name,other in variants]


def rational_action(state,label,N):
    R = len(N)
    route = LEFT[label]
    addresses = set(state)
    addresses.update(route[g] for g in state)
    zero = (F(0),)*R
    out = {}
    for a in sorted(addresses):
        b = route[a]
        if a > b:
            continue
        X,Y = state.get(a,zero),state.get(b,zero)
        shift = tuple(sum(N[i][j]*(Y[j]-X[j]) for j in range(R)) for i in range(R))
        first,second = tuple(x+d for x,d in zip(X,shift)),tuple(y-d for y,d in zip(Y,shift))
        if any(first):
            out[a] = first
        if any(second):
            out[b] = second
    return out


def rational_fixture():
    P = ((F(1),F(0)),(F(0),F(0)))
    Q = ((F(1,2),F(1)),(F(1,4),F(1,2)))
    multiply = lambda A,B:tuple(tuple(sum(A[i][k]*B[k][j] for k in range(2)) for j in range(2)) for i in range(2))
    need(multiply(P,P) == P and multiply(Q,Q) == Q and multiply(P,Q) != multiply(Q,P),'rational noncommuting rank-one projectors')
    C = lambda A:tuple(tuple(F(int(i==j))-A[i][j] for j in range(2)) for i in range(2))
    word = ((0,P),(0,C(P)),(1,Q),(1,C(Q)))
    records = []
    for R in (2,3):
        digest = hashlib.sha256()
        for group in range(24):
            for scalar in range(R):
                vector = tuple(F(int(i==scalar)) for i in range(R))
                state = {group:vector}
                for label,N in reversed(word):
                    extended = tuple(tuple(N[i][j] if i<2 and j<2 else F(0) for j in range(R)) for i in range(R))
                    state = rational_action(state,label,extended)
                wanted = INDEX[compose(PERMS[TARGET],PERMS[group])] if scalar<2 else group
                need(state == {wanted:vector},'all faithful rational basis columns including dirty spectator')
                payload = [[g,[str(x) for x in v]] for g,v in sorted(state.items())]
                digest.update((canonical([group,scalar,payload])+'\n').encode())
        records.append({'scalar_roles':R,'regular_basis_columns':24*R,'actual_column_sha256':digest.hexdigest()})
    return {'P':[[str(x) for x in row] for row in P],'Q':[[str(x) for x in row] for row in Q],
            'commute':False,'checks':records,'scope':'Exact rational noncommuting familyA and one individually restored arbitrary dirty spectator; finite corroboration only.'}


def nonfaithful_proxy_control():
    # A genuine algebra element, not a claimed legal four-call word.
    sums = [[0]*4 for _ in range(4)]
    formal = []
    for p in PERMS:
        sign = -1 if sum(p[i]>p[j] for i in range(4) for j in range(i+1,4))%2 else 1
        formal.append([list(p),sign])
        for column in range(4):
            sums[p[column]][column] += sign
    need(all(x == 0 for row in sums for x in row) and any(x[1] for x in formal),'natural proxy is nonfaithful')
    return {'kind':'computed algebra-element toy, not a legal-word fault','natural_matrix':sums,
            'nonzero_formal_coefficients':formal,'consequence':'full regular action is retained for every join'}


def compute():
    authenticate()
    # F2 is deliberately completed as the first classification falsification.
    domains = [scan(q) for q in (2,3,5)]
    return {'schema_version':1,'source_manifest_sha256':MANIFEST,
            'method':'Independent line-functional projectors, faithful left-regular address-pair updates, complete3+1join',
            'written_convention':'G1G2G3G4 acts rightmost first; streamG3G2G1T and matchG4',
            'domains':domains,'semantic_controls':semantic_controls(),'rational_fixture':rational_fixture(),
            'nonfaithful_proxy_control':nonfaithful_proxy_control(),
            'scope':'Complete finite q2/3/5 actual hit sets only. The arbitrary-field equality classification needs the separate written proof; no new inherited tariff/support lemma, physical mixing cost,supplier or kappa.'}


def compare_primary(result):
    primary = decode((HERE/'RESULT.json').read_bytes())
    need(type(primary['schema_version']) is int and primary['schema_version'] == 1,'primary receipt schema')
    need(primary['source_manifest_sha256'] == MANIFEST,'primary receipt source binding')
    own = {row['q']:row for row in result['domains']}
    seen = set()
    for row in primary['domains']:
        q = row['q']
        need(type(q) is int and q in own and q not in seen,'distinct exact primary field domain')
        seen.add(q)
        expected = own[q]
        need(canonical(row['hits']) == canonical(expected['hits']),'ALL ordered actual hit words agree')
        need(canonical(row['projectors']) == canonical(expected['projector_matrices']),'complete literal projector-table agreement')
        need(len(row['projectors']) == expected['projectors'],'projector count agreement')
        families = {'A':row['family_counts']['block'],'B':row['family_counts']['interleaved']}
        need(canonical(families) == canonical(expected['family_counts']),'explicit block/interleaved to A/B family agreement')
        need(canonical(row['hit_label_histogram']) == canonical(expected['hit_label_histogram']),'actual hit-label histogram agreement')
        for key in ('gates','full_words_covered','hit_sha256'):
            need(canonical(row[key]) == canonical(expected[key]),'primary hit-domain receipt '+key)
    need(seen == own.keys(),'all three finite field domains compared')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        retained = decode((HERE/'ORACLE.json').read_bytes())
        need(canonical(retained) == canonical(result),'strict independent receipt drift')
        compare_primary(result)
        print('PASS_RANK_TWO_ST_REGULAR_ACTION_ORACLE')


if __name__ == '__main__':
    main()
