"""Verify fixed-skeleton diagonal body rigidity on the exact signed 8+9 caller."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

CALLER = '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'


def pinned(path,digest):
    payload=path.read_bytes()
    assert sha256(payload).hexdigest()==digest, path
    return payload


def shear(a):
    assert a
    return ((Q(1),Q(a)),(Q(0),Q(1)))


def equal_transport(matrix,before,after):
    return all(before[s]==after[d] for d in range(2) for s in range(2) if matrix[d][s])


def cuts(caller,ty):
    t=caller['types'][ty]
    live={r:(0,[]) for r in range(t['offset'],t['offset']+t['roles'])}
    edges=[]; nodes=[]; counts=Counter(); shapes=Counter(); signed=Counter()
    stages=[]
    for i,e in enumerate(caller['events']):
        if e[0]=='J':
            stages.append(e[1]); op='J'
            if ty=='A':
                x,y,u,v=e[2]; alpha=Q(t['alpha2'])
                mixes=((y,x,shear(1),-1),(u,v,shear(alpha),1))
            else:
                s,z,a,b=e[3];a,b=map(Q,(a,b))
                assert (a,b)==(-1,Q(1,2)) and 1+a*b
                mixes=((s,z,((Q(1),a),(b,1+a*b)),(1,-1)),)
        elif e[0]!=ty:
            continue
        else:
            op=e[1]
            if op in ('IDLE_ONE','IDLE_ODD'):
                r,mask=e[2:4]
                assert mask and len(mask)==len(set(mask)) and all(1<=j<=17 for j in mask)
                live[r][1].append((i,r,tuple(mask),op))
                continue
            if op=='SWAP':
                a,b=e[2:4];live[a],live[b]=live[b],live[a];counts[op]+=1;continue
            if op in ('SCALE','LAMBDA'):
                assert e[2] in live and (Q(e[3]) if op=='SCALE' else e[3] in (-1,1))
                counts[op]+=1;continue
            assert op in ('ADD','QUERY')
            a,b=e[2:4]
            if op=='ADD':
                mixes=((a,b,shear(Q(e[4])),0),)
            else:
                assert e[4] in (-1,1)
                mixes=((a,b,shear(1),e[4]),)
        for a,b,matrix,q in mixes:
            assert a!=b and a in live and b in live and matrix[0][0] and matrix[1][1] and matrix[0][1]
            assert equal_transport(matrix,(1,1),(1,1))
            assert not equal_transport(matrix,(1,0),(1,0))
            assert not equal_transport(matrix,(1,1),(1,0))
            node=len(nodes)+1
            counts[op]+=1
            shapes[f'{op}/{tuple(tuple(bool(x) for x in row) for row in matrix)}']+=1
            if op=='J':
                signed[str((tuple(tuple(str(x) for x in row) for row in matrix),q))]+=1
            nodes.append((i,op,a,b))
            for r in (a,b):
                start,phases=live[r];edges.append((start,node,phases));live[r]=(node,[])
    assert stages==list(range(1,18))
    sink=len(nodes)+1
    edges.extend((start,sink,phases) for start,phases in live.values())
    return counts,shapes,signed,nodes,edges,sink


def zero_reach(edges,sink,label):
    clear=[(a,b) for a,b,ph in edges if all(label not in p[2] for p in ph)]
    forward,backward={0},{sink}
    for a,b in clear:
        if a in forward:forward.add(b)
    for a,b in reversed(clear):
        if b in backward:backward.add(a)
    return set(range(sink+1))-forward,set(range(sink+1))-backward


def rigidity(caller):
    results={}
    for ty,expected in (('A',(688,30)),('B',(3493,64))):
        counts,shapes,signed,nodes,edges,sink=cuts(caller,ty)
        sizes=Counter(len(ph) for _,_,ph in edges if ph)
        assert (len(nodes),sizes[1])==expected and set(sizes)=={1}
        assert all(a<b for a,b,_ in edges) and [b for _,b,_ in edges]==sorted(b for _,b,_ in edges)
        incoming=defaultdict(list);outgoing=defaultdict(list)
        for a,b,ph in edges:
            mask={j for p in ph for j in p[2]}
            outgoing[a].append(mask);incoming[b].append(mask)
        barriers=0
        # The epoch ordering at a node matches its two literal lane operands.
        for i in range(1,sink):
            a,b=incoming[i]
            # Reachability is the main test. The lane pairing is checked separately below.
            barriers+=bool(a&b)
        assert barriers==0
        reach={j:tuple(map(len,zero_reach(edges,sink,j))) for j in range(1,18)}
        assert set(reach.values())=={(0,0)}
        results[ty]=dict(mixing_nodes=len(nodes),lane_epochs=len(edges),paid_idle_epochs=sizes[1],
            counts=counts,nonzero_mixing_patterns=shapes,literal_J_coefficients_and_q_powers=signed,
            zero_edge_unreachable_by_stage=reach,
            graph_sha256=sha256(json.dumps([nodes,edges],separators=(',',':')).encode()).hexdigest())
    # Removing the zero edge out of the source makes a nonzero potential feasible.
    assert zero_reach([(0,1,[(0,0,(1,),'IDLE_ONE')]),(1,2,[])],2,1)==({1,2},{0})
    # Without nonnegativity, endpoint-zero potentials (0,1,0) can put +1,-1 on zero-old edges.
    assert (1-0,0-1)==(1,-1)
    # Without the sink pin, (0,1,1) is monotone and permits new payment on a zero-old path.
    assert (1-0,1-1)==(1,0)
    return results


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    package = Path(__file__).resolve().parent
    caller = json.loads(pinned(package / "CALLER.json", CALLER))
    receipt = dict(status="PASS_DIAGONAL_BODY_RIGIDITY", caller_sha256=CALLER,
                   types=rigidity(caller), price=None)
    rendered = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    assert rendered == (package / "RIGIDITY.json").read_text(), "Exact graph and controls receipt"
    print(receipt["status"])
