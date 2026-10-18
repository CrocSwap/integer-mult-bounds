# SPDX-License-Identifier: Apache-2.0
"""Mason Hale/Codex PR2696 literal replay, extended by Tekalign/Codex.
Adds anticipatory corrections, checks six pre-life hosts and checks all twelve
source-recovery assertions at operator IDs47 through58.
"""
import json,gzip,hashlib
from collections import Counter,defaultdict
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
@lru_cache(None)
def span(vs):
    s={0}
    for v in vs:s|={x^v for x in tuple(s)}
    return frozenset(s)
def S(vs):return span(tuple(vs))
def rank(vs):return len(S(vs)).bit_length()-1
def dm(s):return len(s).bit_length()-1
FULL=S([1<<i for i in range(9)])
def im(cols,x):
    a=0
    for i,c in enumerate(cols):
        if x>>i&1:a^=c
    return a
def regs(g):return g[1:3] if g[0]=='add' else g[1:2]
def nt(r):return not 112<=r<224
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def chronological(w):
    d=defaultdict(list)
    for op,(p,r,*_) in enumerate(w['warps'],1):d[p].append(['warp',r,op])
    b=[]
    for i in range(len(w['B'])+1):
        b+=d[i]
        if i<len(w['B']):b.append(w['B'][i])
    return b

def check_frames(w):
    live=set(range(704))-set(w['removed'])
    cur={r:S([w['ports'][r]]) if r<112 else S(w['start_extra'].get(str(r),[])) for r in live}
    ends={r:FULL for r in live}
    for i,p in enumerate(w['ports']):ends[112+i]=frozenset(x for x in range(512) if (x&p).bit_count()%2==0)
    for r,vs in w['helper_final'].items():ends[int(r)]=S(vs)
    start=cur.copy();counts=Counter();bysection={};sections={}
    def climb(r,vs):
        s=S(vs);assert cur[r]<=s,(r,cur[r],s)
        d=dm(s)-dm(cur[r]);cur[r]=s
        if d:counts[d]+=1
    def warp(r,op,old,new):
        cols=w['warps'][abs(op)-1][2]
        assert len(S(cols))==512
        assert cur[r]==S(old)
        # Check positive-direction map for either sign, without computing inverse.
        a,b=(old,new) if op>0 else (new,old)
        assert frozenset(im(cols,x) for x in S(a))==S(b)
        cur[r]=S(new)
    for g in w['A']:
        if g[0]=='warp':warp(*g[1:])
        else:
            for r in regs(g):climb(r,g[-1])
    bysection['A']=dict(counts);prev=counts.copy()
    lev={int(k):S(v) for k,v in w['target_levels'].items()}
    assert all(cur[112+t]==lev.get(t,S([])) for t in range(112))
    paths=[]
    for r,vs in zip(w['centers'],w['center_frames']):
        s=S(vs);assert cur[r]==s
        targets=[g[1]-112 for g in w['cut'] if g[2]==r]
        frames=sorted({lev.get(t,S([])) for t in targets},key=lambda s:-len(s))
        ds=[]
        for f in frames:
            assert f<=s
            d=dm(s)-dm(f)
            if d:counts[d]+=1;ds.append(d)
            s=f
        paths.append({'center':r,'start_rank':rank(vs),'target_offsets':targets,'reader_lines':[sorted(f-{0}) for f in frames],'paid_degrees':ds})
    bysection['cut']=dict(counts-prev);prev=counts.copy()
    ops=defaultdict(list)
    for op,rec in enumerate(w['warps'],1):ops[rec[0]].append((op,rec))
    for i in range(len(w['B'])+1):
        for op,(_,r,cols,old,new) in ops[i]:warp(r,op,old,new)
        if i<len(w['B']):
            g=w['B'][i]
            for r in regs(g):climb(r,g[-1])
    bysection['B']=dict(counts-prev);prev=counts.copy()
    for g in w['restore']:
        for r in regs(g):climb(r,g[-1])
    bysection['restore']=dict(counts-prev);prev=counts.copy()
    for r in live:climb(r,ends[r])
    bysection['ends']=dict(counts-prev)
    inventory=Counter(dm(ends[r])-dm(start[r]) for r in live if r>=224)
    assert counts==Counter({int(k):v for k,v in w['report']['local_profile'].items()})
    assert inventory==Counter({int(k):v for k,v in w['report']['width_inventory'].items()})
    return {'profile':dict(sorted(counts.items())),'section_profiles':bysection,'inventory':dict(sorted(inventory.items())),'center_paths':paths},start,ends

