"""Separate version-label cost oracle and exact-grid primitive interpreter.
No search/constructor/predecessor imports. Apache-2.0; OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction
from itertools import product


def require(ok,msg):
    if not ok:raise ValueError(msg)


def logarithm(q):
    require(q!=0,'zero coefficient')
    a,b=abs(q.numerator),q.denominator
    require(a&(a-1)==0 and b&(b-1)==0,'not dyadic power')
    return a.bit_length()-b.bit_length()


def direct_records(raw,slots):
    old=[0]*8;new=[0]*8;tot=[0]*8;seen=[0]*8;done=set();records=[]
    for op in raw:
        if op[0]=='scale':tot[op[1]]+=logarithm(Fraction(op[2],op[3]))
    for op in raw:
        if op[0]=='scale':old[op[1]]+=logarithm(Fraction(op[2],op[3]));continue
        _,d,s,a,b,_=op
        for r in (d,s):
            if r in slots and r not in done and slots[r]==seen[r]:
                records.append(('scale',r,tot[r]));new[r]=tot[r];done.add(r)
        e=logarithm(Fraction(a,b))+new[d]-old[d]-new[s]+old[s]
        records.append(('add',d,s,e));seen[d]+=1;seen[s]+=1
    for r in slots:
        if r not in done:records.append(('scale',r,tot[r]))
    return records


def price(records,mode,base):
    # Version labels change on writes; SCALE retains the label but shifts power.
    version=list(range(8));power=[0]*8;work_version=-1;work_power=0
    total=base;next_version=8;known_zero=False
    for op in records:
        if op[0]=='scale':power[op[1]]+=op[2];continue
        _,d,s,e=op
        if e:
            required_power=power[s]+e
            fresh=1+abs(e)
            reuse=abs(required_power-work_power) if work_version==version[s] else 10**9
            total+=(min(fresh,reuse) if mode=='cache' else fresh)+1
            work_version=version[s];work_power=required_power;known_zero=False
        else:total+=1
        version[d]=next_version;next_version+=1;power[d]=0
        if mode=='per_add':total+=1;known_zero=True;work_version=-1
        if mode=='clean' and(e or not known_zero):total+=1;known_zero=True;work_version=-1
    if not known_zero:total+=1
    return total


def census(raw):
    uses=[0]*8
    for op in raw:
        if op[0]=='add':uses[op[1]]+=1;uses[op[2]]+=1
    base=sum(abs(logarithm(Fraction(op[2],op[3])))+int(Fraction(op[2],op[3])<0)for op in raw if op[0]=='scale')
    order=[7,6,2,1,0];hist={m:Counter()for m in ('per_add','clean','defer','cache')}
    for choices in product(*(range(uses[r]+1)for r in order)):
        slots=dict(zip(order,choices));slots[5]=7
        records=direct_records(raw,slots)
        for mode in hist:hist[mode][price(records,mode,base)]+=1
    return {mode:dict(sorted(h.items()))for mode,h in hist.items()}


def primitive_replay(stream):
    unit=1<<64
    rows=[[unit*int(i==j)for j in range(9)]for i in range(9)]
    peak=unit;depth=0;trace=[]
    for op in stream:
        t,d=op[:2]
        require(type(d)is int and 0<=d<9,'primitive destination')
        if t=='copy':rows[d]=rows[op[2]].copy()
        elif t=='clear':rows[d]=[0]*9
        elif t=='plus':rows[d]=[x+y for x,y in zip(rows[d],rows[op[2]])]
        elif t=='minus':rows[d]=[x-y for x,y in zip(rows[d],rows[op[2]])]
        elif t=='double':rows[d]=[2*x for x in rows[d]]
        elif t=='neg':rows[d]=[-x for x in rows[d]]
        elif t=='half':
            require(all(x%2==0 for x in rows[d]),'inexact grid halving')
            rows[d]=[x//2 for x in rows[d]]
        else:raise ValueError('unknown primitive')
        peak=max(peak,sum(abs(x)for x in rows[d]))
        for x in rows[d]:
            if x:depth=max(depth,64-((abs(x)&-abs(x)).bit_length()-1))
        trace.append(tuple(rows[d]))
    return rows,{'peak_row_l1':str(Fraction(peak,unit)),'denominator_depth':depth},trace


def macro_replay(raw):
    rows=[[Fraction(i==j)for j in range(9)]for i in range(9)]
    for op in raw:
        if op[0]=='add':
            _,d,s,a,b,_=op;c=Fraction(a,b)
            rows[d]=[x+c*y for x,y in zip(rows[d],rows[s])]
        else:
            _,d,a,b,_=op;c=Fraction(a,b);rows[d]=[c*x for x in rows[d]]
    rows[8]=[Fraction(0)]*9
    return rows


def check(stream,raw):
    rows,summary,trace=primitive_replay(stream)
    expected=macro_replay(raw)
    require(all(Fraction(x,1<<64)==y for row,oracle in zip(rows,expected)for x,y in zip(row,oracle)),
            'primitive boundary mismatch, including dirty work')
    return summary


def check_orientations(words):
    forward=[row[:8]for row in macro_replay(words['forward'])[:8]]
    aug=[row+[Fraction(i==j)for j in range(8)]for i,row in enumerate(forward)]
    for col in range(8):
        pivot=next(r for r in range(col,8)if aug[r][col])
        aug[col],aug[pivot]=aug[pivot],aug[col]
        q=aug[col][col];aug[col]=[x/q for x in aug[col]]
        for r in range(8):
            if r!=col:
                q=aug[r][col];aug[r]=[x-q*y for x,y in zip(aug[r],aug[col])]
    inverse=[r[8:]for r in aug]
    expected={'forward':forward,'inverse':inverse,
              'inverse_transpose':[list(r)for r in zip(*inverse)],
              'transpose':[list(r)for r in zip(*forward)]}
    for name,word in words.items():
        require([r[:8]for r in macro_replay(word)[:8]]==expected[name],'orientation identity')
