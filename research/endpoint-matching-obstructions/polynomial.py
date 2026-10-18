"""Exact gauge, polynomial identity and premise checks; no polynomial search."""
from collections import defaultdict
from fractions import Fraction
from fractions import Fraction as Q
from itertools import permutations

def check_identity(records, n, certificate):
    """Replay a polynomial identity directly, without the search algebra helpers."""
    total = defaultdict(Fraction)
    for index, shift, scale in certificate:
        if type(index) is not int or not 0 <= index < len(records):
            raise ValueError('bad generator index')
        if len(shift) != n or any(type(v) is not int or v < 0 for v in shift):
            raise ValueError('bad exponent')
        scale = Fraction(scale)
        for mask, coefficient in records[index]['poly'].items():
            monomial = tuple(shift[i] + ((mask >> i) & 1) for i in range(n))
            total[monomial] += scale * coefficient
    total = {m: c for m, c in total.items() if c}
    if total != {(0,) * n: Fraction(1)}:
        raise ValueError('unit identity does not replay')

def reconstruct(coefficients, selection, normalization):
    blocks = len(selection['entry_support'])
    active = [9*k+j for k,s in enumerate(selection['entry_support']) for j,v in enumerate(s) if v]
    tree = normalization['tree_entries']
    assert normalization['active_entries'] == active
    assert len(tree)==len(set(tree)) and set(tree)<=set(active)
    # A tree-edge normalization is valid precisely because no cycle is fixed.
    adjacency=defaultdict(set)
    for e in tree:
        k,j=divmod(e,9);r,c=divmod(j,3);a,b=3*k+c,3*(k+1)+r
        reached,pending=set(),[a]
        while pending:
            v=pending.pop()
            if v in reached:continue
            reached.add(v);pending.extend(adjacency[v]-reached)
        assert b not in reached
        adjacency[a].add(b);adjacency[b].add(a)
    old_n=len(active)+blocks
    retained=[i for i in range(old_n) if i>=len(active) or active[i] not in tree]
    assert normalization['old_variables']==old_n
    assert normalization['retained_variables']==retained
    index={old:new for new,old in enumerate(retained)}
    entry_variables={e:index[i] for i,e in enumerate(active) if i in index}
    full=[]
    for i,r in enumerate(coefficients):
        if r['frame']!=selection['frames'][r['column']]:
            full.append({'kind':'off_target','record':i,'poly':r['poly']})
    for k in range(blocks):
        polynomial={0:-1}
        for perm in permutations(range(3)):
            mask=(1<<(9*blocks+k))|sum(1<<(9*k+3*r+perm[r]) for r in range(3))
            polynomial[mask]=(-1)**sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3))
        full.append({'kind':'inverse_determinant','block':k,'poly':polynomial})
    records,sources=[],[]
    for source in full:
        p=defaultdict(int);survives=False
        for mask,c in source['poly'].items():
            entries={i for i in range(9*blocks) if mask&(1<<i)}
            if not entries<=set(active):continue
            survives=True
            converted=sum(1<<entry_variables[e] for e in entries if e not in tree)
            for k in range(blocks):
                if mask&(1<<(9*blocks+k)):converted|=1<<index[len(active)+k]
            p[converted]+=c
        # The producer drops only generators empty before normalization.
        if source['kind']=='off_target' and not survives:continue
        records.append({**source,'poly':{m:c for m,c in p.items() if c}});sources.append(source)
    return records,len(retained),sources

def check_core(coefficients,selection,result,core,cnf):
    records,n,sources=reconstruct(coefficients,selection,result['normalization'])
    assert n==result['variables'] and len(records)==result['constraints']
    certificate=result['answer']['certificate']
    check_identity(records,n,certificate)
    used=sorted({t[0] for t in certificate})
    assert used==core['used_generators']
    active=set(result['normalization']['active_entries']);tree=set(result['normalization']['tree_entries'])
    nonzero=set(core['nonzero_entries']);zero=set(core['zero_entries'])
    absent={tuple(x) for x in core['absent_frames']}
    assert nonzero<=tree and not zero&active
    blocks=len(selection['entry_support'])
    assert all(0<=e<9*blocks for e in zero)
    for i in used:
        source=sources[i]
        if source['kind']=='off_target':
            r=coefficients[source['record']]
            if r['rank']==3:assert (r['column'],r['frame']) in absent
        for mask in source['poly']:
            entries={e for e in range(9*blocks) if mask&(1<<e)}
            if entries-active:assert entries&zero
            else:assert entries&tree<=nonzero
    selectors={(v[1],v[2]):i for i,v in enumerate(cnf['labels']) if v and v[0]=='frame'}
    return [-(e+1) for e in core['nonzero_entries']]+[e+1 for e in core['zero_entries']]+[selectors[tuple(f)] for f in core['absent_frames']]
