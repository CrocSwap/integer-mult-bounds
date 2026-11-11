"""Independent fraction-free geometry and set-valued funded incidence audit."""
from collections import defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import prod
from pathlib import Path
import sys

root,receipt = map(Path,sys.argv[1:])
r = json.loads(receipt.read_bytes())
pins = {}
for line in Path(__file__).with_name('SOURCES.tsv').read_text().splitlines():
    key,digest,_ = line.split('\t')
    assert key not in pins
    pins[key] = digest
assert pins == r['pins']


def read(path):
    blob = (root/path).read_bytes()
    assert sha256(blob).hexdigest() == pins[path]
    return blob


def det(data):
    a = [list(v) for v in data]
    n = len(a)
    previous = sign = 1
    for i in range(n-1):
        j = next((j for j in range(i,n) if a[j][i]),None)
        if j is None:
            return 0
        if j != i:
            sign *= -1
            a[i],a[j] = a[j],a[i]
        pivot = a[i][i]
        for k in range(i+1,n):
            for j in range(i+1,n):
                v = pivot*a[k][j]-a[k][i]*a[i][j]
                assert v % previous == 0
                a[k][j] = v//previous
            a[k][i] = 0
        previous = pivot
    return sign*a[-1][-1]


def integer(row):
    r = [Fraction(x) for x in row]
    d = prod(x.denominator for x in r)
    return [int(x*d) for x in r]


def norm7(A):
    normal = tuple((-1)**j*det([row[:j]+row[j+1:] for row in A]) for j in range(8))
    assert any(normal)
    assert all(sum(a*b for a,b in zip(row,normal))==0 for row in A)
    return normal


def contained(A,n):
    return not any(sum(x*y for x,y in zip(a,n)) for a in A)


assert det([[1,2],[3,4]]) == -2 and det([[0,2],[3,4]]) == -6
w = json.loads(gzip.decompress(read('research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz')))
prev = json.loads(read('round23/RESULT.json'))
summary = json.loads(read('pr7258/SUMMARY.json'))
assert summary['receipt_sha256'] == pins['round22/RESULT.json']
marks = [b['event'] for b in json.loads(read('pr7209/RESULT.json'))['bank_maps']]
size = {int(i):v['dim'] for i,v in w['frames'].items()}
mat = {int(i):[integer(a) for a in v['B']] for i,v in w['frames'].items()}
normal = {i:norm7(a) for i,a in mat.items() if size[i]==7}
N = w['public']
f = w['start']+[None]*w['owned_fields']
x = [frozenset((j,)) for j in range(N)]+[frozenset()]*w['owned_fields']
history,paid,touch = defaultdict(dict),{},defaultdict(list)


def remember(j,cut,op):
    if x[j]:
        history[f[j]].setdefault((j,x[j]),(cut,op))


for j in range(N):
    remember(j,0,'initial')
for t,row in enumerate(w['program']):
    op,j = row[:2]
    touch[j].append(t)
    if op=='MOVE':
        a,b = row[2:]
        assert f[j]==a and a!=1
        paid[t] = (j,a,b,x[j])
        f[j]=b
    elif op=='ADD':
        k,a=row[2:]
        assert f[j]==f[k]==a
        touch[k].append(t)
        x[j]^=x[k]
    elif op=='SWAP':
        k=row[2]
        touch[k].append(t)
        f[j],f[k]=f[k],f[j]
        x[j],x[k]=x[k],x[j]
        remember(k,t+1,op)
    else:
        assert op in ('INIT','CLEAR') and row[2]!=1
        assert f[j]==(None if op=='INIT' else row[2])
        f[j]=row[2] if op=='INIT' else None
        x[j]=frozenset()
    remember(j,t+1,op)
assert f==w['final']+[None]*w['owned_fields']
assert x==[frozenset((i-111,i)) if 111<=i<222 else frozenset((i,)) for i in range(N)]+[frozenset()]*w['owned_fields']
assert len(paid)==2871


def window(t,j):
    i=touch[j].index(t)
    seq=touch[j]
    return [seq[i-1]+1 if i else 0,seq[i+1] if i+1<len(seq) else len(w['program'])]


def row_basis(rows):
    b={}
    for v in rows:
        while v:
            i=min(v)
            if i not in b:
                b[i]=v
                break
            v^=b[i]
    return b


def rem(basis,v):
    for i,a in sorted(basis.items()):
        if i in v:
            v^=a
    return v


terminal={e:v for e,(_,a,b,v) in paid.items() if b==1}
donors=sorted(set(terminal)-set(marks))
assert len(donors)==523 and len(terminal)==545
want=row_basis(v for chart,v in zip(f,x) if chart==1)
assert len(want)==545
basis={}
for k,e in enumerate(donors+marks):
    v=terminal[e]
    assert not rem(want,v)
    tag=frozenset((k,))
    while v:
        i=min(v)
        if i not in basis:
            basis[i]=(v,tag)
            break
        a,b=basis[i]
        v^=a
        tag^=b
    assert v
assert len(basis)==545
ordered=sorted(basis.items())


