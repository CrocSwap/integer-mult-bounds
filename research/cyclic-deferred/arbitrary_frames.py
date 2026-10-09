"""Arbitrary binary physical frames under icekylinx PR130's Clifford theorem.

The PR117 DAG and PR124 compensated reuse remain unchanged. Only common
mixer frames move, with sources, roots, gauges and reuse handoffs fixed.
Prepared for eumemic with OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict
from functools import lru_cache
from reuse import basis, complement, contained

# r^(1-1/3000), rounded to integer multiples of 10^-40 with 90-digit
# Decimal precision. These frozen integers choose the search path only;
# the complete histogram and characteristic moment are certified exactly.
WEIGHTS = (0, 10000000000000000000000000000000000000000, 19995379552591837382775889827050449904979, 29989015888449392928645236540478701956455, 39981520345220774690768272038046978013735, 49973183228757330836823088833072358339525, 59964175509825272502769082288517196077212, 69954610152207694202574952004534640790419, 79944567439236201753790348429080145493684, 89934107395767013189839565186018423885624, 99923276611021966935579916938258879056401, 109912112302259010906160819839182212710832, 119900644887718846958874586969063870269385, 129888899695720170457234823823425114507787, 139876898144698708970082643468833997994746, 149864658584359632812685622102969862143699, 159852196911530273460627424580342355718650, 169839527031456604018724816697495391901760, 179826661210191807363562888188255624208623, 189813610348441151070503826377433151796525, 199800384197600682599437329947280431748835, 209786991532483974684540213818179734824257, 219773440291076756696113170334150098302772, 229759737688831192394197057459135847609982, 239745890313046845226998719817503395211757)

@lru_cache(None)
def cap(A,B,h):
    return complement(basis(complement(A,h)+complement(B,h)),h)

@lru_cache(None)
def general_frame(F,h):
    """Check the actual arbitrary-subspace L_U, including its radical."""
    assert F==basis(F), 'Noncanonical generalized frame'
    Q=complement(F,h)
    L=basis(tuple(x|(x<<h)for x in F)+tuple(y<<h for y in Q))
    assert len(L)==h, 'General frame Lagrangian dimension'
    mask=(1<<h)-1
    assert all((((((x&mask)&(y>>h)).bit_count()+((x>>h)&(y&mask)).bit_count())&1)==0)for x in L for y in L), 'General frame symplectic pairing'
    return True

def optimize(data):
    ops=data['ops'];h=data['h'];R=data['R'];FULL=basis(1<<i for i in range(h))
    frames={i:basis(F)for i,F in data['op_frames'].items()};original=frames.copy()
    sigma={s:basis(F)for s,F in data['placed'].items()};events=defaultdict(list);first={};frozen=set()
    for i,o in enumerate(ops):
        ss=o[1:2]if o[0]=='src'else o[1:3]
        for s in ss:events[s].append(i);first.setdefault(s,i)
        if o[0]=='src':frozen.add(i)
    for row in data['reuse_pairs']:
        frozen.update((data['last'][row['donor']],first[row['recipient']]))
    prev={};after={};end={s:basis(data['root_frame'].get(s,FULL))for s in range(R)}
    for s,es in events.items():
        for j,i in enumerate(es):
            prev[i,s]=es[j-1]if j else None
            after[i,s]=es[j+1]if j+1<len(es)else None
    passes=[]
    for turn in range(20):
        changes=0
        for i in (reversed(range(len(ops)))if turn%2==0 else range(len(ops))):
            if i in frozen:continue
            a,b=ops[i][1:3];old=frames[i]
            starts=[frames[prev[i,s]]if prev[i,s]is not None else sigma.get(s,())for s in(a,b)]
            ends=[frames[after[i,s]]if after[i,s]is not None else end[s]for s in(a,b)]
            low=basis(starts[0]+starts[1]);high=cap(*ends,h)
            assert contained(low,old)and contained(old,high)
            def cost(d):return sum(WEIGHTS[d-len(P)]+WEIGHTS[len(N)-d]for P,N in zip(starts,ends))
            winner=min((low,high,old),key=lambda C:cost(len(C)))
            if cost(len(winner))<cost(len(old)):
                frames[i]=winner;changes+=1
        passes.append(changes)
        print('Arbitrary physical-frame descent',turn,changes,flush=True)
        if not changes:break
    assert passes[-1]==0, 'Arbitrary-frame descent did not reach its checked fixed point'
    steps=0
    for s,es in events.items():
        seq=[sigma.get(s,())]+[frames[i]for i in es]+[end[s],FULL]
        assert all(contained(A,B)for A,B in zip(seq,seq[1:])), 'Arbitrary physical chain inclusion'
        steps+=len(seq)-1
    assert all(frames[i]==original[i]for i in frozen), 'Changed frozen source or reuse handoff'
    assert all(general_frame(F,h)for F in set(frames.values()))
    return frames,dict(passes=passes,changed_gates=sum(frames[i]!=original[i]for i in frames),checked_chain_steps=steps,frozen_gates=len(frozen),source_root_gauge_and_reuse_handoffs_fixed=True)