def check_cleanup(w):
    restored=set(map(int,w['helper_final']))
    cold=lambda r:r+704 if r in restored else r
    forward=w['A'][w['prelude_events']:]+chronological(w)+w['restore']
    expected=[]
    for g in reversed(forward):
        if g[0]=='warp':expected.append(['warp',cold(g[1]),-g[2]])
        elif nt(g[1]):
            if g[0]=='add':expected.append(['add',cold(g[1]),cold(g[2]),-g[3],g[4]])
            else:expected.append(['scale',cold(g[1]),g[3],g[2]])
    assert expected==[g[:-1] for g in w['cleanup']]
    assert all(S(g[-1])==FULL for g in w['cleanup'])
    return len(expected)

def algebra(w):
    # A monomial records its operations oldest-first; appending an inverse
    # cancels the newest symbol. No native/generator/audit modules imported.
    live=set(range(704))-set(w['removed']);cold=set(map(int,w['helper_final']))
    assert all(112<=x['target']<224 and x['source'] in {273,275,289,291,305,321} for x in w['initial_corrections'])
    program=[['correction',x] for x in w['initial_corrections']]+w['precondition']+w['compensation']+w['A']+w['cut']+chronological(w)+w['restore']
    result={}
    for dual in [False,True]:
        rows={r:{(r,()):F(1)} for r in live}
        rows.update({704+r:{} for r in cold})
        def apply(g):
            op=g[0]
            if op=='correction':
                x=g[1];t,s=x['target'],x['source'];q=F(x['coefficient'])
                ops=list(reversed(x['operator_word']))
                if dual:
                    t,s,q=s,t,-q
                    ops=[-(abs(v)+1000)*(1 if v>0 else -1) for v in x['operator_word']]
                for (r,word),c in list(rows[s].items()):
                    for v in ops:word=word[:-1] if word and word[-1]==-v else word+(v,)
                    key=(r,word);value=rows[t].get(key,F(0))+q*c
                    if value:rows[t][key]=value
                    else:rows[t].pop(key,None)
            elif op=='add':
                t,s=g[1:3];q=F(g[3],g[4]);assert t!=s
                if dual:t,s,q=s,t,-q
                for term,c in list(rows[s].items()):
                    v=rows[t].get(term,F(0))+q*c
                    if v:rows[t][term]=v
                    else:rows[t].pop(term,None)
            elif op=='scale':
                q=F(g[2],g[3]);q=1/q if dual else q
                rows[g[1]]={term:q*c for term,c in rows[g[1]].items()}
            elif op=='warp':
                d=g[2]
                if not dual and 46<d<=58:
                    assert rows[g[1]]=={(g[1],()):F(1)},('new lender not restored',g,rows[g[1]])
                if dual:d=(abs(d)+1000)*(1 if d>0 else -1)
                rows[g[1]]={(r,word[:-1] if word and word[-1]==-d else word+(d,)):c for (r,word),c in rows[g[1]].items()}
            else:raise AssertionError(op)
        for g in program:apply(g)
        if not dual:
            assert all(rows[112+t]=={(112+t,()):F(1),(t,()):F(1)} for t in range(112))
            assert all(rows[r]=={(r,()):F(1)} for r in cold)
            assert all(not any(var in cold-{r} for (var,word) in rows[r]) for r in live)
        for g in w['cleanup']:apply(g)
        for r in live:
            exp={(r,()):F(1)}
            if dual and r<112:exp[(112+r,())]=F(-1)
            if not dual and 112<=r<224:exp[(r-112,())]=F(1)
            assert rows[r]==exp,(dual,r,rows[r])
        assert all(not rows[704+r] for r in cold)
        result['dual' if dual else 'forward']='PASS'
    return result