def project(v):
    tag=frozenset()
    for i,(a,b) in ordered:
        if i in v:
            v^=a
            tag^=b
    return v,tag


def quotient(raw):
    outside={}
    q=[]
    for v in row_basis(raw).values():
        residual,_=project(v)
        while residual:
            p=min(residual)
            if p not in outside:
                outside[p]=(residual,v)
                break
            a,b=outside[p]
            residual^=a
            v^=b
        if not residual:
            a,b=project(v)
            assert not a
            q.append(frozenset(k-523 for k in b if k>=523))
    return row_basis(q)


def span_agrees(space,expected):
    report=row_basis(frozenset(a) for a in expected)
    assert len(space)==len(report) and all(not rem(report,a) for a in space.values())


cohort=[e for e in sorted(terminal) if size[paid[e][1]]<=6]
assert len(cohort)==185 and cohort==[row['event'] for row in r['incidence']]
mid_charts={a:sorted(i for i,n in normal.items() if contained(mat[a],n)) for a in {paid[e][1] for e in cohort}}
base={b['event']:{frozenset(v['row']) for v in b['source_rows']} for b in prev['scopes'][1]['donors']}
singletons=frozenset(prev['quiet_singleton_mark_positions'])
raw_paid=[defaultdict(set),defaultdict(set)]
raw_all=[defaultdict(set),defaultdict(set)]
witness_count=[0,0]
for e,b in zip(cohort,r['incidence'],strict=True):
    j,a,_,old=paid[e]
    assert j==b['owner'] and a==b['source_chart'] and sorted(old)==b['old_row']
    assert b['quiet_window']==window(e,j)
    assert sorted(b['compatible_literal_charts'])==mid_charts[a]
    for mode,s in enumerate(b['clocks']):
        deadline=window(e,j)[1] if mode else e
        assert s['deadline_cut']==deadline
        assert sorted(v['chart'] for v in s['compatible_charts'])==mid_charts[a]
        for row in s['compatible_charts']:
            g=row['chart']
            candidates={(i,k,h,v) for i,(k,h,target,v) in paid.items() if target==g and i<deadline and v}
            seen={(v['event'],v['owner'],v['source_chart'],frozenset(v['row'])) for v in row['paid_ingress']}
            assert candidates==seen and all(v['after_cut']==v['event']+1 for v in row['paid_ingress'])
            old_cache={(cut,k,op,v) for (k,v),(cut,op) in history[g].items() if cut<=deadline}
            given_cache={(x['cut'],x['owner'],x['operation'],frozenset(x['row'])) for x in row['literal_coframed_cache']}
            assert old_cache==given_cache
            witness_count[mode]+=len(candidates)
            raw_paid[mode][e].update(v for _,_,_,v in candidates)
            raw_all[mode][e].update(v for _,_,_,v in old_cache|candidates)
        if e not in marks:
            q=quotient(base[e]|raw_all[mode][e])
            span_agrees(q,s['W_over_U_basis'])
            span_agrees(row_basis(v&singletons for v in q.values()),s['singleton_basis'])
            span_agrees(quotient(base[e]|raw_paid[mode][e]),s['paid_ingress_only_W_over_U_basis'])
reports=[]
for mode,s in enumerate(r['scopes']):
    q=[quotient(base[e]|raw_all[mode][e]) for e in donors]
    p=[quotient(base[e]|raw_paid[mode][e]) for e in donors]
    useful=[e for e,x in zip(donors,q) if x]
    assert useful==s['quotient_useful_slots']==[21445]
    assert [e for e,x in zip(donors,p) if x and e!=21445]==s['additional_useful_slots_with_old_paid_ingress']==[]
    for key,spaces in [('t',q),('s',[row_basis(v&singletons for v in x.values()) for x in q])]:
        rado=s[key]['rado_subset']
        rank=len(row_basis(v for i in rado for v in spaces[i].values()))
        assert 523-len(rado)+rank==s[key]['rank']==1
        assert sum(bool(x) for x in spaces)==1
        assert len(s[key]['directions'])==1
        a=s[key]['directions'][0]
        assert a['port']==21445
        assert not rem(spaces[donors.index(21445)],frozenset(a['projection']))
    for a in s['paid_refinement_price']:
        h=a['additional_separately_charged_donors']
        assert a['stock_upper']==min(22,14+2*h)
        for price in a['directed'].values():
            p0,p1=map(Fraction,price['raw_net'])
            c0,c1=map(Fraction,price['minimum_split_charge'])
            assert list(map(Fraction,price['charged_net_upper']))==[p0-h*c1,p1-h*c0]
            assert p1-h*c0<0
    reports.append({'scope':s['scope'],'witnesses':witness_count[mode],'donors':523,'t':1,'s':1,'additional_funded_useful':0})
print(json.dumps({'status':'PASS','paid_events':len(paid),'cohort':len(cohort),'literal_chart_incidences':sum(len(b['compatible_literal_charts']) for b in r['incidence']), 'geometry':'independent fraction-free cofactors','scopes':reports},sort_keys=True))
