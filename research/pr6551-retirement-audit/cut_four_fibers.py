"""Independent exact cut check in all four fibers of q^4 - 1.

No source or lead replay routines are imported. Gaussian rational arithmetic and
formal commuting stage monomials are implemented here. Apache-2.0; prepared for
DLamdata with substantial OpenAI Codex assistance.
"""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json
import sys

Z = (F(0), F(0))
O = (F(1), F(0))
I = (F(0), F(1))
MON = (0,)*19


def need(ok, label):
    if not ok:
        raise ValueError(label)


def plus(a, b):
    return a[0]+b[0], a[1]+b[1]


def times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def power(a, n):
    out=O
    for _ in range(n%4):
        out=times(out,a)
    return out


def add_poly(a, b, scalar=O):
    result=dict(a)
    for mon, value in b.items():
        value=plus(result.get(mon,Z),times(value,scalar))
        if value==Z:
            result.pop(mon,None)
        else:
            result[mon]=value
    return result


def scale(a, b):
    return {mon:times(value,b) for mon,value in a.items() if times(value,b)!=Z}


def stage(a, labels):
    labels=set(labels)
    return {tuple(x+int(i in labels) for i,x in enumerate(mon)):value for mon,value in a.items()}


def replay_vector(events, q, reverse=False, target=4):
    state=[{} for _ in range(35)]
    state[target]={MON:O}
    for e in (reversed(events) if reverse else events):
        op=e[0]
        if op in ('SCALE','Q_POWER','LAMBDA'):
            r=e[1]
            if op=='SCALE':
                c=(F(e[2]),F(0))
            elif op=='Q_POWER':
                c=power(q,e[2])
            else:
                c=plus((F(1,2),F(e[2],2)), times((F(1,2),F(-e[2],2)),power(q,2)))
            state[r]=scale(state[r],c)
        elif op=='SWAP':
            a,b=e[1:]
            state[a],state[b]=state[b],state[a]
        elif op in ('ADD','QUERY'):
            dst,src=e[1:3]
            c=(F(e[3]),F(0)) if op=='ADD' else power(q,e[3])
            if reverse:
                src,dst=dst,src
            state[dst]=add_poly(state[dst],state[src],c)
        elif op=='LOCAL':
            j,src,dst=e[1:]
            if reverse:
                state[src]=stage(state[src], [j])
                state[dst]=stage(state[dst], [j])
                state[src]=add_poly(state[src],state[dst],power(q,-1))
            else:
                state[dst]=add_poly(state[dst],state[src],power(q,-1))
                state[src]=stage(state[src],[j])
                state[dst]=stage(state[dst],[j])
        elif op in ('IDLE','IDLE_ONE'):
            roles,labels=(e[1:3],e[3]) if op=='IDLE' else ([e[1]],e[2])
            for r in roles:
                state[r]=stage(state[r],labels)
        else:
            raise ValueError('unknown opcode '+op)
    return state


def slots(e):
    return {'ADD':(1,2),'SWAP':(1,2),'SCALE':(1,),'LAMBDA':(1,),
            'Q_POWER':(1,),'QUERY':(1,2),'LOCAL':(2,3),'IDLE':(1,2),'IDLE_ONE':(1,)}[e[0]]


def audit(word):
    events=word['events']
    need(word['roles']==35 and word['stages']==18,'dimensions')
    prefix=events[:345]
    need(prefix[-1]==['ADD',4,21,'1'],'cut marker')
    need(all(e[i]!=34 for e in prefix for i in slots(e)),'fresh input used before handoff')
    need(all(e[i]!=4 for e in events[345:-3] for i in slots(e)), 'retired input reused after handoff')
    need(events[-3:]==[['LAMBDA',4,-1],['LAMBDA',20,-1],['LAMBDA',21,-1]],'final normalization')
    totals=[]
    for q in [O,(-F(1),F(0)),I,(F(0),-F(1))]:
        lam=plus((F(1,2),F(1,2)),times((F(1,2),-F(1,2)),power(q,2)))
        s=times(lam,power(q,-1))
        expected=[{} for _ in range(35)]
        expected[4]={MON:s}
        for reverse in [False,True]:
            got=replay_vector(prefix,q,reverse)
            need(got==expected,'pivot column' if not reverse else 'pivot row')
        totals.append({'q':[str(v) for v in q], 'pivot_scalar':[str(v) for v in s], 'row_coefficients':35,'column_coefficients':35})
    return totals


def reject(label,word):
    try:
        audit(word)
    except ValueError as exc:
        return {'control':label,'rejected_by':str(exc)}
    raise ValueError('accepted mutant: '+label)


def main():
    old,new=map(Path,sys.argv[1:3])
    a=json.loads(old.read_text());b=json.loads(new.read_text())
    need(a['events'][:345]==b['events'][:345],'literal prefix unchanged')
    results={'old':audit(a),'new':audit(b)}
    controls=[]
    bad=deepcopy(b);bad['events'][340][-1]='-1'
    controls.append(reject('changed_middle_add_sign',bad))
    bad=deepcopy(b);bad['events'][0][-1]='1'
    controls.append(reject('changed_input_basis_sign',bad))
    bad=deepcopy(b);bad['events'][0][2]=34
    controls.append(reject('fresh_input_read_before_handoff',bad))
    bad=deepcopy(b);bad['events'].insert(345,['ADD',0,4,'1'])
    controls.append(reject('retired_input_reused_after_handoff',bad))
    # A true external cancellation keeps the prefix operator identical.
    positive=deepcopy(b);positive['events'][5:5]=[['ADD',1,2,'1'],['ADD',1,2,'-1']]
    for q in [O,(-F(1),F(0)),I,(F(0),-F(1))]:
        for rev in [False,True]:
            need(replay_vector(positive['events'][:347],q,rev)==replay_vector(b['events'][:345],q,rev),'cancelling ADD pair')
    results.update(status='PASS_FOUR_FIBER_RETIREMENT_CUT',literal_shared_events=345,raw_shared_prefix_events=329,controls=controls,positive_control='cancelling ADD pair at cut input')
    print(json.dumps(results,indent=2,sort_keys=True))

if __name__=='__main__':main()
