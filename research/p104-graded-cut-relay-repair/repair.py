#!/usr/bin/env python3
"""Replay a non-improving, exact P104 326→531 relay schedule.

Source: #8041 / #8027 strong-bit.json.gz, verified by SHA-256. The graph is
normalized F₂-linear; a 630-bit row denotes a scalar linear form. All inserted
ADDs are cocharted, and all changed MOVE endpoints are verified by exact
rational projectors. No physical or caller realization is claimed.
"""
import gzip
import hashlib
import json
import sys
import tempfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
HASH = '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
EXPANDED_HASH = 'b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'


def load(path):
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != HASH:
        raise ValueError('graph hash mismatch')
    data = gzip.decompress(raw)
    if hashlib.sha256(data).hexdigest() != EXPANDED_HASH:
        raise ValueError('expanded graph hash mismatch')
    return json.loads(data)


def matmul(a, b):
    return [[sum((a[i][k]*b[k][j] for k in range(8)), Q(0))
             for j in range(8)] for i in range(8)]


def inverse(a):
    v = [[Q(x) for x in row] + [Q(i == j) for j in range(8)]
         for i,row in enumerate(a)]
    for k in range(8):
        pivot = next(i for i in range(k,8) if v[i][k])
        v[k],v[pivot] = v[pivot],v[k]
        f = v[k][k]
        v[k] = [x/f for x in v[k]]
        for i in range(8):
            if i != k:
                f = v[i][k]
                v[i] = [x-f*y for x,y in zip(v[i],v[k])]
    return [r[8:] for r in v]


def projector(spec):
    src = spec['B'] + spec['A']
    m = [[Q(src[j][i]) for j in range(8)] for i in range(8)]
    im = inverse(m)
    assert all(x.denominator % 3 for row in im for x in row)
    d = spec['dim']
    return matmul([[m[i][j] if j < d else Q(0) for j in range(8)]
                   for i in range(8)], im)


def same(a,b):
    return a == b


def builds(p, variant):
    """Transform by zero-based *original* clocks, preserving event order."""
    assert variant in ('original','fault','partial','exact','corrupt')
    anchors = {
        8070:['ADD',2326,1857,326],8071:['ADD',2326,2224,326],
        8072:['MOVE',2326,326,531],8073:['INIT',2327,326],
        8074:['ADD',2327,1855,326],8075:['MOVE',2327,326,1],
        10136:['INIT',2862,531],10137:['ADD',2862,2326,531],
        10138:['MOVE',2862,531,1],11022:['MOVE',3152,328,8],
        11025:['ADD',3153,3152,8],11026:['MOVE',3153,8,0],
        19845:['INIT',3298,0],19951:['ADD',3298,3284,0],
        19952:['MOVE',3298,0,7],19954:['ADD',3299,5,7],
        19958:['ADD',3300,1902,330],19959:['ADD',3300,1908,330],
        30079:['ADD',3550,2326,531],30080:['ADD',3550,2333,531],
        30081:['ADD',3550,3300,531],39319:['CLEAR',3152,8],
    }
    for k,expect in anchors.items(): assert p[k] == expect,(k,p[k])
    if variant == 'original': return [list(row) for row in p]
    fix1 = variant in ('partial','exact','corrupt')
    fixall = variant in ('exact','corrupt')
    out=[]
    for i,row in enumerate(p):
        row=list(row)
        if i in (8070,8071): continue
        row={8073:['INIT',2327,531],8074:['ADD',2327,2326,531],
             8075:['MOVE',2327,531,1]}.get(i,row)
        if fix1:
            row={10136:['INIT',2862,326],10137:['ADD',2862,2224,326],
                 10138:['MOVE',2862,326,1]}.get(i,row)
        if fixall:
            if i==11022:row=['MOVE',3152,328,0]
            if i==11025:continue
            if i==19845:
                out.extend([['INIT',3298,0],['ADD',3298,117,0]])
                if variant != 'corrupt':out.append(['ADD',3298,3152,0])
                out.append(['ADD',3298,3153,0])
                continue
            if 19846 <= i <= 19951:continue
            if i in (19954,19958,19959,30079,30080):continue
            if i==39319:row=['CLEAR',3152,0]
        out.append(row)
        if fix1 and i==10138:out.append(['ADD',2862,2861,1])
        if fixall and i==11026:out.append(['ADD',3153,3152,0])
    return out


def forward(g,p):
    c=dict(enumerate(g['start']))
    v={i:1<<i for i in c}
    clears=[]
    for op,d,*a in p:
        if op=='INIT': assert d not in c;c[d]=a[0];v[d]=0
        elif op=='CLEAR':
            assert d>=g['public'] and c[d]==a[0]
            clears.append((d,c[d],v[d]));del c[d],v[d]
        elif op=='ADD':
            x,chart=a;assert c[d]==c[x]==chart;v[d]^=v[x]
        elif op=='MOVE':
            source,dest=a;assert c[d]==source;c[d]=dest
        elif op=='SWAP':
            x,=a;c[d],c[x]=c[x],c[d];v[d],v[x]=v[x],v[d]
        else:raise ValueError(op)
    assert c==dict(enumerate(g['final']))
    return [v[i] for i in range(g['public'])],clears


def reverse(g,p):
    """Independent transposed execution: one 630-bit column per live owner."""
    c=dict(enumerate(g['final']))
    v={i:1<<i for i in c}
    for op,d,*a in reversed(p):
        if op=='CLEAR':assert d not in c;c[d]=a[0];v[d]=0
        elif op=='INIT':assert c[d]==a[0];del c[d],v[d]
        elif op=='ADD':
            x,chart=a;assert c[d]==c[x]==chart;v[x]^=v[d]
        elif op=='MOVE':source,dest=a;assert c[d]==dest;c[d]=source
        elif op=='SWAP':
            x,=a;c[d],c[x]=c[x],c[d];v[d],v[x]=v[x],v[d]
        else:raise ValueError(op)
    assert c==dict(enumerate(g['start']))
    return [v[i] for i in range(g['public'])]


def rank(rows):
    b={}
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k not in b:b[k]=x;break
            x^=b[k]
    return len(b)


def hist(g,p):
    dims={int(k):x['dim'] for k,x in g['frames'].items()}
    return Counter(abs(dims[b]-dims[a]) for op,d,*args in p
                   if op=='MOVE' for a,b in [args])


def support(x):return [i for i in range(630) if (x>>i)&1]


def main():
    if sys.flags.optimize:raise RuntimeError('Run without optimization')
    g=load(HERE/'strong-bit.json.gz')
    assert g['public']==630 and len(g['program'])==39600
    projector_cache={i:projector(g['frames'][str(i)]) for i in (0,1,8,326,328,531)}
    for small,large in [(326,531),(531,1),(326,1),(0,328),(8,328)]:
        a,b=projector_cache[small],projector_cache[large]
        assert same(matmul(a,b),a) and same(matmul(b,a),a),(small,large)
    dims={i:g['frames'][str(i)]['dim'] for i in projector_cache}
    assert (dims[326],dims[531],dims[1],dims[328],dims[8],dims[0])==(6,7,8,6,1,0)

    rows={};clears={};progs={}
    for mode in ('original','fault','partial','exact','corrupt'):
        progs[mode]=builds(g['program'],mode)
        rows[mode],clears[mode]=forward(g,progs[mode])
    old=rows['original'];new=rows['exact']
    assert old==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(630)]
    assert rank(old)==rank(new)==630
    assert new==old
    errors={m:[i for i in range(630) if rows[m][i]!=old[i]]
            for m in ('fault','partial','exact','corrupt')}
    assert errors['fault']==[0,11,117,223,224,230,249,250,251]
    assert errors['partial']==[117]
    assert errors['exact']==[]
    assert errors['corrupt']==[117]
    chart1=[i for i in range(630) if g['final'][i]==1]
    assert len(chart1)==505 and all(rows['partial'][i]==old[i] for i in chart1)
    assert all(len(x)==3433 and all(v for _,_,v in x) for x in clears.values())
    assert len({d for d,c,v in clears['exact']})==3433
    c0={d:(c,v) for d,c,v in clears['original']}
    c1={d:(c,v) for d,c,v in clears['exact']}
    changed_clears={str(d):{'old_chart':c0[d][0],'new_chart':c1[d][0],
                           'value_changed':c0[d][1]!=c1[d][1]}
                    for d in c0 if c0[d]!=c1[d]}

    for mode in ('original','exact','corrupt'):
        dual=reverse(g,progs[mode])
        assert all(((rows[mode][o]>>i)&1)==((dual[i]>>o)&1)
                   for o in range(630) for i in range(630))
    assert reverse(g,progs['exact'])==reverse(g,progs['original'])
    assert reverse(g,progs['corrupt'])!=reverse(g,progs['original'])
    h0=hist(g,progs['original']);h1=hist(g,progs['exact'])
    assert sum(h0.values())==sum(h1.values())==2803
    assert h1-h0==Counter({6:1}) and h0-h1==Counter({5:1})
    # Source-byte negative control exercises the same loader used above.
    raw=(HERE/'strong-bit.json.gz').read_bytes()
    with tempfile.TemporaryDirectory(prefix='p104-graph-control-') as tmp:
        bad=Path(tmp)/'bad.gz'
        bad.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
        try: load(bad)
        except ValueError as e: assert str(e)=='graph hash mismatch'
        else: raise AssertionError('corrupted source accepted')
    result={
        'source_sha256':HASH,'expanded_sha256':EXPANDED_HASH,
        'scope':'All-input normalized F2 linear 630-output local graph. No physical, caller, or bound claim.',
        'projector_nesting_checked':[[326,531],[531,1],[326,1],[0,328],[8,328]],
        'output_rank':rank(new),'exact_public_rows':630,'adjoint_matches_original':True,
        'partial_wrong_rows':errors['partial'],'fault_wrong_rows':errors['fault'],
        'corrupt_control_wrong_rows':errors['corrupt'],
        'partial_exact_chart1_outputs':len(chart1),
        'corrupt_control_117_delta_support':support(rows['corrupt'][117]^old[117]),
        'private_clears':len(clears['exact']),'symbolically_dirty_clears':sum(bool(v) for _,_,v in clears['exact']),
        'changed_private_clear_values_or_charts':changed_clears,
        'original_paid_histogram':dict(sorted(h0.items())),
        'new_paid_histogram':dict(sorted(h1.items())),
        'one_word_paid_count':sum(h1.values()),
        'one_word_rank_sum_delta':sum(k*(h1[k]-h0[k]) for k in set(h0)|set(h1)),
        'corrupted_source_rejected':True,
    }
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
